from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base, UTCDateTime


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Fare(Base):
    __tablename__ = "fares"
    __table_args__ = (
        CheckConstraint("seats_left >= 0", name="ck_fares_seats_left_nonnegative"),
        CheckConstraint("base_price_paisa >= 0", name="ck_fares_base_price_nonnegative"),
        CheckConstraint("taxes_paisa >= 0", name="ck_fares_taxes_nonnegative"),
        CheckConstraint("total_price_paisa >= 0", name="ck_fares_total_price_nonnegative"),
        CheckConstraint("total_price_paisa = base_price_paisa + taxes_paisa", name="ck_fares_total_matches_components"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    origin: Mapped[str] = mapped_column(String(32), nullable=False)
    destination: Mapped[str] = mapped_column(String(32), nullable=False)
    airline: Mapped[str] = mapped_column(String(64), nullable=False)
    flight_number: Mapped[str] = mapped_column(String(32), nullable=False)
    departure_time: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    arrival_time: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    base_price_paisa: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    taxes_paisa: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_price_paisa: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    seats_left: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fare_rules: Mapped[str] = mapped_column(Text, nullable=True)
    refundable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_reference: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, index=True)
    fare_id: Mapped[int] = mapped_column(ForeignKey("fares.id"), nullable=False)
    customer_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="HELD")
    base_price_paisa: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    taxes_paisa: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_price_paisa: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    expires_at: Mapped[Optional[datetime]] = mapped_column(UTCDateTime(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, onupdate=utcnow)
    pnr: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    ticketed_at: Mapped[Optional[datetime]] = mapped_column(UTCDateTime(), nullable=True)

    fare: Mapped["Fare"] = relationship("Fare")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), nullable=False)
    partner_key_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    request_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    amount_paisa: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="PKR")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    psp_reference: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, onupdate=utcnow)

    __table_args__ = (
        CheckConstraint("amount_paisa >= 0", name="ck_payments_amount_nonnegative"),
        UniqueConstraint("partner_key_id", "idempotency_key", name="uq_payment_partner_idempotency"),
    )


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)


class AirlineTicketRequest(Base):
    __tablename__ = "airline_ticket_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), nullable=False, unique=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    airline_reference: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    pnr: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, onupdate=utcnow)


class PartnerAPIKey(Base):
    __tablename__ = "partner_api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    key_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    scopes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)


class CustomerToken(Base):
    __tablename__ = "customer_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), nullable=False, unique=True)
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
