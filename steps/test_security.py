from pytest_bdd import given, scenarios, then, when

from conftest import Context
from models.booking import BookingIdList, CreateBookingResponse
from steps.booking_data import booking_payload, default_booking

scenarios("../features/security.feature")

SCRIPT = "<script>alert(1)</script>"


def _register_created_booking(context: Context) -> None:
    if context.response.status_code == 200:
        context.booking_id = CreateBookingResponse.model_validate_json(context.response.text).bookingid


# INJEÇÃO NOSQL
@when("o usuário busca bookings com um operador do banco no filtro de lastname")
def busca_com_operador_no_filtro(context: Context) -> None:
    context.last_response = context.booking_client.get_booking_ids_raw({"lastname[$ne]": "valor-que-nao-existe"})


@then("o booking criado deve aparecer mesmo sem ter o sobrenome buscado")
def booking_aparece_com_o_operador(context: Context) -> None:
    assert context.response.status_code == 200
    body = BookingIdList.validate_json(context.response.text)
    assert any(b.bookingid == context.booking_id for b in body)


@when("o usuário tenta fazer login com um operador do banco no lugar da senha")
def login_com_operador_na_senha(context: Context) -> None:
    context.last_response = context.auth_client.create_token_raw(
        {"username": context.auth_client.username, "password": {"$ne": None}}
    )


@then("o login deve ser recusado")
def login_recusado(context: Context) -> None:
    body = context.response.json()
    assert body.get("reason") == "Bad credentials"
    assert "token" not in body


# CABEÇALHOS
@then("a resposta deve expor a tecnologia do servidor no cabeçalho X-Powered-By")
def expoe_x_powered_by(context: Context) -> None:
    assert context.response.headers.get("X-Powered-By") == "Express"


@then("a resposta não deve trazer os cabeçalhos X-Content-Type-Options e X-Frame-Options")
def sem_cabecalhos_de_seguranca(context: Context) -> None:
    assert "X-Content-Type-Options" not in context.response.headers
    assert "X-Frame-Options" not in context.response.headers


# SCRIPT EM CAMPO DE TEXTO
@when("o usuário cria um booking com um script no firstname")
def cria_booking_com_script(context: Context) -> None:
    context.booking_data = default_booking().model_copy(update={"firstname": SCRIPT})
    context.last_response = context.booking_client.create_booking(context.booking_data)
    _register_created_booking(context)


@when("o usuário consulta esse booking")
def consulta_esse_booking(context: Context) -> None:
    assert context.booking_id is not None
    context.last_response = context.booking_client.get_booking(context.booking_id)


@then("a resposta deve ser JSON, e não HTML")
def resposta_json(context: Context) -> None:
    assert context.response.headers["Content-Type"].startswith("application/json")


@then("o firstname deve voltar exatamente como foi enviado")
def firstname_igual(context: Context) -> None:
    assert context.response.json()["firstname"] == SCRIPT


# RESPOSTAS DE ERRO
@when("o usuário cria um booking com um corpo que não é JSON válido")
def cria_booking_com_json_malformado(context: Context) -> None:
    context.last_response = context.booking_client.create_booking_from_text("{nao-e-json")


# Um rastro de pilha do Node traria linhas como "at Object.<anonymous>" e o
# caminho de arquivos do servidor; a resposta segura é só a frase genérica.
@then("a resposta deve ser um erro genérico, sem detalhes internos")
def erro_generico(context: Context) -> None:
    assert context.response.status_code == 400
    assert context.response.text == "Bad Request"


# ATRIBUIÇÃO EM MASSA
@when("o usuário cria um booking informando o próprio bookingid")
def cria_booking_com_bookingid(context: Context) -> None:
    context.last_response = context.booking_client.create_booking_raw(booking_payload(bookingid=1))
    _register_created_booking(context)


@then("a API deve ignorar o bookingid enviado")
def bookingid_ignorado(context: Context) -> None:
    body = context.response.json()
    assert body["bookingid"] != 1
    assert "bookingid" not in body["booking"]


# SESSÃO
@given("que o usuário faz um novo login")
def faz_novo_login(context: Context) -> None:
    novo_token = context.auth_client.get_valid_token()
    assert novo_token != context.token


@when("o usuário atualiza parcialmente o booking com o token anterior")
def atualiza_com_token_anterior(context: Context) -> None:
    assert context.booking_id is not None
    context.last_response = context.booking_client.partial_update_booking(
        context.booking_id, {"lastname": "TokenAntigo"}, context.token_or_empty
    )


@then("o token anterior ainda deve ser aceito")
def token_anterior_aceito(context: Context) -> None:
    assert context.response.status_code == 200
