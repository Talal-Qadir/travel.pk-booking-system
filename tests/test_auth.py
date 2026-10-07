def test_missing_partner_key_is_rejected(client):
    response = client.get("/fares")
    assert response.status_code == 401


def test_invalid_partner_key_is_rejected(client):
    response = client.get("/fares", headers={"Authorization": "bad-key"})
    assert response.status_code == 401


def test_insufficient_scope_is_rejected(client, partner_headers):
    headers = {**partner_headers, "Authorization": "partner-readonly"}
    response = client.get("/fares", headers=headers)
    assert response.status_code == 403


def test_valid_partner_scope_is_allowed(client, partner_headers):
    response = client.get("/fares", headers=partner_headers)
    assert response.status_code == 200


def test_customer_token_only_accesses_own_booking(client, partner_headers):
    first_hold = client.post(
        "/holds",
        json={"fare_id": 1, "customer_name": "Alice"},
        headers=partner_headers,
    )
    assert first_hold.status_code == 200, first_hold.text
    first_booking = first_hold.json()["booking_reference"]
    first_token = first_hold.json()["customer_token"]

    second_hold = client.post(
        "/holds",
        json={"fare_id": 2, "customer_name": "Bob"},
        headers=partner_headers,
    )
    assert second_hold.status_code == 200, second_hold.text
    second_booking = second_hold.json()["booking_reference"]

    own = client.get(f"/bookings/{first_booking}", headers={"Authorization": f"Bearer {first_token}"})
    assert own.status_code == 200

    other = client.get(f"/bookings/{second_booking}", headers={"Authorization": f"Bearer {first_token}"})
    assert other.status_code == 404
