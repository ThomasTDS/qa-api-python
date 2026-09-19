from typing import Any

import pytest
from pydantic import ValidationError

from models.booking import AuthResponse, Booking, BookingDates, BookingId, CreateBookingResponse


def _valid_booking_payload() -> dict[str, Any]:
    return {
        "firstname": "Jim",
        "lastname": "Brown",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {"checkin": "2024-01-01", "checkout": "2024-01-02"},
        "additionalneeds": "Breakfast",
    }


def test_booking_accepts_a_full_valid_payload() -> None:
    booking = Booking.model_validate(_valid_booking_payload())

    assert booking.firstname == "Jim"
    assert booking.bookingdates == BookingDates(checkin="2024-01-01", checkout="2024-01-02")


def test_booking_additionalneeds_defaults_to_none_when_omitted() -> None:
    payload = _valid_booking_payload()
    del payload["additionalneeds"]

    booking = Booking.model_validate(payload)

    assert booking.additionalneeds is None


def test_booking_rejects_a_missing_required_field() -> None:
    payload = _valid_booking_payload()
    del payload["totalprice"]

    with pytest.raises(ValidationError):
        Booking.model_validate(payload)


def test_booking_rejects_incomplete_bookingdates() -> None:
    payload = _valid_booking_payload()
    del payload["bookingdates"]["checkout"]

    with pytest.raises(ValidationError):
        Booking.model_validate(payload)


def test_booking_id_rejects_a_non_numeric_id() -> None:
    with pytest.raises(ValidationError):
        BookingId.model_validate({"bookingid": "not-a-number"})


def test_create_booking_response_nests_the_booking_model() -> None:
    payload = {"bookingid": 1, "booking": _valid_booking_payload()}

    response = CreateBookingResponse.model_validate(payload)

    assert response.bookingid == 1
    assert isinstance(response.booking, Booking)


def test_auth_response_requires_a_token() -> None:
    with pytest.raises(ValidationError):
        AuthResponse.model_validate({})
