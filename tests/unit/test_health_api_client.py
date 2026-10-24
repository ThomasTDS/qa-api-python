import requests
from requests_mock import Mocker

from api.health_api_client import HealthApiClient

BASE_URL = "https://example.test"


def test_ping_hits_the_health_check_endpoint(requests_mock: Mocker) -> None:
    requests_mock.get(f"{BASE_URL}/ping", status_code=201, text="Created")
    client = HealthApiClient(requests.Session(), BASE_URL)

    response = client.ping()

    assert response.status_code == 201
    assert requests_mock.last_request is not None
    assert requests_mock.last_request.method == "GET"
