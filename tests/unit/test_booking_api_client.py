import requests
from requests_mock import Mocker

from api.booking_api_client import BookingApiClient
from models.booking import Booking, BookingDates

BASE_URL = "https://example.test"


def _booking() -> Booking:
    return Booking(
        firstname="Jim",
        lastname="Brown",
        totalprice=111,
        depositpaid=True,
        bookingdates=BookingDates(checkin="2024-01-01", checkout="2024-01-02"),
        additionalneeds="Breakfast",
    )


def test_get_booking_ids_sends_no_params_when_no_filter_is_given(requests_mock: Mocker) -> None:
    requests_mock.get(f"{BASE_URL}/booking", json=[])
    client = BookingApiClient(requests.Session(), BASE_URL)

    client.get_booking_ids()

    assert requests_mock.last_request is not None
    assert requests_mock.last_request.qs == {}


def test_get_booking_ids_sends_only_the_filters_that_were_given(requests_mock: Mocker) -> None:
    requests_mock.get(f"{BASE_URL}/booking", json=[])
    client = BookingApiClient(requests.Session(), BASE_URL)

    client.get_booking_ids(firstname="Jim", checkin="2024-01-01")

    assert requests_mock.last_request is not None
    assert requests_mock.last_request.qs == {"firstname": ["jim"], "checkin": ["2024-01-01"]}


def test_get_booking_hits_the_booking_by_id_endpoint(requests_mock: Mocker) -> None:
    requests_mock.get(f"{BASE_URL}/booking/1", json={"firstname": "Jim"})
    client = BookingApiClient(requests.Session(), BASE_URL)

    client.get_booking(1)

    assert requests_mock.last_request is not None
    assert requests_mock.last_request.url == f"{BASE_URL}/booking/1"


def test_create_booking_sends_the_booking_payload_and_no_auth_cookie(requests_mock: Mocker) -> None:
    requests_mock.post(f"{BASE_URL}/booking", json={"bookingid": 1, "booking": {}})
    client = BookingApiClient(requests.Session(), BASE_URL)
    booking = _booking()

    client.create_booking(booking)

    assert requests_mock.last_request is not None
    assert requests_mock.last_request.json() == booking.model_dump(exclude_none=True)
    assert "Cookie" not in requests_mock.last_request.headers


def test_update_booking_sends_the_full_payload_with_the_auth_token_as_cookie(requests_mock: Mocker) -> None:
    requests_mock.put(f"{BASE_URL}/booking/1", json={})
    client = BookingApiClient(requests.Session(), BASE_URL)
    booking = _booking()

    client.update_booking(1, booking, token="tok123")

    assert requests_mock.last_request is not None
    assert requests_mock.last_request.json() == booking.model_dump(exclude_none=True)
    assert requests_mock.last_request.headers["Cookie"] == "token=tok123"


def test_update_booking_raw_sends_the_payload_as_is_with_the_auth_token_as_cookie(requests_mock: Mocker) -> None:
    requests_mock.put(f"{BASE_URL}/booking/1", json={})
    client = BookingApiClient(requests.Session(), BASE_URL)
    payload = {"firstname": "Jane", "totalprice": "nao-e-numero"}

    client.update_booking_raw(1, payload, token="tok123")

    assert requests_mock.last_request is not None
    assert requests_mock.last_request.json() == payload
    assert requests_mock.last_request.headers["Cookie"] == "token=tok123"


def test_partial_update_booking_sends_only_the_given_fields(requests_mock: Mocker) -> None:
    requests_mock.patch(f"{BASE_URL}/booking/1", json={})
    client = BookingApiClient(requests.Session(), BASE_URL)

    client.partial_update_booking(1, {"firstname": "Jane"}, token="tok123")

    assert requests_mock.last_request is not None
    assert requests_mock.last_request.json() == {"firstname": "Jane"}
    assert requests_mock.last_request.headers["Cookie"] == "token=tok123"


def test_delete_booking_sends_the_auth_token_as_cookie(requests_mock: Mocker) -> None:
    requests_mock.delete(f"{BASE_URL}/booking/1")
    client = BookingApiClient(requests.Session(), BASE_URL)

    client.delete_booking(1, token="tok123")

    assert requests_mock.last_request is not None
    assert requests_mock.last_request.headers["Cookie"] == "token=tok123"
