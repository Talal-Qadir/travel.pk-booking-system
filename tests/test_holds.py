from datetime import datetime, timedelta, timezone

from app.db.database import SessionLocal
from app.db.models import Booking, Fare
from app.services.expiry import expire_booking_if_needed


def test_successful_hold(client, partner_headers):
    response = client.post(
        "/holds",
        json={"fare_id": 1, "customer_name": "Alice"},
        headers=partner_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["booking_reference"].startswith("TPK-")
    assert payload["price_snapshot_paisa"] > 0
    assert "customer_token" in payload


def test_hold_decrements_inventory_and_snaps_price(client, partner_headers):
    fare_id = 1
    response = client.get("/fares", headers=partner_headers)
    before = next(item for item in response.json() if item["id"] == fare_id)
    hold = client.post(
        "/holds",
        json={"fare_id": fare_id, "customer_name": "Bob"},
        headers=partner_headers,
    )
    assert hold.status_code == 200, hold.text
    after = client.get("/fares", headers=partner_headers)
    after_fare = next(item for item in after.json() if item["id"] == fare_id)
    assert before["seats_left"] == after_fare["seats_left"] + 1
    assert hold.json()["price_snapshot_paisa"] == before["total_price_paisa"]


def test_no_seats_returns_conflict(client, partner_headers):
    fare_id = 3
    response = None
    for _ in range(30):
        response = client.post(
            "/holds",
            json={"fare_id": fare_id, "customer_name": "Visitor"},
            headers=partner_headers,
        )
        if response.status_code == 409:
            break
    assert response is not None and response.status_code == 409


def test_expired_hold_releases_seat(client, partner_headers):
    response = client.post(
        "/holds",
        json={"fare_id": 2, "customer_name": "Charlie"},
        headers=partner_headers,
    )
    assert response.status_code == 200, response.text
    booking_ref = response.json()["booking_reference"]

    db = SessionLocal()
    try:
        booking = db.query(Booking).filter(Booking.public_reference == booking_ref).one()
        booking.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        booking.status = "HELD"
        fare = db.query(Fare).filter(Fare.id == booking.fare_id).one()
        before_seats = fare.seats_left
        db.commit()
        expire_booking_if_needed(db, booking)
        db.refresh(booking)
        db.refresh(fare)
    finally:
        db.close()

    assert booking.status == "EXPIRED"
    assert fare.seats_left == before_seats + 1


def test_cancel_refundable_and_non_refundable_bookings(client, partner_headers):
    refundable = client.post(
        "/holds",
        json={"fare_id": 2, "customer_name": "Refundable"},
        headers=partner_headers,
    )
    non_refundable = client.post(
        "/holds",
        json={"fare_id": 1, "customer_name": "NonRefundable"},
        headers=partner_headers,
    )

    refundable_response = client.post(
        f"/bookings/{refundable.json()['booking_reference']}/cancel",
        headers=partner_headers,
    )
    non_refundable_response = client.post(
        f"/bookings/{non_refundable.json()['booking_reference']}/cancel",
        headers=partner_headers,
    )

    assert refundable_response.status_code == 200
    assert refundable_response.json()["status"] == "CANCELLED"
    assert non_refundable_response.status_code == 200
    assert non_refundable_response.json()["status"] == "CANCELLED"


def test_ticketing_webhook_characterization(client, partner_headers):
    hold = client.post(
        "/holds",
        json={"fare_id": 2, "customer_name": "Webhook Buyer"},
        headers=partner_headers,
    )
    booking_ref = hold.json()["booking_reference"]

    payment = client.post(
        "/payments",
        json={"booking_reference": booking_ref},
        headers={**partner_headers, "Idempotency-Key": "char-payment"},
    )
    assert payment.status_code == 200, payment.text
    payment_id = payment.json()["id"]

    from app.suppliers.psp import trigger_psp_webhook

    webhook_result = trigger_psp_webhook(payment_id)
    assert webhook_result["status"] in {"SUCCEEDED", "duplicate"}

    booking = client.get(f"/bookings/{booking_ref}", headers=partner_headers)
    assert booking.status_code == 200
    assert booking.json()["status"] in {"PAID", "TICKETED"}

    db = SessionLocal()
    try:
        booking_row = db.query(Booking).filter(Booking.public_reference == booking_ref).one()
        booking_row.status = "PAID"
        db.commit()

        from app.services.ticketing import schedule_ticketing

        schedule_ticketing(db, booking_row)
        db.refresh(booking_row)
    finally:
        db.close()

    assert booking_row.status in {"TICKETING", "TICKETED", "PAID"}
