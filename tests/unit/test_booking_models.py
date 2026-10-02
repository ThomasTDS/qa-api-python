import json
from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError

from models.booking import AuthResponse, Booking, BookingDates, BookingId, BookingIdList, CreateBookingResponse


def _valid_booking_payload() -> dict[str, Any]:
    return {
        "firstname": "Jim",
        "lastname": "Brown",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {"checkin": "2024-01-01", "checkout": "2024-01-02"},
        "additionalneeds": "Breakfast",
    }


# Os modelos validam o corpo das respostas em JSON (model_validate_json), do
# mesmo jeito que os steps fazem com o texto que vem da API.
def _validate_booking(payload: dict[str, Any]) -> Booking:
    return Booking.model_validate_json(json.dumps(payload))


def test_booking_accepts_a_full_valid_payload() -> None:
    booking = _validate_booking(_valid_booking_payload())

    assert booking.firstname == "Jim"
    assert booking.bookingdates == BookingDates(checkin=date(2024, 1, 1), checkout=date(2024, 1, 2))


def test_booking_additionalneeds_defaults_to_none_when_omitted() -> None:
    payload = _valid_booking_payload()
    del payload["additionalneeds"]

    booking = _validate_booking(payload)

    assert booking.additionalneeds is None


def test_booking_rejects_a_missing_required_field() -> None:
    payload = _valid_booking_payload()
    del payload["totalprice"]

    with pytest.raises(ValidationError):
        _validate_booking(payload)


def test_booking_rejects_incomplete_bookingdates() -> None:
    payload = _valid_booking_payload()
    del payload["bookingdates"]["checkout"]

    with pytest.raises(ValidationError):
        _validate_booking(payload)


def test_booking_rejects_a_numeric_string_as_totalprice() -> None:
    payload = {**_valid_booking_payload(), "totalprice": "111"}

    with pytest.raises(ValidationError):
        _validate_booking(payload)


def test_booking_rejects_a_string_as_depositpaid() -> None:
    payload = {**_valid_booking_payload(), "depositpaid": "true"}

    with pytest.raises(ValidationError):
        _validate_booking(payload)


def test_booking_rejects_a_corrupted_checkin_date() -> None:
    payload = _valid_booking_payload()
    payload["bookingdates"]["checkin"] = "0NaN-aN-aN"

    with pytest.raises(ValidationError):
        _validate_booking(payload)


def test_booking_ignores_fields_it_does_not_know() -> None:
    payload = {**_valid_booking_payload(), "campo_novo": "qualquer"}

    booking = _validate_booking(payload)

    assert booking.firstname == "Jim"


def test_booking_id_rejects_a_non_numeric_id() -> None:
    with pytest.raises(ValidationError):
        BookingId.model_validate_json('{"bookingid": "not-a-number"}')


def test_booking_id_list_validates_every_item() -> None:
    ids = BookingIdList.validate_json('[{"bookingid": 1}, {"bookingid": 2}]')

    assert [item.bookingid for item in ids] == [1, 2]


def test_create_booking_response_nests_the_booking_model() -> None:
    payload = {"bookingid": 1, "booking": _valid_booking_payload()}

    response = CreateBookingResponse.model_validate_json(json.dumps(payload))

    assert response.bookingid == 1
    assert isinstance(response.booking, Booking)


def test_auth_response_requires_a_token() -> None:
    with pytest.raises(ValidationError):
        AuthResponse.model_validate_json("{}")
