from datetime import date
from typing import Any
from uuid import uuid4

from models.booking import Booking, BookingDates


# O sufixo aleatório no sobrenome deixa cada booking identificável na API
# pública, que é compartilhada: a busca por nome encontra só o booking do
# próprio teste, mesmo com outras execuções rodando ao mesmo tempo.
def default_booking() -> Booking:
    return Booking(
        firstname="Fulano",
        lastname=f"Ciclano-{uuid4().hex[:6]}",
        totalprice=150,
        depositpaid=True,
        bookingdates=BookingDates(checkin=date(2026, 1, 1), checkout=date(2026, 1, 5)),
        additionalneeds="Breakfast",
    )


# Payload cru (sem passar pelo Pydantic) a partir do booking padrão, trocando
# só o que interessa ao cenário: um campo com valor inválido (overrides) ou um
# campo obrigatório ausente (without).
def booking_payload(*, without: str | None = None, **overrides: Any) -> dict[str, Any]:
    payload = default_booking().model_dump(mode="json", exclude_none=True)
    payload.update(overrides)
    if without is not None:
        del payload[without]
    return payload
