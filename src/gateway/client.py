import os
import requests
from config.loader import Config


class ApiClient:

    def __init__(self):
        cfg = Config()

        self.base_url = cfg.base_url.rstrip("/")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cfg.token}" if cfg.token else None
        }
        # Entferne leere Header
        self.headers = {k: v for k, v in self.headers.items() if v}

        disable_verify = os.getenv("DISABLE_TLS_VERIFY", "false").lower() == "true"
        self.verify = False if disable_verify else os.getenv("CA_BUNDLE", "/etc/ssl/certs/custom-ca.pem")

    def _request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                verify=self.verify,
                **kwargs
            )
        except requests.RequestException as e:
            raise RuntimeError(f"API connection error: {e}")

        # Raise HTTP errors directly
        try:
            response.raise_for_status()
        except requests.HTTPError as err:
            msg = f"API error {response.status_code} on {method} {url}"
            raise RuntimeError(f"{msg}\nResponse: {response.text}") from err

        # Empty response
        if not response.text.strip():
            return {}

        # Try JSON parsing
        try:
            return response.json()
        except ValueError:
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