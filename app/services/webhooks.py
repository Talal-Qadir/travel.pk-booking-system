from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import PSP_SECRET
from app.core.errors import api_error
from app.db.models import Booking, Payment, WebhookEvent


def verify_psp_timestamp(timestamp_text: str) -> bool:
    try:
        ts = int(timestamp_text)
    except (TypeError, ValueError):
        return False
    now = int(datetime.now(timezone.utc).timestamp())
    return abs(now - ts) < 300


def verify_psp_signature(raw_body: bytes, timestamp_text: str, provided_signature: str | None) -> bool:
    if not provided_signature:
        return False
    signed = f"{timestamp_text}.{raw_body.decode('utf-8')}"
    expected = hmac.new(PSP_SECRET.encode("utf-8"), signed.encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, provided_signature)


def process_psp_webhook(db: Session, payload: dict, timestamp: str, signature: str | None) -> dict:
    if not verify_psp_timestamp(timestamp):
        raise api_error(401, "STALE_WEBHOOK", "Webhook timestamp is stale.")

    if not payload.get("psp_reference"):
        raise api_error(400, "INVALID_WEBHOOK", "Invalid webhook payload.")

    event_id = payload.get("event_id")
    if not event_id:
        raise api_error(400, "INVALID_WEBHOOK", "Invalid webhook payload.")

    if payload.get("status") != "paid":
        raise api_error(400, "INVALID_WEBHOOK", "Webhook status is not paid.")

    if payload.get("amount_paisa") is None:
        raise api_error(400, "INVALID_WEBHOOK", "Invalid webhook payload.")

    payment = db.query(Payment).filter(Payment.psp_reference == payload.get("psp_reference")).first()
    if payment is None:
        raise api_error(404, "PAYMENT_NOT_FOUND", "Payment not found.")

    if payload.get("amount_paisa") != payment.amount_paisa:
        raise api_error(400, "INVALID_WEBHOOK", "Webhook amount does not match the payment amount.")

    raw_body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if not verify_psp_signature(raw_body, timestamp, signature):
        raise api_error(401, "INVALID_WEBHOOK_SIGNATURE", "Invalid webhook signature.")

    existing = db.query(WebhookEvent).filter(WebhookEvent.event_id == event_id).first()
    if existing is not None:
        return {"status": "duplicate", "event_id": event_id}

    booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
    if booking is None:
        raise api_error(404, "BOOKING_NOT_FOUND", "Booking not found.")

    if booking.status in {"EXPIRED", "CANCELLED"}:
        payment.status = "REFUNDED"
    else:
        payment.status = "SUCCEEDED"
        if booking.status not in {"CANCELLED", "FAILED", "REFUNDED"}:
            booking.status = "PAID"

    db.add(WebhookEvent(
        event_id=event_id,
        provider="psp",
        event_type="payment_succeeded",
        timestamp=datetime.now(timezone.utc),
        payload_hash=hashlib.sha256(raw_body).hexdigest(),
    ))
    db.commit()

    if payment.status == "SUCCEEDED" and booking.status == "PAID":
        from app.services.ticketing import schedule_ticketing

        schedule_ticketing(db, booking)

    return {"status": payment.status, "booking_reference": booking.public_reference}
