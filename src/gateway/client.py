import requests
import os

from config.loader import Config


class ApiClient:
    def __init__(self):
        cfg = Config()
        self.base_url = cfg.base_url.rstrip('/')
        self.headers = {'Content-Type': 'application/json'}
        if cfg.token:
            self.headers['Authorization'] = f'Bearer {cfg.token}'

    def request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        disable_verify = os.getenv("DISABLE_TLS_VERIFY", "false").lower() == "true"
        verify_path = False if disable_verify else os.getenv("CA_BUNDLE", "/etc/ssl/certs/custom-ca.pem")

        response = requests.request(
            method,
            url,
            headers=self.headers,
            verify=verify_path,
            **kwargs
        )

        response.raise_for_status()

        if not response.text or response.text.strip() == "":
            return {}

        try:
            return response.json()
        except ValueError:
            print("WARN: Response is not valid JSON.")
            print("STATUS:", response.status_code)
            print("RAW:", response.text)
            return {"raw": response.text}


    def get(self, endpoint, **kwargs):
        return self.request('GET', endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self.request('POST', endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        return self.request('PUT', endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.request('DELETE', endpoint, **kwargs)
