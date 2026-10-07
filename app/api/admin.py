from __future__ import annotations

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import AirlineTicketRequest, Booking, Payment, WebhookEvent
from app.services.auth import require_partner_scope

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/payments")
def list_payments(
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    require_partner_scope(db, authorization, "bookings:read")
    payments = db.query(Payment).order_by(Payment.created_at.desc()).limit(200).all()
    rows = []
    for payment in payments:
        booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
        rows.append(
            {
                "id": payment.id,
                "booking_reference": booking.public_reference if booking else None,
                "amount_paisa": payment.amount_paisa,
                "currency": payment.currency,
                "status": payment.status,
                "idempotency_key": payment.idempotency_key,
                "created_at": payment.created_at.isoformat(),
                "updated_at": payment.updated_at.isoformat(),
            }
        )
    return rows


@router.get("/webhook-events")
def list_webhook_events(
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    require_partner_scope(db, authorization, "bookings:read")
    events = db.query(WebhookEvent).order_by(WebhookEvent.timestamp.desc()).limit(200).all()
    return [
        {
            "id": event.id,
            "event_id": event.event_id,
            "provider": event.provider,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "processed_at": event.processed_at.isoformat(),
            "payload_hash": event.payload_hash,
        }
        for event in events
    ]


@router.get("/airline-requests")
def list_airline_requests(
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    require_partner_scope(db, authorization, "bookings:read")
    requests = db.query(AirlineTicketRequest).order_by(AirlineTicketRequest.created_at.desc()).limit(200).all()
    rows = []
    for req in requests:
        booking = db.query(Booking).filter(Booking.id == req.booking_id).first()
        rows.append(
            {
                "id": req.id,
                "booking_reference": booking.public_reference if booking else None,
                "idempotency_key": req.idempotency_key,
                "status": req.status,
                "pnr": req.pnr,
                "attempt_count": req.attempt_count,
                "last_error": req.last_error,
                "created_at": req.created_at.isoformat(),
                "updated_at": req.updated_at.isoformat(),
            }
        )
    return rows
