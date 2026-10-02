from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError
from pytest_bdd import given, parsers, scenarios, then, when

from conftest import Context
from models.booking import AuthResponse, Booking, BookingDates, BookingIdList, CreateBookingResponse

scenarios("../features")


def _default_booking() -> Booking:
    return Booking(
        firstname="Fulano",
        lastname="Ciclano",
        totalprice=150,
        depositpaid=True,
        bookingdates=BookingDates(checkin=date(2026, 1, 1), checkout=date(2026, 1, 5)),
        additionalneeds="Breakfast",
    )


# Payload cru (sem passar pelo Pydantic) a partir do booking padrão, trocando
# só o que interessa ao cenário: um campo com valor inválido (overrides) ou um
# campo obrigatório ausente (without).
def _booking_payload(*, without: str | None = None, **overrides: Any) -> dict[str, Any]:
    payload = _default_booking().model_dump(mode="json", exclude_none=True)
    payload.update(overrides)
    if without is not None:
        del payload[without]
    return payload


# Envia um payload cru e, se a API criou o booking mesmo assim, guarda o id
# para a limpeza no fim do teste. Só registra quando a resposta é 200: com
# erro, a API não devolve JSON nem cria nada.
def _create_raw(context: Context, payload: dict[str, Any]) -> None:
    context.last_response = context.booking_client.create_booking_raw(payload)
    if context.last_response.status_code == 200:
        context.booking_id = context.last_response.json().get("bookingid")


# AUTENTICAÇÃO
@given("que ele não possui nenhum token de autenticação")
def sem_token_de_autenticacao(context: Context) -> None:
    context.token = None


@given("que ele possui um token de autenticação válido")
def com_token_de_autenticacao_valido(context: Context) -> None:
    context.token = context.auth_client.get_valid_token()


@given("que ele possui um token de autenticação inválido")
def com_token_de_autenticacao_invalido(context: Context) -> None:
    context.token = "token-invalido-qualquer"


@when("ele solicita um token com credenciais válidas")
def solicita_um_token_com_credenciais_validas(context: Context) -> None:
    client = context.auth_client
    context.last_response = client.create_token(client.username, client.password)


@when(parsers.parse('ele solicita um token com o usuário "{username}" e a senha "{password}"'))
def solicita_um_token(context: Context, username: str, password: str) -> None:
    context.last_response = context.auth_client.create_token(username, password)


@then("ele deve receber um token de autenticação válido")
def deve_receber_um_token_valido(context: Context) -> None:
    assert context.response.status_code == 200
    body = AuthResponse.model_validate_json(context.response.text)
    assert body.token


@then("a resposta deve indicar credenciais inválidas")
def resposta_indica_credenciais_invalidas(context: Context) -> None:
    assert context.response.json()["reason"] == "Bad credentials"


# CRIAÇÃO
@given("que existe um booking criado")
def existe_um_booking_criado(context: Context) -> None:
    context.booking_data = _default_booking()
    response = context.booking_client.create_booking(context.booking_data)
    body = CreateBookingResponse.model_validate_json(response.text)
    context.booking_id = body.bookingid


@when("ele cria um booking com dados válidos")
def cria_um_booking_com_dados_validos(context: Context) -> None:
    context.booking_data = _default_booking()
    context.last_response = context.booking_client.create_booking(context.booking_data)


@then("o booking deve ser criado com sucesso")
def booking_deve_ser_criado_com_sucesso(context: Context) -> None:
    assert context.response.status_code == 200


@then("o id do booking criado deve ser retornado")
def id_do_booking_criado_deve_ser_retornado(context: Context) -> None:
    body = CreateBookingResponse.model_validate_json(context.response.text)
    assert body.bookingid > 0
    context.booking_id = body.bookingid


@when("ele tenta criar um booking sem informar o firstname")
def tenta_criar_booking_sem_firstname(context: Context) -> None:
    _create_raw(context, _booking_payload(without="firstname"))


@then("a resposta deve indicar um erro interno do servidor")
def resposta_indica_erro_interno_do_servidor(context: Context) -> None:
    assert context.response.status_code == 500


@when("ele cria um booking com totalprice em formato inválido")
def cria_booking_com_totalprice_invalido(context: Context) -> None:
    _create_raw(context, _booking_payload(totalprice="nao-e-numero"))


@then("a resposta da API não deve corresponder ao schema esperado")
def resposta_nao_corresponde_ao_schema(context: Context) -> None:
    assert context.response.status_code == 200
    with pytest.raises(ValidationError):
        CreateBookingResponse.model_validate_json(context.response.text)


