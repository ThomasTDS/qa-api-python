from pytest_bdd import parsers, scenarios, then, when

from conftest import Context

scenarios("../features/delete_booking.feature")


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
