from pytest_bdd import parsers, scenarios, then, when

from conftest import Context
from models.booking import Booking
from steps.booking_data import booking_payload, default_booking

scenarios("../features/update_booking.feature")


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
    payload = booking_payload(totalprice="nao-e-numero")
    context.last_response = context.booking_client.update_booking_raw(
        context.booking_id, payload, context.token_or_empty
    )


@then("o totalprice do booking atualizado deve ser nulo")
def totalprice_do_booking_atualizado_deve_ser_nulo(context: Context) -> None:
    assert context.response.json()["totalprice"] is None


@when("ele atualiza o booking sem o campo bookingdates")
def atualiza_o_booking_sem_bookingdates(context: Context) -> None:
    assert context.booking_id is not None
    payload = booking_payload(without="bookingdates")
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
            999999999, default_booking(), context.token_or_empty
        )
    else:
        context.last_response = context.booking_client.partial_update_booking(
            999999999, {"lastname": "Novo"}, context.token_or_empty
        )
