from pytest_bdd import parsers, scenarios, then, when

from conftest import Context
from models.booking import Booking, BookingIdList

scenarios("../features/get_booking.feature")


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
