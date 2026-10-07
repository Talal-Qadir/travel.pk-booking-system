from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.requests import HoldCreate
from app.services.auth import require_partner_scope
from app.services.holds import create_hold

router = APIRouter()


@router.post("/holds")
def create_booking_hold(
    request: Request,
    payload: HoldCreate,
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    require_partner_scope(db, authorization, "holds:create")
    return create_hold(db, payload.fare_id, payload.customer_name or "Guest")
