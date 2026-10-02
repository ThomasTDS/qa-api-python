import requests

from api.base_api_client import BaseApiClient
from models.booking import AuthResponse


class AuthApiClient(BaseApiClient):
    def create_token(self, username: str, password: str) -> requests.Response:
        return self._request("POST", "/auth", json={"username": username, "password": password})

    def get_valid_token(self) -> str:
        response = self.create_token("admin", "password123")
        body = AuthResponse.model_validate(response.json())
        return body.token
