import os
from typing import Any, Dict, Optional

import requests

from config.loader import Config
from utils.logger import Logger as log

# Sensitive headers that should be masked in logs
SENSITIVE_HEADERS = {"authorization", "x-api-key", "cookie", "set-cookie"}
DEFAULT_TIMEOUT = 30  # seconds


class ApiClient:
    """HTTP client with connection pooling, security features, and timeout support."""

    _session: Optional[requests.Session] = None

    def __init__(self):
        cfg = Config()
        self.cfg = cfg
        self.timeout = int(os.getenv("API_TIMEOUT", DEFAULT_TIMEOUT))

        log.debug("ApiClient", f"base_url={cfg.base_url}")
        log.debug("ApiClient", f"auth_type={cfg.auth_type}")

        self.base_url = cfg.base_url.rstrip("/")
        self.headers = {
            "Content-Type": "application/json"
        }
        if cfg.auth_type.lower() == "bearer":
            self.headers["Authorization"] = f"Bearer {cfg.token}"
        elif cfg.auth_type.lower() == "basic":
            self.headers["Authorization"] = f"Basic {cfg.token}"
        elif cfg.auth_type.lower() == "apikey":
            self.headers["X-API-Key"] = cfg.token

        self.headers = {k: v for k, v in self.headers.items() if v}
        self.headers["X-Requested-With"] = "XMLHttpRequest"

        disable_verify = os.getenv("DISABLE_TLS_VERIFY", "false").lower() == "true"
        self.verify = False if disable_verify else os.getenv("CA_BUNDLE", "/etc/ssl/certs/custom-ca.pem")

        if disable_verify:
            log.debug("ApiClient", "WARNING: TLS verification is disabled")

    @property
    def session(self) -> requests.Session:
        """Get or create a session for connection pooling."""
        if ApiClient._session is None:
            ApiClient._session = requests.Session()
        return ApiClient._session

    def _mask_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Mask sensitive header values for safe logging."""
        masked = {}
        for key, value in headers.items():
            if key.lower() in SENSITIVE_HEADERS:
                masked[key] = "***REDACTED***"
            else:
                masked[key] = value
        return masked

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        endpoint = endpoint.strip("/")
        url = f"{self.base_url}/{endpoint}"
        safe_headers = self._mask_sensitive_headers(self.headers)

        log.debug("ApiClient", f"Calling {method} {url}")
        log.debug("ApiClient", f"Headers: {safe_headers}")
        log.debug("ApiClient", f"Verify: {self.verify}")
        log.debug("ApiClient", f"Timeout: {self.timeout}s")

        # Build CURL command with masked sensitive data for debugging
        curl_parts = ["curl", "-X", method]
        for k, v in safe_headers.items():
            curl_parts.append(f"-H '{k}: {v}'")
        if "json" in kwargs:
            import json as _json
            curl_parts.append(f"-d '{_json.dumps(kwargs.get('json'))}'")
        curl_parts.append(f"'{url}'")
        log.debug("ApiClient", f"[CURL]: {' '.join(curl_parts)}")

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=self.headers,
                verify=self.verify,
                allow_redirects=False,
                timeout=self.timeout,
                **kwargs
            )
        except requests.ConnectionError as e:
            log.error("ApiClient", f"Connection refused when calling {url}: {e}")
            raise e
        except requests.Timeout as e:
            log.error("ApiClient", f"Request timeout when calling {url}: {e}")
            raise e
        except requests.RequestException as e:
            log.error("ApiClient", f"Unexpected request error: {e}")
            raise e

        if response.status_code in (301, 308) and "Location" in response.headers:
            redirect_url = response.headers["Location"]
            log.debug("ApiClient", f"Following redirect to: {redirect_url}")
            response = self.session.request(
                method=method,
                url=redirect_url,
                headers=self.headers,
                verify=self.verify,
                timeout=self.timeout,
            )

        # Raise HTTP errors (4xx, 5xx)
        if response.status_code == 404 and method == "GET":
            return None

        try:
            response.raise_for_status()
        except requests.HTTPError:
            log.error("ApiClient", f"HTTP {response.status_code} on {method} {url} body={response.text}")
            raise

        if not response.text or not response.text.strip():
            return {}

        try:
            return response.json()
        except ValueError:
            log.debug("ApiClient", "Non-JSON response received")
            return {
                "warning": "Non-JSON response",
                "status": response.status_code,
                "raw": response.text
            }

    def get(self, endpoint, **kwargs):
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        return self._request("PUT", endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self._request("DELETE", endpoint, **kwargs)
