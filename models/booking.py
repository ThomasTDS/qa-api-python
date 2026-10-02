from datetime import date

from pydantic import BaseModel, ConfigDict, TypeAdapter


# Modo estrito: o Pydantic deixa de converter tipos por conta própria. Sem
# ele, um totalprice "150" (texto) viraria 150.0 e um depositpaid "true"
# viraria True, e uma mudança de tipo na resposta da API passaria sem ser
# notada. Campos extras na resposta continuam sendo ignorados, já que a API é
# de terceiros e um campo a mais não é defeito.
class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True)


class BookingDates(StrictModel):
    checkin: date
    checkout: date


class Booking(StrictModel):
    firstname: str
    lastname: str
    totalprice: float
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: str | None = None


class BookingId(StrictModel):
    bookingid: int


class CreateBookingResponse(StrictModel):
    bookingid: int
    booking: Booking


class AuthResponse(StrictModel):
    token: str


# GET /booking devolve uma lista solta, sem um objeto em volta, então a
# validação é feita por um TypeAdapter em vez de um modelo.
BookingIdList = TypeAdapter(list[BookingId])
