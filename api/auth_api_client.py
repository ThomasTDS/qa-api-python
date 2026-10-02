import requests

from api.base_api_client import DEFAULT_TIMEOUT, BaseApiClient
from models.booking import AuthResponse


class AuthApiClient(BaseApiClient):
    def __init__(
        self,
        session: requests.Session,
        base_url: str,
        username: str,
        password: str,
        timeout: tuple[float, float] = DEFAULT_TIMEOUT,
    ) -> None:
        super().__init__(session, base_url, timeout)
        self.username = username
        self.password = password

    def create_token(self, username: str, password: str) -> requests.Response:
        return self._request("POST", "/auth", json={"username": username, "password": password})

    # Token com as credenciais configuradas no client, usado pelos cenários
    # que só precisam estar autenticados e pela limpeza ao fim de cada teste.
    def get_valid_token(self) -> str:
        response = self.create_token(self.username, self.password)
        body = AuthResponse.model_validate_json(response.text)
        return body.token
