import requests
from requests_mock import Mocker

from api.auth_api_client import AuthApiClient
from api.base_api_client import DEFAULT_TIMEOUT

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


def test_create_token_raw_sends_the_payload_as_is(requests_mock: Mocker) -> None:
    requests_mock.post(f"{BASE_URL}/auth", json={"reason": "Bad credentials"})

    _client().create_token_raw({"username": "usuario", "password": {"$ne": None}})

    assert requests_mock.last_request is not None
    assert requests_mock.last_request.json() == {"username": "usuario", "password": {"$ne": None}}


# O AuthApiClient tem um construtor próprio, que precisa repassar o timeout à
# classe base; sem isso, as chamadas de login ficariam sem limite de tempo
# (achado pelo teste de mutação).
def _sent_timeout(requests_mock: Mocker) -> object:
    assert requests_mock.last_request is not None
    return requests_mock.last_request.timeout


def test_auth_client_uses_the_default_timeout(requests_mock: Mocker) -> None:
    requests_mock.post(f"{BASE_URL}/auth", json={"token": "abc123"})

    _client().create_token("usuario", "senha")

    assert _sent_timeout(requests_mock) == DEFAULT_TIMEOUT


def test_auth_client_uses_the_timeout_given_to_it(requests_mock: Mocker) -> None:
    requests_mock.post(f"{BASE_URL}/auth", json={"token": "abc123"})
    client = AuthApiClient(requests.Session(), BASE_URL, username="usuario", password="senha", timeout=(1, 2))

    client.create_token("usuario", "senha")

    assert _sent_timeout(requests_mock) == (1, 2)
