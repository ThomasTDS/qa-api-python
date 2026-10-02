# Steps usados por mais de uma feature. Ficam disponíveis para todos os
# módulos de teste via pytest_plugins, no conftest.py da raiz.
from pytest_bdd import given, then

from conftest import Context
from models.booking import CreateBookingResponse
from steps.booking_data import default_booking


@given("que o usuário não possui nenhum token de autenticação")
def sem_token_de_autenticacao(context: Context) -> None:
    context.token = None


@given("que o usuário possui um token de autenticação válido")
def com_token_de_autenticacao_valido(context: Context) -> None:
    context.token = context.auth_client.get_valid_token()


@given("que o usuário possui um token de autenticação inválido")
def com_token_de_autenticacao_invalido(context: Context) -> None:
    context.token = "token-invalido-qualquer"


@given("que existe um booking criado")
def existe_um_booking_criado(context: Context) -> None:
    context.booking_data = default_booking()
    response = context.booking_client.create_booking(context.booking_data)
    body = CreateBookingResponse.model_validate_json(response.text)
    context.booking_id = body.bookingid


@then("a resposta deve indicar acesso não autorizado")
def resposta_indica_acesso_nao_autorizado(context: Context) -> None:
    assert context.response.status_code == 403


@then("a resposta deve indicar que o método não é permitido")
def resposta_indica_metodo_nao_permitido(context: Context) -> None:
    assert context.response.status_code == 405
