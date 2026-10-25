import json
import math
from datetime import date
from typing import Any
from urllib.parse import parse_qs, urlsplit

import pytest
import requests
import requests_mock
from hypothesis import assume, example, given
from hypothesis import strategies as st
from pydantic import ValidationError

from api.booking_api_client import BookingApiClient
from models.booking import ISO_DATE, Booking, BookingDates, BookingIdList
from steps.booking_data import booking_payload, default_booking

# Testes de propriedade: em vez de alguns exemplos escritos à mão, o Hypothesis
# gera centenas de entradas (textos, números, datas e combinações que ninguém
# lembraria de testar) e procura uma que quebre a regra. Quando acha, reduz o
# caso ao menor exemplo possível antes de mostrar.

BASE_URL = "https://example.test"
FILTERS = ["firstname", "lastname", "checkin", "checkout"]
BOOKING_FIELDS = ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates", "additionalneeds"]

prices = st.floats(allow_nan=False, allow_infinity=False) | st.integers(min_value=-(10**9), max_value=10**9)
bookings = st.builds(
    Booking,
    firstname=st.text(),
    lastname=st.text(),
    totalprice=prices,
    depositpaid=st.booleans(),
    bookingdates=st.builds(BookingDates, checkin=st.dates(), checkout=st.dates()),
    additionalneeds=st.none() | st.text(),
)


def _payload_with(field: str, value: object) -> str:
    payload = default_booking().model_dump(mode="json")
    payload[field] = value
    return json.dumps(payload)


# MODELOS
@given(bookings)
def test_any_valid_booking_survives_a_json_round_trip(booking: Booking) -> None:
    assert Booking.model_validate_json(booking.model_dump_json()) == booking


@given(st.sampled_from([math.nan, math.inf, -math.inf]))
def test_booking_rejects_nan_and_infinity_as_totalprice(value: float) -> None:
    with pytest.raises(ValidationError):
        default_booking().model_validate({**default_booking().model_dump(), "totalprice": value})


@given(st.text())
def test_booking_rejects_any_text_as_totalprice(value: str) -> None:
    with pytest.raises(ValidationError):
        Booking.model_validate_json(_payload_with("totalprice", value))


@given(st.text() | st.integers() | st.floats(allow_nan=False, allow_infinity=False) | st.none())
def test_booking_rejects_anything_but_a_boolean_as_depositpaid(value: object) -> None:
    with pytest.raises(ValidationError):
        Booking.model_validate_json(_payload_with("depositpaid", value))


# Os dois exemplos fixos são casos que o Hypothesis encontrou: textos numéricos
# que o Pydantic aceitava como timestamp Unix à meia-noite.
@given(st.text())
@example("0")
@example("86400")
def test_booking_rejects_any_text_that_is_not_an_iso_date_as_checkin(value: str) -> None:
    assume(not ISO_DATE.fullmatch(value))
    payload = json.loads(_payload_with("additionalneeds", "x"))
    payload["bookingdates"]["checkin"] = value
    with pytest.raises(ValidationError):
        Booking.model_validate_json(json.dumps(payload))


@given(st.dates())
def test_booking_accepts_any_real_date_as_checkin(value: date) -> None:
    payload = json.loads(_payload_with("additionalneeds", "x"))
    payload["bookingdates"]["checkin"] = value.isoformat()
    assert Booking.model_validate_json(json.dumps(payload)).bookingdates.checkin == value


@given(st.lists(st.integers(min_value=1, max_value=2**31)))
def test_booking_id_list_keeps_every_id_in_order(ids: list[int]) -> None:
    body = json.dumps([{"bookingid": i} for i in ids])
    assert [item.bookingid for item in BookingIdList.validate_json(body)] == ids


# CLIENTS
# O requests_mock é usado como gerenciador de contexto, e não como fixture: o
# Hypothesis roda o teste várias vezes dentro do mesmo teste do pytest, e uma
# fixture guardaria as requisições de todas as rodadas.
@given(st.dictionaries(st.sampled_from(FILTERS), st.text(min_size=1)))
def test_get_booking_ids_sends_exactly_the_filters_that_were_given(filters: dict[str, str]) -> None:
    with requests_mock.Mocker() as mock:
        mock.get(f"{BASE_URL}/booking", json=[])
        BookingApiClient(requests.Session(), BASE_URL).get_booking_ids(**filters)
        sent = parse_qs(urlsplit(mock.last_request.url).query, keep_blank_values=True)

    assert sent == {key: [value] for key, value in filters.items()}


@given(st.sampled_from(BOOKING_FIELDS))
def test_booking_payload_without_removes_only_that_field(field: str) -> None:
    payload = booking_payload(without=field)

    assert set(payload) == set(BOOKING_FIELDS) - {field}


@given(st.dictionaries(st.sampled_from(BOOKING_FIELDS), st.text() | st.integers() | st.none()))
def test_booking_payload_overrides_only_the_given_fields(overrides: dict[str, Any]) -> None:
    payload = booking_payload(**overrides)
    reference = default_booking().model_dump(mode="json", exclude_none=True)

    for field in BOOKING_FIELDS:
        if field in overrides:
            assert payload[field] == overrides[field]
        elif field != "lastname":  # o sobrenome muda a cada booking (sufixo aleatório)
            assert payload.get(field) == reference.get(field)
