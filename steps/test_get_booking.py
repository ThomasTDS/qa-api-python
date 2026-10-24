from datetime import date

from pytest_bdd import given, parsers, scenarios, then, when

from conftest import Context
from models.booking import Booking, BookingDates, BookingIdList, CreateBookingResponse
from steps.booking_data import default_booking

scenarios("../features/get_booking.feature")


@when("o usuário busca o booking pelo id")
def busca_o_booking_pelo_id(context: Context) -> None:
    assert context.booking_id is not None
    context.last_response = context.booking_client.get_booking(context.booking_id)


@when(parsers.parse('o usuário busca o booking pelo id "{booking_id}"'))
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


@when("o usuário busca bookings filtrando pelo firstname e lastname do booking criado")
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


@when("o usuário busca bookings filtrando por um firstname e lastname que não correspondem a nenhum booking")
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


# FILTROS POR DATA
# As datas ficam explícitas no cenário porque o que se testa é a fronteira
# entre a data do booking e a data do filtro.
@given(parsers.parse('que existe um booking criado com checkin em "{checkin}" e checkout em "{checkout}"'))
def existe_um_booking_criado_com_datas(context: Context, checkin: str, checkout: str) -> None:
    dates = BookingDates(checkin=date.fromisoformat(checkin), checkout=date.fromisoformat(checkout))
    context.booking_data = default_booking().model_copy(update={"bookingdates": dates})
    response = context.booking_client.create_booking(context.booking_data)
    context.booking_id = CreateBookingResponse.model_validate_json(response.text).bookingid


# Combina o filtro de data com o nome do booking criado, para que o resultado
# não dependa dos outros bookings que existem na API.
@when(parsers.parse('o usuário busca o booking criado com o filtro de {campo} "{data}"'))
def busca_o_booking_criado_com_filtro_de_data(context: Context, campo: str, data: str) -> None:
    assert campo in ("checkin", "checkout"), campo
    assert context.booking_data is not None
    context.last_response = context.booking_client.get_booking_ids(
        firstname=context.booking_data.firstname,
        lastname=context.booking_data.lastname,
        **{campo: data},
    )


@when(parsers.parse('o usuário busca bookings com o filtro de checkin "{data}"'))
def busca_bookings_com_filtro_de_checkin(context: Context, data: str) -> None:
    context.last_response = context.booking_client.get_booking_ids(checkin=data)
