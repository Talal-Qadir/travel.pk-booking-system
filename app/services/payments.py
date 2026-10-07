from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import Booking, Payment
from app.services.expiry import expire_booking_if_needed


def _stable_fingerprint(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def create_payment(db: Session, partner_key_id: str, booking_reference: str, request_body: dict[str, Any], idempotency_key: str) -> dict[str, Any]:
    expire_booking_if_needed(db)
    booking = db.query(Booking).filter(Booking.public_reference == booking_reference).first()
    if booking is None:
        raise HTTPException(status_code=404, detail={"error": {"code": "BOOKING_NOT_FOUND", "message": "Booking not found."}})

    if not idempotency_key:
        raise HTTPException(status_code=400, detail={"error": {"code": "MISSING_IDEMPOTENCY_KEY", "message": "Idempotency-Key header is required."}})

    request_fingerprint = _stable_fingerprint(request_body)
    existing = db.query(Payment).filter(Payment.partner_key_id == partner_key_id, Payment.idempotency_key == idempotency_key).first()
    if existing is not None:
        if existing.request_fingerprint != request_fingerprint:
            raise HTTPException(status_code=409, detail={"error": {"code": "IDEMPOTENCY_KEY_REUSED", "message": "The idempotency key was already used with a different request."}})
        return {
            "_created": False,
            "id": existing.id,
            "booking_reference": booking_reference,
            "status": existing.status,
            "amount_paisa": existing.amount_paisa,
            "currency": existing.currency,
        }

    if booking.status in {"EXPIRED", "CANCELLED", "REFUNDED", "FAILED", "TICKETED"}:
        raise HTTPException(status_code=409, detail={"error": {"code": "BOOKING_NOT_ELIGIBLE", "message": "Booking is not eligible for payment."}})

    payment = Payment(
        booking_id=booking.id,
        partner_key_id=partner_key_id,
        idempotency_key=idempotency_key,
        request_fingerprint=request_fingerprint,
        amount_paisa=booking.total_price_paisa,
        currency="PKR",
        status="PENDING",
    )
    db.add(payment)
    db.flush()
    booking.status = "PAYMENT_PENDING"
    booking.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "_created": True,
        "id": payment.id,
        "booking_reference": booking_reference,
        "status": payment.status,
        "amount_paisa": payment.amount_paisa,
        "currency": payment.currency,
    }
