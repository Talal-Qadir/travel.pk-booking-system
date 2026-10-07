from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from app.core.config import PSP_SECRET
from app.db.database import SessionLocal
from app.db.models import Booking, Payment
from app.services.webhooks import process_psp_webhook


def build_psp_payload(payment: Payment, booking: Booking) -> dict[str, Any]:
    return {
        "event_id": f"evt-{uuid.uuid4()}",
        "psp_reference": f"psp-{payment.id}-{uuid.uuid4().hex[:8]}",
        "booking_reference": booking.public_reference,
        "amount_paisa": payment.amount_paisa,
        "status": "paid",
    }


def trigger_psp_webhook(payment_id: int) -> dict[str, Any]:
    db = SessionLocal()
    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if payment is None:
            return {"status": "ignored"}
        booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
        if booking is None:
            return {"status": "ignored"}

        payload = build_psp_payload(payment, booking)
        timestamp = str(int(datetime.now(timezone.utc).timestamp()))
        body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        signature = hmac.new(PSP_SECRET.encode("utf-8"), f"{timestamp}.{body.decode('utf-8')}".encode("utf-8"), hashlib.sha256).hexdigest()
        payment.psp_reference = payload["psp_reference"]
        db.commit()
        result = process_psp_webhook(db, payload, timestamp, signature)
        return result
    finally:
        db.close()
