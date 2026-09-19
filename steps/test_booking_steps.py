import pytest
from pydantic import ValidationError
from pytest_bdd import given, parsers, scenarios, then, when

from conftest import Context
from models.booking import AuthResponse, Booking, BookingDates, BookingId, CreateBookingResponse

scenarios("../features")


def _default_booking() -> Booking:
    return Booking(
        firstname="Fulano",
        lastname="Ciclano",
        totalprice=150,
        depositpaid=True,
        bookingdates=BookingDates(checkin="2026-01-01", checkout="2026-01-05"),
        additionalneeds="Breakfast",
    )


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


@when(parsers.parse('ele solicita um token com o usuário "{username}" e a senha "{password}"'))
def solicita_um_token(context: Context, username: str, password: str) -> None:
    context.last_response = context.auth_client.create_token(username, password)


@then("ele deve receber um token de autenticação válido")
def deve_receber_um_token_valido(context: Context) -> None:
    assert context.last_response is not None
    assert context.last_response.status_code == 200
    body = AuthResponse.model_validate(context.last_response.json())
    assert body.token


@then("a resposta deve indicar credenciais inválidas")
def resposta_indica_credenciais_invalidas(context: Context) -> None:
    assert context.last_response is not None
    body = context.last_response.json()
    assert body["reason"] == "Bad credentials"


# CRIAÇÃO
@given("que existe um booking criado")
def existe_um_booking_criado(context: Context) -> None:
    context.booking_data = _default_booking()
    response = context.booking_client.create_booking(context.booking_data)
    body = CreateBookingResponse.model_validate(response.json())
    context.booking_id = body.bookingid


@when("ele cria um booking com dados válidos")
def cria_um_booking_com_dados_validos(context: Context) -> None:
    context.booking_data = _default_booking()
    context.last_response = context.booking_client.create_booking(context.booking_data)


@then("o booking deve ser criado com sucesso")
def booking_deve_ser_criado_com_sucesso(context: Context) -> None:
    assert context.last_response is not None
    assert context.last_response.status_code == 200


@then("o id do booking criado deve ser retornado")
def id_do_booking_criado_deve_ser_retornado(context: Context) -> None:
    assert context.last_response is not None
    body = CreateBookingResponse.model_validate(context.last_response.json())
    assert body.bookingid > 0
    context.booking_id = body.bookingid


@when("ele tenta criar um booking sem informar o firstname")
def tenta_criar_booking_sem_firstname(context: Context) -> None:
    payload = {
        "lastname": "Ciclano",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-05"},
    }
    context.last_response = context.booking_client.create_booking_raw(payload)


@then("a resposta deve indicar um erro interno do servidor")
def resposta_indica_erro_interno_do_servidor(context: Context) -> None:
    assert context.last_response is not None
    assert context.last_response.status_code == 500


@when("ele cria um booking com totalprice em formato inválido")
def cria_booking_com_totalprice_invalido(context: Context) -> None:
    payload = {
        "firstname": "Fulano",
        "lastname": "Ciclano",
        "totalprice": "nao-e-numero",
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-05"},
    }
    context.last_response = context.booking_client.create_booking_raw(payload)
    # A resposta não bate com o schema, mas o id criado é válido e precisa
    # ser limpo no final do teste como qualquer outro booking.
    context.booking_id = context.last_response.json().get("bookingid")


@then("a resposta da API não deve corresponder ao schema esperado")
def resposta_nao_corresponde_ao_schema(context: Context) -> None:
    assert context.last_response is not None
    assert context.last_response.status_code == 200
    with pytest.raises(ValidationError):
        CreateBookingResponse.model_validate(context.last_response.json())


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
    assert context.last_response is not None
    assert context.last_response.status_code == 200
    body = Booking.model_validate(context.last_response.json())
    assert body == context.booking_data


@then("a resposta deve indicar que o booking não foi encontrado")
def resposta_indica_booking_nao_encontrado(context: Context) -> None:
    assert context.last_response is not None
    assert context.last_response.status_code == 404


@when("ele busca bookings filtrando pelo firstname e lastname do booking criado")
def busca_bookings_filtrando_pelo_booking_criado(context: Context) -> None:
    assert context.booking_data is not None
    context.last_response = context.booking_client.get_booking_ids(
        firstname=context.booking_data.firstname,
        lastname=context.booking_data.lastname,
    )


