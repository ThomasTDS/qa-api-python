import requests
from requests_mock import Mocker

from api.base_api_client import DEFAULT_TIMEOUT, BaseApiClient

BASE_URL = "https://example.test"


# Os tipos do requests-mock declaram o timeout como int, mas em tempo de
# execução ele guarda o valor exatamente como foi passado (aqui, uma tupla).
def _sent_timeout(requests_mock: Mocker) -> object:
    assert requests_mock.last_request is not None
    return requests_mock.last_request.timeout


def test_request_uses_the_default_timeout_when_none_is_given(requests_mock: Mocker) -> None:
    requests_mock.get(f"{BASE_URL}/ping")
    client = BaseApiClient(requests.Session(), BASE_URL)

    client._request("GET", "/ping")

    assert _sent_timeout(requests_mock) == DEFAULT_TIMEOUT


def test_request_uses_the_timeout_given_to_the_client(requests_mock: Mocker) -> None:
    requests_mock.get(f"{BASE_URL}/ping")
    client = BaseApiClient(requests.Session(), BASE_URL, timeout=(1, 2))

    client._request("GET", "/ping")

    assert _sent_timeout(requests_mock) == (1, 2)


def test_request_joins_the_base_url_and_the_path(requests_mock: Mocker) -> None:
    requests_mock.post(f"{BASE_URL}/booking/1")
    client = BaseApiClient(requests.Session(), BASE_URL)

    client._request("POST", "/booking/1")

    assert requests_mock.last_request is not None
    assert requests_mock.last_request.url == f"{BASE_URL}/booking/1"
