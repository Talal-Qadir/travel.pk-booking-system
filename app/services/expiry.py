from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import Booking, Fare


def expire_booking_if_needed(db: Session, booking: Booking | None = None) -> None:
    now = datetime.now(timezone.utc)
    pending = db.query(Booking).filter(Booking.status == "HELD", Booking.expires_at < now)
    if booking is not None:
        pending = pending.filter(Booking.id == booking.id)

    expires = pending.all()
    for expired in expires:
        db.execute(
            "UPDATE bookings SET status = 'EXPIRED', updated_at = :updated_at WHERE id = :booking_id AND status = 'HELD'",
            {"updated_at": now, "booking_id": expired.id},
        )

    if not expires:
        return

    seats_to_release = []
    for expired in expires:
        seats_to_release.append(expired.fare_id)

    for fare_id in sorted(set(seats_to_release)):
        db.execute(
            "UPDATE fares SET seats_left = seats_left + 1 WHERE id = :fare_id",
            {"fare_id": fare_id},
        )

    db.commit()
