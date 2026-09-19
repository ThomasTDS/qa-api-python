import requests

from models.booking import AuthResponse


class AuthApiClient:
    def __init__(self, session: requests.Session, base_url: str) -> None:
        self.session = session
        self.base_url = base_url

    def create_token(self, username: str, password: str) -> requests.Response:
        return self.session.post(f"{self.base_url}/auth", json={"username": username, "password": password})

    def get_valid_token(self) -> str:
        response = self.create_token("admin", "password123")
        body = AuthResponse.model_validate(response.json())
        return body.token
