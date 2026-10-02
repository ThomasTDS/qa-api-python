from typing import Any

import pytest
from pydantic import ValidationError
from pytest_bdd import scenarios, then, when

from conftest import Context
from models.booking import CreateBookingResponse
from steps.booking_data import booking_payload, default_booking

scenarios("../features/create_booking.feature")


# Envia um payload cru e, se a API criou o booking mesmo assim, guarda o id
# para a limpeza no fim do teste. Só registra quando a resposta é 200: com
# erro, a API não devolve JSON nem cria nada.
def _create_raw(context: Context, payload: dict[str, Any]) -> None:
    context.last_response = context.booking_client.create_booking_raw(payload)
    if context.last_response.status_code == 200:
        context.booking_id = context.last_response.json().get("bookingid")


@when("o usuário cria um booking com dados válidos")
def cria_um_booking_com_dados_validos(context: Context) -> None:
    context.booking_data = default_booking()
    context.last_response = context.booking_client.create_booking(context.booking_data)


@then("o booking deve ser criado com sucesso")
def booking_deve_ser_criado_com_sucesso(context: Context) -> None:
    assert context.response.status_code == 200


@then("o id do booking criado deve ser retornado")
def id_do_booking_criado_deve_ser_retornado(context: Context) -> None:
    body = CreateBookingResponse.model_validate_json(context.response.text)
    assert body.bookingid > 0
    context.booking_id = body.bookingid


@when("o usuário tenta criar um booking sem informar o firstname")
def tenta_criar_booking_sem_firstname(context: Context) -> None:
    _create_raw(context, booking_payload(without="firstname"))


@then("a resposta deve indicar um erro interno do servidor")
def resposta_indica_erro_interno_do_servidor(context: Context) -> None:
    assert context.response.status_code == 500


@when("o usuário cria um booking com totalprice em formato inválido")
def cria_booking_com_totalprice_invalido(context: Context) -> None:
    _create_raw(context, booking_payload(totalprice="nao-e-numero"))


@then("a resposta da API não deve corresponder ao schema esperado")
def resposta_nao_corresponde_ao_schema(context: Context) -> None:
    assert context.response.status_code == 200
    with pytest.raises(ValidationError):
        CreateBookingResponse.model_validate_json(context.response.text)


@when("o usuário cria um booking com depositpaid em formato inválido")
def cria_booking_com_depositpaid_invalido(context: Context) -> None:
    _create_raw(context, booking_payload(depositpaid="sim"))


@then("o depositpaid do booking criado deve ser true")
def depositpaid_do_booking_criado_deve_ser_true(context: Context) -> None:
    assert context.response.json()["booking"]["depositpaid"] is True


@when("o usuário cria um booking com checkin em formato inválido")
def cria_booking_com_checkin_invalido(context: Context) -> None:
    _create_raw(context, booking_payload(bookingdates={"checkin": "data-invalida", "checkout": "2026-01-05"}))


@then("o checkin do booking criado deve estar corrompido")
def checkin_do_booking_criado_deve_estar_corrompido(context: Context) -> None:
    checkin = context.response.json()["booking"]["bookingdates"]["checkin"]
    assert checkin != "data-invalida"
    assert "NaN" in checkin


@when("o usuário cria um booking com totalprice negativo")
def cria_booking_com_totalprice_negativo(context: Context) -> None:
    _create_raw(context, booking_payload(totalprice=-150))


@then("o totalprice do booking criado deve ser negativo")
def totalprice_do_booking_criado_deve_ser_negativo(context: Context) -> None:
    assert context.response.json()["booking"]["totalprice"] < 0
