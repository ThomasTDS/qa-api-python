import requests

from api.base_api_client import BaseApiClient


class HealthApiClient(BaseApiClient):
    def ping(self) -> requests.Response:
        return self._request("GET", "/ping")
