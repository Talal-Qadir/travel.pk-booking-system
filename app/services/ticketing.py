from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import AirlineTicketRequest, Booking
from app.suppliers.airline import issue_airline_ticket


def schedule_ticketing(db: Session, booking: Booking) -> None:
    if booking.status != "PAID":
        return

    existing = db.query(AirlineTicketRequest).filter(AirlineTicketRequest.booking_id == booking.id).first()
    if existing is not None and existing.status in {"COMPLETED", "IN_PROGRESS"}:
        return

    idempotency_key = f"ticket-{booking.public_reference}"
    if existing is None:
        ticket_req = AirlineTicketRequest(
            booking_id=booking.id,
            idempotency_key=idempotency_key,
            status="IN_PROGRESS",
            attempt_count=1,
        )
        db.add(ticket_req)
    else:
        ticket_req = existing
        ticket_req.status = "IN_PROGRESS"
        ticket_req.attempt_count += 1
    booking.status = "TICKETING"
    booking.updated_at = datetime.now(timezone.utc)
    db.commit()

    try:
        result = asyncio.run(issue_airline_ticket(booking.public_reference, idempotency_key))
        pnr = result.get("pnr")
        booking.pnr = pnr
        booking.status = "TICKETED"
        booking.ticketed_at = datetime.now(timezone.utc)
        booking.updated_at = datetime.now(timezone.utc)
        ticket_req.status = "COMPLETED"
        ticket_req.pnr = pnr
        ticket_req.last_error = None
    except Exception as exc:  # noqa: BLE001 — airline stub failures for demo
        ticket_req.status = "FAILED"
        ticket_req.last_error = str(exc)
        booking.status = "PAID"
    ticket_req.updated_at = datetime.now(timezone.utc)
    db.commit()
