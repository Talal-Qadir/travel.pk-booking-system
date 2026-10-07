from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.errors import api_error
from app.db.models import Booking, CustomerToken, PartnerAPIKey


def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def normalize_bearer_token(token: Optional[str]) -> str:
    if not token:
        raise api_error(401, "AUTH_REQUIRED", "Authentication required.")

    normalized = token.strip()
    if normalized.lower().startswith("bearer "):
        normalized = normalized[7:].strip()

    if not normalized:
        raise api_error(401, "AUTH_REQUIRED", "Authentication required.")

    return normalized


def generate_customer_token() -> str:
    return secrets.token_urlsafe(32)


def generate_booking_reference() -> str:
    import random

    return f"TPK-{random.randint(100000, 999999):06d}"


def get_partner_by_token(db: Session, token: Optional[str]) -> PartnerAPIKey:
    raw_token = normalize_bearer_token(token)

    partner = db.query(PartnerAPIKey).filter(PartnerAPIKey.key_id == raw_token, PartnerAPIKey.active.is_(True)).first()
    if partner is None:
        partner = db.query(PartnerAPIKey).filter(PartnerAPIKey.key_hash == hash_secret(raw_token), PartnerAPIKey.active.is_(True)).first()

    if partner is None:
        raise api_error(401, "INVALID_PARTNER_KEY", "Invalid partner credentials.")
    return partner


def require_partner_scope(db: Session, token: Optional[str], required_scope: str) -> PartnerAPIKey:
    partner = get_partner_by_token(db, token)
    granted = set(partner.scopes.split())
    if required_scope not in granted:
        raise api_error(403, "INSUFFICIENT_SCOPE", "Missing required partner scope.")
    return partner


def customer_has_access_to_booking(db: Session, token_value: str, booking_reference: str) -> Booking:
    token_hash = hash_secret(token_value)
    customer_token = db.query(CustomerToken).filter(CustomerToken.token_hash == token_hash).first()
    if customer_token is None:
        raise api_error(401, "INVALID_CUSTOMER_TOKEN", "Invalid or expired customer token.")

    expires_at = customer_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise api_error(401, "INVALID_CUSTOMER_TOKEN", "Invalid or expired customer token.")

    booking = db.query(Booking).filter(Booking.id == customer_token.booking_id).first()
    if booking is None:
        raise api_error(404, "BOOKING_NOT_FOUND", "Booking not found.")

    if booking.public_reference != booking_reference:
        raise api_error(404, "BOOKING_NOT_FOUND", "Booking not found.")

    return booking