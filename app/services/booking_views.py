from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.db.models import AirlineTicketRequest, Booking, Fare, Payment


def _latest_payment(db: Session, booking_id: int) -> Payment | None:
    return (
        db.query(Payment)
        .filter(Payment.booking_id == booking_id)
        .order_by(Payment.created_at.desc())
        .first()
    )


def compute_refund_paisa(db: Session, booking: Booking, fare: Fare | None) -> int:
    payment = _latest_payment(db, booking.id)
    if payment is None or payment.status not in {"SUCCEEDED", "PENDING"}:
        return 0
    if fare is not None and not fare.refundable:
        return 0
    return booking.total_price_paisa


def can_cancel_booking(booking: Booking) -> bool:
    return booking.status not in {"CANCELLED", "EXPIRED", "REFUNDED", "FAILED"}


def serialize_booking_detail(db: Session, booking: Booking) -> dict[str, Any]:
    fare = db.query(Fare).filter(Fare.id == booking.fare_id).first()
    payment = _latest_payment(db, booking.id)
    ticket_req = db.query(AirlineTicketRequest).filter(AirlineTicketRequest.booking_id == booking.id).first()

    route = f"{fare.origin} → {fare.destination}" if fare else "unknown"
    payment_block: dict[str, Any] | None = None
    if payment is not None:
        payment_block = {
            "id": payment.id,
            "amount_paisa": payment.amount_paisa,
            "currency": payment.currency,
            "status": payment.status,
            "idempotency_key": payment.idempotency_key,
            "psp_reference": payment.psp_reference,
            "created_at": payment.created_at.isoformat(),
            "updated_at": payment.updated_at.isoformat(),
        }

    ticket_block: dict[str, Any] | None = None
    if ticket_req is not None:
        ticket_block = {
            "status": ticket_req.status,
            "pnr": ticket_req.pnr or booking.pnr,
            "attempt_count": ticket_req.attempt_count,
            "idempotency_key": ticket_req.idempotency_key,
            "last_error": ticket_req.last_error,
            "airline_reference": ticket_req.airline_reference,
            "updated_at": ticket_req.updated_at.isoformat(),
        }
    elif booking.pnr:
        ticket_block = {
            "status": "COMPLETED" if booking.status == "TICKETED" else booking.status,
            "pnr": booking.pnr,
            "attempt_count": 0,
            "idempotency_key": None,
            "last_error": None,
            "airline_reference": None,
            "updated_at": booking.updated_at.isoformat(),
        }

    return {
        "booking_reference": booking.public_reference,
        "route": route,
        "origin": fare.origin if fare else None,
        "destination": fare.destination if fare else None,
        "customer_name": booking.customer_name or "Guest",
        "fare": {
            "id": fare.id,
            "airline": fare.airline,
            "flight_number": fare.flight_number,
            "refundable": fare.refundable,
        }
        if fare
        else {},
        "price_paisa": booking.total_price_paisa,
        "base_price_paisa": booking.base_price_paisa,
        "taxes_paisa": booking.taxes_paisa,
        "status": booking.status,
        "expires_at": booking.expires_at.isoformat() if booking.expires_at else None,
        "payment": payment_block,
        "payment_status": payment.status if payment else None,
        "ticket": ticket_block,
        "pnr": booking.pnr,
        "ticketed_at": booking.ticketed_at.isoformat() if booking.ticketed_at else None,
        "created_at": booking.created_at.isoformat(),
        "updated_at": booking.updated_at.isoformat(),
        "refund_preview_paisa": compute_refund_paisa(db, booking, fare),
        "can_cancel": can_cancel_booking(booking),
        "can_pay": booking.status in {"HELD", "PAYMENT_PENDING"},
    }


def serialize_booking_summary(db: Session, booking: Booking) -> dict[str, Any]:
    fare = db.query(Fare).filter(Fare.id == booking.fare_id).first()
    payment = _latest_payment(db, booking.id)
    route = f"{fare.origin} → {fare.destination}" if fare else "unknown"
    return {
        "booking_reference": booking.public_reference,
        "route": route,
        "customer_name": booking.customer_name or "Guest",
        "amount_paisa": booking.total_price_paisa,
        "status": booking.status,
        "payment_status": payment.status if payment else None,
        "pnr": booking.pnr,
        "created_at": booking.created_at.isoformat(),
    }