@when("ele cria um booking com depositpaid em formato inválido")
def cria_booking_com_depositpaid_invalido(context: Context) -> None:
    _create_raw(context, _booking_payload(depositpaid="sim"))


@then("o depositpaid do booking criado deve ser true")
def depositpaid_do_booking_criado_deve_ser_true(context: Context) -> None:
    assert context.response.json()["booking"]["depositpaid"] is True


@when("ele cria um booking com checkin em formato inválido")
def cria_booking_com_checkin_invalido(context: Context) -> None:
    _create_raw(context, _booking_payload(bookingdates={"checkin": "data-invalida", "checkout": "2026-01-05"}))


@then("o checkin do booking criado deve estar corrompido")
def checkin_do_booking_criado_deve_estar_corrompido(context: Context) -> None:
    checkin = context.response.json()["booking"]["bookingdates"]["checkin"]
    assert checkin != "data-invalida"
    assert "NaN" in checkin


@when("ele cria um booking com totalprice negativo")
def cria_booking_com_totalprice_negativo(context: Context) -> None:
    _create_raw(context, _booking_payload(totalprice=-150))


@then("o totalprice do booking criado deve ser negativo")
def totalprice_do_booking_criado_deve_ser_negativo(context: Context) -> None:
    assert context.response.json()["booking"]["totalprice"] < 0


# CONSULTA
@when("ele busca o booking pelo id")
def busca_o_booking_pelo_id(context: Context) -> None:
    assert context.booking_id is not None
    context.last_response = context.booking_client.get_booking(context.booking_id)


@when(parsers.parse('ele busca o booking pelo id "{booking_id}"'))
def busca_o_booking_pelo_id_informado(context: Context, booking_id: str) -> None:
    context.last_response = context.booking_client.get_booking(int(booking_id))


@then("os dados retornados devem corresponder ao booking criado")
def dados_correspondem_ao_booking_criado(context: Context) -> None:
    assert context.response.status_code == 200
    body = Booking.model_validate_json(context.response.text)
    assert body == context.booking_data


@then("a resposta deve indicar que o booking não foi encontrado")
def resposta_indica_booking_nao_encontrado(context: Context) -> None:
    assert context.response.status_code == 404


@when("ele busca bookings filtrando pelo firstname e lastname do booking criado")
def busca_bookings_filtrando_pelo_booking_criado(context: Context) -> None:
    assert context.booking_data is not None
    context.last_response = context.booking_client.get_booking_ids(
        firstname=context.booking_data.firstname,
        lastname=context.booking_data.lastname,
    )


@then("o id do booking criado deve estar entre os resultados")
def id_do_booking_criado_esta_entre_os_resultados(context: Context) -> None:
    assert context.response.status_code == 200
    body = BookingIdList.validate_json(context.response.text)
    assert any(b.bookingid == context.booking_id for b in body)


@when("ele busca bookings filtrando por um firstname e lastname que não correspondem a nenhum booking")
def busca_bookings_filtrando_por_dados_inexistentes(context: Context) -> None:
    context.last_response = context.booking_client.get_booking_ids(
        firstname="Inexistente-xyz-999",
        lastname="NaoExiste-abc-000",
    )


@then("o id do booking criado não deve estar entre os resultados")
def id_do_booking_criado_nao_esta_entre_os_resultados(context: Context) -> None:
    assert context.response.status_code == 200
    body = BookingIdList.validate_json(context.response.text)
    assert not any(b.bookingid == context.booking_id for b in body)


# ATUALIZAÇÃO (PUT/PATCH)
@when("ele atualiza o booking com novos dados")
def atualiza_o_booking_com_novos_dados(context: Context) -> None:
    assert context.booking_data is not None
    assert context.booking_id is not None
    updated = context.booking_data.model_copy(update={"firstname": "Atualizado", "totalprice": 200})
    context.last_response = context.booking_client.update_booking(context.booking_id, updated, context.token_or_empty)
    context.booking_data = updated


@when("ele tenta atualizar o booking com novos dados")
def tenta_atualizar_o_booking_com_novos_dados(context: Context) -> None:
    assert context.booking_data is not None
    assert context.booking_id is not None
    updated = context.booking_data.model_copy(update={"firstname": "NaoDeveriaFuncionar"})
    context.last_response = context.booking_client.update_booking(context.booking_id, updated, context.token_or_empty)


@then("o booking deve ser atualizado com sucesso")
def booking_deve_ser_atualizado_com_sucesso(context: Context) -> None:
    assert context.response.status_code == 200


