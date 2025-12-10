import os
import sys
import requests
from config.loader import Config
from utils.logger import Logger as log


class ApiClient:

    def __init__(self):
        cfg = Config()
        self.cfg = cfg

        if cfg.debug:
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

    def _request(self, method, endpoint, **kwargs):
        endpoint = endpoint.strip("/")
        url = f"{self.base_url}/{endpoint}"
        url = url.replace("://", "§§").replace("//", "/").replace("§§", "://")

        if self.cfg.debug:
            log.debug("ApiClient", f"Request {method} {url}")
            curl_parts = ["curl", "-X", method]
            for k, v in self.headers.items():
                curl_parts.append(f"-H '{k}: {v}'")
            if "json" in kwargs:
                import json as _json
                curl_parts.append(f"-d '{_json.dumps(kwargs.get('json'))}'")
            curl_parts.append(f"'{url}'")
            log.debug("ApiClient", f"[CURL]: {' '.join(curl_parts)}")

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                verify=self.verify,
                allow_redirects=False,
                **kwargs
            )
        except requests.ConnectionError as e:
            log.error("ApiClient", f"Connection refused when calling {url}: {e}")
            sys.exit(1)
        except requests.Timeout as e:
            log.error("ApiClient", f"Request timeout when calling {url}: {e}")
            sys.exit(1)
        except requests.RequestException as e:
            log.error("ApiClient", f"Unexpected request error: {e}")
            sys.exit(1)

        if response.status_code in (301, 308) and "Location" in response.headers:
            redirect_url = response.headers["Location"]
            response = requests.request(
                method=method,
                url=redirect_url,
                headers=self.headers,
                verify=self.verify,
            )

        # Raise HTTP errors (4xx, 5xx)
        if response.status_code == 404 and method == "GET":
            return None

        try:
            response.raise_for_status()
        except requests.HTTPError:
            log.error("ApiClient", f"HTTP {response.status_code} on {method} {url} body={response.text}")
            sys.exit(1)

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