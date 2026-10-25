import re
from datetime import date
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, TypeAdapter

ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


# Mesmo no modo estrito, o Pydantic aceita como data um texto numérico que
# represente um timestamp Unix exatamente à meia-noite: "0" virava 01/01/1970
# (achado pelos testes de propriedade com Hypothesis). Uma data em texto
# precisa estar no formato AAAA-MM-DD, o único que a API usa. O texto já sai
# daqui convertido em date, porque depois deste validador o modo estrito só
# aceita um objeto date, e não texto.
def _iso_date_text(value: object) -> object:
    if isinstance(value, str):
        if not ISO_DATE.fullmatch(value):
            raise ValueError("a data precisa estar no formato AAAA-MM-DD")
        return date.fromisoformat(value)
    return value


IsoDate = Annotated[date, BeforeValidator(_iso_date_text)]


# Modo estrito: o Pydantic deixa de converter tipos por conta própria. Sem
# ele, um totalprice "150" (texto) viraria 150.0 e um depositpaid "true"
# viraria True, e uma mudança de tipo na resposta da API passaria sem ser
# notada. Campos extras na resposta continuam sendo ignorados, já que a API é
# de terceiros e um campo a mais não é defeito.
#
# allow_inf_nan=False recusa NaN e infinito nos números. Sem isso, o modelo
# aceitava esses valores e os transformava em null ao montar o JSON da
# requisição, sem avisar (achado pelos testes de propriedade com Hypothesis).
class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True, allow_inf_nan=False)


class BookingDates(StrictModel):
    checkin: IsoDate
    checkout: IsoDate


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
