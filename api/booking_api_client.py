from typing import Any

import requests

from models.booking import Booking


class BookingApiClient:
    def __init__(self, session: requests.Session, base_url: str) -> None:
        self.session = session
        self.base_url = base_url

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
        return self.session.get(f"{self.base_url}/booking", params=params)

    def get_booking(self, booking_id: int) -> requests.Response:
        return self.session.get(f"{self.base_url}/booking/{booking_id}")

    def create_booking(self, booking: Booking) -> requests.Response:
        return self.session.post(f"{self.base_url}/booking", json=booking.model_dump(exclude_none=True))

    def update_booking(self, booking_id: int, booking: Booking, token: str) -> requests.Response:
        return self.session.put(
            f"{self.base_url}/booking/{booking_id}",
            json=booking.model_dump(exclude_none=True),
            cookies={"token": token},
        )

    def partial_update_booking(self, booking_id: int, partial_booking: dict[str, Any], token: str) -> requests.Response:
        return self.session.patch(
            f"{self.base_url}/booking/{booking_id}",
            json=partial_booking,
            cookies={"token": token},
        )

    def delete_booking(self, booking_id: int, token: str) -> requests.Response:
        return self.session.delete(f"{self.base_url}/booking/{booking_id}", cookies={"token": token})

    def exemplo_com_bug(self, booking_id: int) -> None:
        self.get_booking(booking_id)
