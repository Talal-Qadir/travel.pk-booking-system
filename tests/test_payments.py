from datetime import datetime, timedelta, timezone

from app.db.database import SessionLocal


def test_missing_idempotency_key_is_rejected(client, partner_headers):
    response = client.post(
        "/payments",
        json={"booking_reference": "TPK-000001"},
        headers=partner_headers,
    )
    assert response.status_code in (400, 422)


def test_successful_payment_creation(client, partner_headers):
    response = client.post(
        "/holds",
        json={"fare_id": 1, "customer_name": "Payee"},
        headers=partner_headers,
    )
    booking_ref = response.json()["booking_reference"]
    payment = client.post(
        "/payments",
        json={"booking_reference": booking_ref, "amount_paisa": 10000},
        headers={
            **partner_headers,
            "Idempotency-Key": "pay-1",
        },
    )
    assert payment.status_code == 200, payment.text
    assert payment.json()["status"] in {"PENDING", "SUCCEEDED"}


def test_reused_key_same_body_is_idempotent(client, partner_headers):
    response = client.post(
        "/holds",
        json={"fare_id": 2, "customer_name": "Idempotent"},
        headers=partner_headers,
    )
    booking_ref = response.json()["booking_reference"]
    headers = {**partner_headers, "Idempotency-Key": "pay-repeat"}
    first = client.post("/payments", json={"booking_reference": booking_ref}, headers=headers)
    second = client.post("/payments", json={"booking_reference": booking_ref}, headers=headers)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()


def test_reused_key_with_different_body_is_conflict(client, partner_headers):
    response = client.post(
        "/holds",
        json={"fare_id": 3, "customer_name": "Conflict"},
        headers=partner_headers,
    )
    booking_ref = response.json()["booking_reference"]
    headers = {**partner_headers, "Idempotency-Key": "pay-diff"}
    first = client.post("/payments", json={"booking_reference": booking_ref}, headers=headers)
    second = client.post("/payments", json={"booking_reference": booking_ref, "amount_paisa": 999}, headers=headers)
    assert first.status_code == 200
    assert second.status_code == 409


def test_expired_hold_payment_is_rejected(client, partner_headers):
    response = client.post(
        "/holds",
        json={"fare_id": 2, "customer_name": "Expired"},
        headers=partner_headers,
    )
    booking_ref = response.json()["booking_reference"]

    db = SessionLocal()
    try:
        from app.db.models import Booking
        booking = db.query(Booking).filter(Booking.public_reference == booking_ref).one()
        booking.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        booking.status = "HELD"
        db.commit()
        from app.services.expiry import expire_booking_if_needed
        expire_booking_if_needed(db, booking)
    finally:
        db.close()

    response = client.post(
        "/payments",
        json={"booking_reference": booking_ref},
        headers={**partner_headers, "Idempotency-Key": "expired-pay"},
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "BOOKING_NOT_ELIGIBLE"