@then("a resposta deve indicar acesso não autorizado")
def resposta_indica_acesso_nao_autorizado(context: Context) -> None:
    assert context.response.status_code == 403


@when(parsers.parse('ele atualiza parcialmente o booking alterando o sobrenome para "{lastname}"'))
@when(parsers.parse('ele tenta atualizar parcialmente o booking alterando o sobrenome para "{lastname}"'))
def atualiza_parcialmente_o_sobrenome(context: Context, lastname: str) -> None:
    assert context.booking_id is not None
    context.last_response = context.booking_client.partial_update_booking(
        context.booking_id, {"lastname": lastname}, context.token_or_empty
    )


@then(parsers.parse('o sobrenome do booking deve ser "{lastname}"'))
def sobrenome_do_booking_deve_ser(context: Context, lastname: str) -> None:
    body = Booking.model_validate_json(context.response.text)
    assert body.lastname == lastname


@when("ele atualiza o booking com corpo vazio")
def atualiza_o_booking_com_corpo_vazio(context: Context) -> None:
    assert context.booking_id is not None
    context.last_response = context.booking_client.update_booking_raw(context.booking_id, {}, context.token_or_empty)


@then("a resposta deve indicar requisição inválida")
def resposta_indica_requisicao_invalida(context: Context) -> None:
    assert context.response.status_code == 400


@when("ele atualiza o booking com totalprice em formato inválido")
def atualiza_o_booking_com_totalprice_invalido(context: Context) -> None:
    assert context.booking_id is not None
    payload = _booking_payload(totalprice="nao-e-numero")
    context.last_response = context.booking_client.update_booking_raw(
        context.booking_id, payload, context.token_or_empty
    )


@then("o totalprice do booking atualizado deve ser nulo")
def totalprice_do_booking_atualizado_deve_ser_nulo(context: Context) -> None:
    assert context.response.json()["totalprice"] is None


@when("ele atualiza o booking sem o campo bookingdates")
def atualiza_o_booking_sem_bookingdates(context: Context) -> None:
    assert context.booking_id is not None
    payload = _booking_payload(without="bookingdates")
    context.last_response = context.booking_client.update_booking_raw(
        context.booking_id, payload, context.token_or_empty
    )


@when("ele atualiza parcialmente o booking com lastname em formato inválido")
def atualiza_parcialmente_o_booking_com_lastname_invalido(context: Context) -> None:
    assert context.booking_id is not None
    context.last_response = context.booking_client.partial_update_booking(
        context.booking_id, {"lastname": 12345}, context.token_or_empty
    )


@then("o lastname do booking atualizado deve ser o valor numérico enviado")
def lastname_do_booking_atualizado_deve_ser_o_valor_numerico(context: Context) -> None:
    assert context.response.json()["lastname"] == 12345


@when("ele atualiza parcialmente o booking com corpo vazio")
def atualiza_parcialmente_o_booking_com_corpo_vazio(context: Context) -> None:
    assert context.booking_id is not None
    context.last_response = context.booking_client.partial_update_booking(
        context.booking_id, {}, context.token_or_empty
    )


@then("os dados do booking não devem ter sido alterados")
def dados_do_booking_nao_devem_ter_sido_alterados(context: Context) -> None:
    body = Booking.model_validate_json(context.response.text)
    assert body == context.booking_data


@when(parsers.parse('ele tenta "{verbo}" um booking inexistente'))
def tenta_verbo_um_booking_inexistente(context: Context, verbo: str) -> None:
    if verbo == "atualizar":
        context.last_response = context.booking_client.update_booking(
            999999999, _default_booking(), context.token_or_empty
        )
    else:
        context.last_response = context.booking_client.partial_update_booking(
            999999999, {"lastname": "Novo"}, context.token_or_empty
        )


# REMOÇÃO
@when("ele remove o booking")
@when("ele tenta remover o booking")
def remove_o_booking(context: Context) -> None:
    assert context.booking_id is not None
    context.last_response = context.booking_client.delete_booking(context.booking_id, context.token_or_empty)


@when(parsers.parse('ele tenta remover o booking pelo id "{booking_id}"'))
def tenta_remover_o_booking_pelo_id_informado(context: Context, booking_id: str) -> None:
    context.last_response = context.booking_client.delete_booking(int(booking_id), context.token_or_empty)


@then("o booking deve ser removido com sucesso")
def booking_deve_ser_removido_com_sucesso(context: Context) -> None:
    assert context.response.status_code == 201


@then("a resposta deve indicar que o método não é permitido")
def resposta_indica_metodo_nao_permitido(context: Context) -> None:
    assert context.response.status_code == 405
