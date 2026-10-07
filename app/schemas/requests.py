from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HoldCreate(BaseModel):
    fare_id: int
    customer_name: str | None = Field(default=None, max_length=128)


class PaymentCreate(BaseModel):
    booking_reference: str
    amount_paisa: int | None = Field(default=None, ge=0)

    model_config = {"extra": "ignore"}


class WebhookEventPayload(BaseModel):
    event_id: str
    psp_reference: str | None = None
    payment_id: int | None = None
    status: str | None = None

    model_config = {"extra": "ignore"}


class JsonBodyEnvelope(BaseModel):
    payload: dict[str, Any]
