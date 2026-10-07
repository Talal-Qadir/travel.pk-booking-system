from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import HOLD_MINUTES, TOKEN_HOURS
from app.core.errors import api_error
from app.db.models import Booking, CustomerToken, Fare
from app.services.auth import generate_booking_reference, generate_customer_token, hash_secret
from app.services.expiry import expire_booking_if_needed


class ConflictError(RuntimeError):
    pass


class NotFoundError(RuntimeError):
    pass


def create_hold(db: Session, fare_id: int, customer_name: str) -> dict[str, Any]:
    expire_booking_if_needed(db)

    fare = db.query(Fare).filter(Fare.id == fare_id, Fare.active.is_(True)).first()
    if fare is None:
        raise api_error(404, "FARE_NOT_FOUND", "Fare not found.")
    if fare.seats_left <= 0:
        raise api_error(409, "NO_SEATS_AVAILABLE", "No seats available for this fare.")

    update_result = db.execute(
        text("UPDATE fares SET seats_left = seats_left - 1 WHERE id = :id AND seats_left > 0"),
        {"id": fare_id},
    )
    db.flush()
    if update_result.rowcount == 0:
        raise api_error(409, "NO_SEATS_AVAILABLE", "Inventory conflict.")

    booking_reference = generate_booking_reference()
    while db.query(Booking).filter(Booking.public_reference == booking_reference).first() is not None:
        booking_reference = generate_booking_reference()

    token = generate_customer_token()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=HOLD_MINUTES)

    booking = Booking(
        public_reference=booking_reference,
        fare_id=fare_id,
        customer_name=customer_name or "Guest",
        status="HELD",
        base_price_paisa=fare.base_price_paisa,
        taxes_paisa=fare.taxes_paisa,
        total_price_paisa=fare.total_price_paisa,
        expires_at=expires_at,
    )
    db.add(booking)
    db.flush()

    customer_token = CustomerToken(
        booking_id=booking.id,
        token_hash=hash_secret(token),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=TOKEN_HOURS),
    )
    db.add(customer_token)
    db.commit()

    return {
        "booking_reference": booking_reference,
        "price_snapshot_paisa": booking.total_price_paisa,
        "expires_at": expires_at.isoformat(),
        "customer_token": token,
        "route": f"{fare.origin} → {fare.destination}",
    }
