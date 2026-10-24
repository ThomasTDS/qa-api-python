from typing import Any

import requests

from api.base_api_client import BaseApiClient
from models.booking import Booking


class BookingApiClient(BaseApiClient):
    def get_booking_ids(
        self,
        firstname: str | None = None,
        lastname: str | None = None,
        checkin: str | None = None,
        checkout: str | None = None,
    ) -> requests.Response:
        params = {
            "firstname": firstname,
            "lastname": lastname,
            "checkin": checkin,
            "checkout": checkout,
        }
        params = {key: value for key, value in params.items() if value is not None}
        return self._request("GET", "/booking", params=params)

    def get_booking(self, booking_id: int) -> requests.Response:
        return self._request("GET", f"/booking/{booking_id}")

    def create_booking(self, booking: Booking) -> requests.Response:
        return self._request("POST", "/booking", json=booking.model_dump(mode="json", exclude_none=True))

    # Recebe um dict cru (sem passar pela validação do Pydantic) para testes
    # negativos que precisam mandar um payload propositalmente inválido.
    def create_booking_raw(self, payload: dict[str, Any]) -> requests.Response:
        return self._request("POST", "/booking", json=payload)

    # A API aceita duas formas de autenticação nas operações de escrita: o token
    # no cookie (padrão) ou usuário e senha em Basic auth. Com Basic auth e sem
    # token, o cookie não é enviado, para que a requisição use só o cabeçalho.
    @staticmethod
    def _credentials(token: str, basic_auth: tuple[str, str] | None) -> dict[str, Any]:
        if basic_auth is None:
            return {"cookies": {"token": token}}
        credentials: dict[str, Any] = {"auth": basic_auth}
        if token:
            credentials["cookies"] = {"token": token}
        return credentials

    def update_booking(
        self, booking_id: int, booking: Booking, token: str, basic_auth: tuple[str, str] | None = None
    ) -> requests.Response:
        return self._request(
            "PUT",
            f"/booking/{booking_id}",
            json=booking.model_dump(mode="json", exclude_none=True),
            **self._credentials(token, basic_auth),
        )

    # Variante crua de update_booking, para os testes de payload inválido no PUT
    # (campos ausentes ou com tipo errado, que não passariam pelo tipo Booking).
    def update_booking_raw(
        self, booking_id: int, payload: dict[str, Any], token: str, basic_auth: tuple[str, str] | None = None
    ) -> requests.Response:
        return self._request("PUT", f"/booking/{booking_id}", json=payload, **self._credentials(token, basic_auth))

    def partial_update_booking(
        self, booking_id: int, partial_booking: dict[str, Any], token: str, basic_auth: tuple[str, str] | None = None
    ) -> requests.Response:
        return self._request(
            "PATCH", f"/booking/{booking_id}", json=partial_booking, **self._credentials(token, basic_auth)
        )

    def delete_booking(
        self, booking_id: int, token: str, basic_auth: tuple[str, str] | None = None
    ) -> requests.Response:
        return self._request("DELETE", f"/booking/{booking_id}", **self._credentials(token, basic_auth))
