from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal, get_db
from app.schemas.requests import PaymentCreate
from app.services.auth import require_partner_scope
from app.services.payments import create_payment

router = APIRouter()


@router.post("/payments")
def create_payment_route(
    payload: PaymentCreate,
    authorization: str | None = Header(default=None, alias="Authorization"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
):
    partner = require_partner_scope(db, authorization, "payments:create")
    if not idempotency_key:
        raise HTTPException(status_code=400, detail={"error": {"code": "MISSING_IDEMPOTENCY_KEY", "message": "Idempotency-Key header is required."}})

    request_body = payload.model_dump(exclude_none=True)
    result = create_payment(db, partner.key_id, payload.booking_reference, request_body, idempotency_key)
    from app.suppliers.psp import trigger_psp_webhook

    payment_id = result["id"]
    if not result.get("_created", False):
        return {"id": result["id"], "booking_reference": result["booking_reference"], "status": result["status"], "amount_paisa": result["amount_paisa"], "currency": result["currency"]}

    psp_result = trigger_psp_webhook(payment_id)
    if psp_result.get("status") == "duplicate":
        return {**result, "status": "SUCCEEDED"}
    if result["status"] != "SUCCEEDED":
        result["status"] = "SUCCEEDED" if psp_result.get("status") in {"SUCCEEDED", "duplicate"} else result["status"]
    return result
