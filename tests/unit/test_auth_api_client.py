import requests
from requests_mock import Mocker

from api.auth_api_client import AuthApiClient

BASE_URL = "https://example.test"


def _client() -> AuthApiClient:
    return AuthApiClient(requests.Session(), BASE_URL, username="usuario", password="senha")


def test_create_token_posts_the_given_credentials(requests_mock: Mocker) -> None:
    requests_mock.post(f"{BASE_URL}/auth", json={"token": "abc123"})

    response = _client().create_token("outro-usuario", "outra-senha")

    assert response.status_code == 200
    assert requests_mock.last_request is not None
    assert requests_mock.last_request.json() == {"username": "outro-usuario", "password": "outra-senha"}


def test_get_valid_token_returns_the_token_from_the_response_body(requests_mock: Mocker) -> None:
    requests_mock.post(f"{BASE_URL}/auth", json={"token": "abc123"})

    token = _client().get_valid_token()

    assert token == "abc123"


def test_get_valid_token_authenticates_with_the_configured_credentials(requests_mock: Mocker) -> None:
    requests_mock.post(f"{BASE_URL}/auth", json={"token": "abc123"})

    _client().get_valid_token()

    assert requests_mock.last_request is not None
    assert requests_mock.last_request.json() == {"username": "usuario", "password": "senha"}
