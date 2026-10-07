from __future__ import annotations

from pydantic import BaseModel


class FareRead(BaseModel):
    id: int
    origin: str
    destination: str
    airline: str
    flight_number: str
    total_price_paisa: int
    seats_left: int
    refundable: bool