@then("o id do booking criado deve estar entre os resultados")
def id_do_booking_criado_esta_entre_os_resultados(context: Context) -> None:
    assert context.last_response is not None
    assert context.last_response.status_code == 200
    body = [BookingId.model_validate(item) for item in context.last_response.json()]
    assert any(b.bookingid == context.booking_id for b in body)


@when("ele busca bookings filtrando por um firstname e lastname que não correspondem a nenhum booking")
def busca_bookings_filtrando_por_dados_inexistentes(context: Context) -> None:
    context.last_response = context.booking_client.get_booking_ids(
        firstname="Inexistente-xyz-999",
        lastname="NaoExiste-abc-000",
    )


@then("o id do booking criado não deve estar entre os resultados")
def id_do_booking_criado_nao_esta_entre_os_resultados(context: Context) -> None:
    assert context.last_response is not None
    assert context.last_response.status_code == 200
    body = [BookingId.model_validate(item) for item in context.last_response.json()]
    assert not any(b.bookingid == context.booking_id for b in body)


# ATUALIZAÇÃO (PUT/PATCH)
@when("ele atualiza o booking com novos dados")
def atualiza_o_booking_com_novos_dados(context: Context) -> None:
    assert context.booking_data is not None
    assert context.booking_id is not None
    updated = context.booking_data.model_copy(update={"firstname": "Atualizado", "totalprice": 200})
    context.last_response = context.booking_client.update_booking(context.booking_id, updated, context.token or "")
    context.booking_data = updated


@when("ele tenta atualizar o booking com novos dados")
def tenta_atualizar_o_booking_com_novos_dados(context: Context) -> None:
    assert context.booking_data is not None
    assert context.booking_id is not None
    updated = context.booking_data.model_copy(update={"firstname": "NaoDeveriaFuncionar"})
    context.last_response = context.booking_client.update_booking(context.booking_id, updated, context.token or "")


@then("o booking deve ser atualizado com sucesso")
def booking_deve_ser_atualizado_com_sucesso(context: Context) -> None:
    assert context.last_response is not None
    assert context.last_response.status_code == 200


@then("a resposta deve indicar acesso não autorizado")
def resposta_indica_acesso_nao_autorizado(context: Context) -> None:
    assert context.last_response is not None
    assert context.last_response.status_code == 403


@when(parsers.parse('ele atualiza parcialmente o booking alterando o sobrenome para "{lastname}"'))
def atualiza_parcialmente_o_sobrenome(context: Context, lastname: str) -> None:
    assert context.booking_id is not None
    context.last_response = context.booking_client.partial_update_booking(
        context.booking_id, {"lastname": lastname}, context.token or ""
    )


@when(parsers.parse('ele tenta atualizar parcialmente o booking alterando o sobrenome para "{lastname}"'))
def tenta_atualizar_parcialmente_o_sobrenome(context: Context, lastname: str) -> None:
    assert context.booking_id is not None
    context.last_response = context.booking_client.partial_update_booking(
        context.booking_id, {"lastname": lastname}, context.token or ""
    )


@then(parsers.parse('o sobrenome do booking deve ser "{lastname}"'))
def sobrenome_do_booking_deve_ser(context: Context, lastname: str) -> None:
    assert context.last_response is not None
    body = Booking.model_validate(context.last_response.json())
    assert body.lastname == lastname


# REMOÇÃO
@when("ele remove o booking")
def remove_o_booking(context: Context) -> None:
    assert context.booking_id is not None
    context.last_response = context.booking_client.delete_booking(context.booking_id, context.token or "")


@when("ele tenta remover o booking")
def tenta_remover_o_booking(context: Context) -> None:
    assert context.booking_id is not None
    context.last_response = context.booking_client.delete_booking(context.booking_id, context.token or "")


@when(parsers.parse('ele tenta remover o booking pelo id "{booking_id}"'))
def tenta_remover_o_booking_pelo_id_informado(context: Context, booking_id: str) -> None:
    context.last_response = context.booking_client.delete_booking(int(booking_id), context.token or "")


@then("o booking deve ser removido com sucesso")
def booking_deve_ser_removido_com_sucesso(context: Context) -> None:
    assert context.last_response is not None
    assert context.last_response.status_code == 201


@then("a resposta deve indicar que o método não é permitido")
def resposta_indica_metodo_nao_permitido(context: Context) -> None:
    assert context.last_response is not None
    assert context.last_response.status_code == 405
