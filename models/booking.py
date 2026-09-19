from pydantic import BaseModel


class BookingDates(BaseModel):
    checkin: str
    checkout: str


class Booking(BaseModel):
    firstname: str
    lastname: str
    totalprice: float
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: str | None = None


class BookingId(BaseModel):
    bookingid: int


class CreateBookingResponse(BaseModel):
    bookingid: int
    booking: Booking


class AuthResponse(BaseModel):
    token: str
