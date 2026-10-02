from pytest_bdd import parsers, scenarios, then, when

from conftest import Context
from models.booking import AuthResponse

scenarios("../features/auth.feature")


@when("o usuário solicita um token com credenciais válidas")
def solicita_um_token_com_credenciais_validas(context: Context) -> None:
    client = context.auth_client
    context.last_response = client.create_token(client.username, client.password)


@when(parsers.parse('o usuário solicita um token com o login "{username}" e a senha "{password}"'))
def solicita_um_token(context: Context, username: str, password: str) -> None:
    context.last_response = context.auth_client.create_token(username, password)


@then("o usuário deve receber um token de autenticação válido")
def deve_receber_um_token_valido(context: Context) -> None:
    assert context.response.status_code == 200
    body = AuthResponse.model_validate_json(context.response.text)
    assert body.token


@then("a resposta deve indicar credenciais inválidas")
def resposta_indica_credenciais_invalidas(context: Context) -> None:
    assert context.response.json()["reason"] == "Bad credentials"
