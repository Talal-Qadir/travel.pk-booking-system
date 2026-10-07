from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.webhooks import process_psp_webhook

router = APIRouter()


@router.post("/webhooks/psp")
async def psp_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_psp_timestamp: str | None = Header(default=None, alias="X-PSP-Timestamp"),
    x_psp_signature: str | None = Header(default=None, alias="X-PSP-Signature"),
):
    raw_body = await request.body()
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON payload") from exc
    return process_psp_webhook(db, payload, x_psp_timestamp or "0", x_psp_signature)
