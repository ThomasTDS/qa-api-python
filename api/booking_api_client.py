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
        return self._request("POST", "/booking", json=booking.model_dump(exclude_none=True))

    # Recebe um dict cru (sem passar pela validação do Pydantic) para testes
    # negativos que precisam mandar um payload propositalmente inválido.
    def create_booking_raw(self, payload: dict[str, Any]) -> requests.Response:
        return self._request("POST", "/booking", json=payload)

    def update_booking(self, booking_id: int, booking: Booking, token: str) -> requests.Response:
        return self._request(
            "PUT",
            f"/booking/{booking_id}",
            json=booking.model_dump(exclude_none=True),
            cookies={"token": token},
        )

    # Variante crua de update_booking, para os testes de payload inválido no PUT
    # (campos ausentes ou com tipo errado, que não passariam pelo tipo Booking).
    def update_booking_raw(self, booking_id: int, payload: dict[str, Any], token: str) -> requests.Response:
        return self._request("PUT", f"/booking/{booking_id}", json=payload, cookies={"token": token})

    def partial_update_booking(self, booking_id: int, partial_booking: dict[str, Any], token: str) -> requests.Response:
        return self._request("PATCH", f"/booking/{booking_id}", json=partial_booking, cookies={"token": token})

    def delete_booking(self, booking_id: int, token: str) -> requests.Response:
        return self._request("DELETE", f"/booking/{booking_id}", cookies={"token": token})
