from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Booking, Payment
from app.services.auth import (
    customer_has_access_to_booking,
    get_partner_by_token,
    normalize_bearer_token,
    require_partner_scope,
)
from app.services.booking_views import (
    can_cancel_booking,
    compute_refund_paisa,
    serialize_booking_detail,
    serialize_booking_summary,
)
from app.services.expiry import expire_booking_if_needed

router = APIRouter()


def _resolve_booking_for_read(db: Session, authorization: str, reference: str) -> Booking:
    expire_booking_if_needed(db)
    token = normalize_bearer_token(authorization)
    try:
        partner = get_partner_by_token(db, token)
        if "bookings:read" in set(partner.scopes.split()):
            booking = db.query(Booking).filter(Booking.public_reference == reference).first()
            if booking is None:
                raise HTTPException(
                    status_code=404,
                    detail={"error": {"code": "BOOKING_NOT_FOUND", "message": "Booking not found."}},
                )
            return booking
    except HTTPException as exc:
        if exc.status_code not in (401, 403):
            raise
    return customer_has_access_to_booking(db, token, reference)


@router.get("/bookings")
def list_bookings(
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    require_partner_scope(db, authorization, "bookings:read")
    expire_booking_if_needed(db)
    bookings = db.query(Booking).order_by(Booking.created_at.desc()).limit(500).all()
    return [serialize_booking_summary(db, booking) for booking in bookings]


@router.get("/bookings/{reference}")
def get_booking(
    reference: str,
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    if not authorization:
        raise HTTPException(status_code=401, detail={"error": {"code": "AUTH_REQUIRED", "message": "Authentication required."}})
    booking = _resolve_booking_for_read(db, authorization, reference)
    return serialize_booking_detail(db, booking)


@router.get("/bookings/{reference}/cancellation-preview")
def cancellation_preview(
    reference: str,
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    if not authorization:
        raise HTTPException(status_code=401, detail={"error": {"code": "AUTH_REQUIRED", "message": "Authentication required."}})
    booking = _resolve_booking_for_read(db, authorization, reference)
    if not can_cancel_booking(booking):
        raise HTTPException(
            status_code=409,
            detail={"error": {"code": "NOT_CANCELLABLE", "message": "This booking cannot be cancelled."}},
        )
    from app.db.models import Fare

    fare = db.query(Fare).filter(Fare.id == booking.fare_id).first()
    refund_paisa = compute_refund_paisa(db, booking, fare)
    return {
        "booking_reference": booking.public_reference,
        "refund_paisa": refund_paisa,
        "currency": "PKR",
        "refundable_fare": fare.refundable if fare else False,
    }


@router.post("/bookings/{reference}/cancel")
def cancel_booking(
    reference: str,
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    if not authorization:
        raise HTTPException(status_code=401, detail={"error": {"code": "AUTH_REQUIRED", "message": "Authentication required."}})

    token = normalize_bearer_token(authorization)
    booking: Booking | None = None

    try:
        partner = get_partner_by_token(db, token)
        if "bookings:cancel" in set(partner.scopes.split()):
            booking = db.query(Booking).filter(Booking.public_reference == reference).first()
            if booking is None:
                raise HTTPException(
                    status_code=404,
                    detail={"error": {"code": "BOOKING_NOT_FOUND", "message": "Booking not found."}},
                )
    except HTTPException as exc:
        if exc.status_code not in (401, 403):
            raise

    if booking is None:
        booking = customer_has_access_to_booking(db, token, reference)

    if booking.status == "CANCELLED":
        raise HTTPException(status_code=409, detail={"error": {"code": "ALREADY_CANCELLED", "message": "Booking already cancelled."}})

    if not can_cancel_booking(booking):
        raise HTTPException(
            status_code=409,
            detail={"error": {"code": "NOT_CANCELLABLE", "message": "This booking cannot be cancelled."}},
        )

    from app.db.models import Fare

    fare = db.query(Fare).filter(Fare.id == booking.fare_id).first()
    refund_paisa = compute_refund_paisa(db, booking, fare)
    payment = (
        db.query(Payment).filter(Payment.booking_id == booking.id).order_by(Payment.created_at.desc()).first()
    )

    if booking.status in {"HELD", "PAYMENT_PENDING"}:
        fare = db.query(Fare).filter(Fare.id == booking.fare_id).first()
        if fare is not None:
            fare.seats_left += 1

    booking.status = "REFUNDED" if refund_paisa > 0 else "CANCELLED"
    booking.updated_at = datetime.now(timezone.utc)
    refund_status = "NONE"
    if payment is not None and refund_paisa > 0:
        payment.status = "REFUNDED"
        payment.updated_at = datetime.now(timezone.utc)
        refund_status = "PENDING" if payment.status == "REFUNDED" else "NONE"

    db.commit()
    return {
        "booking_reference": booking.public_reference,
        "status": booking.status,
        "refund_paisa": refund_paisa,
        "refund_status": refund_status,
    }
