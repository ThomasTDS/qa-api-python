import requests
from requests_mock import Mocker

from api.auth_api_client import AuthApiClient

BASE_URL = "https://example.test"


def test_create_token_posts_the_given_credentials(requests_mock: Mocker) -> None:
    requests_mock.post(f"{BASE_URL}/auth", json={"token": "abc123"})
    client = AuthApiClient(requests.Session(), BASE_URL)

    response = client.create_token("admin", "password123")

    assert response.status_code == 200
    assert requests_mock.last_request is not None
    assert requests_mock.last_request.json() == {"username": "admin", "password": "password123"}


def test_get_valid_token_returns_the_token_from_the_response_body(requests_mock: Mocker) -> None:
    requests_mock.post(f"{BASE_URL}/auth", json={"token": "abc123"})
    client = AuthApiClient(requests.Session(), BASE_URL)

    token = client.get_valid_token()

    assert token == "abc123"


def test_get_valid_token_always_authenticates_as_admin(requests_mock: Mocker) -> None:
    requests_mock.post(f"{BASE_URL}/auth", json={"token": "abc123"})
    client = AuthApiClient(requests.Session(), BASE_URL)

    client.get_valid_token()

    assert requests_mock.last_request is not None
    assert requests_mock.last_request.json() == {"username": "admin", "password": "password123"}
