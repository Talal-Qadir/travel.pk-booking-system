import threading


def test_last_seat_is_reserved_by_one_request_only(client, partner_headers):
    fare_id = 4
    from app.db.database import SessionLocal
    from app.db.models import Fare

    db = SessionLocal()
    try:
        fare = db.query(Fare).filter(Fare.id == fare_id).one()
        fare.seats_left = 1
        db.commit()
    finally:
        db.close()

    results = []

    def attempt():
        response = client.post(
            "/holds",
            json={"fare_id": fare_id, "customer_name": "Concurrent Buyer"},
            headers=partner_headers,
        )
        results.append(response.status_code)

    t1 = threading.Thread(target=attempt)
    t2 = threading.Thread(target=attempt)
    t1.start(); t2.start(); t1.join(); t2.join()

    assert results.count(200) == 1
    assert results.count(409) == 1

    fare_response = client.get("/fares", headers=partner_headers)
    fare = next(item for item in fare_response.json() if item["id"] == fare_id)
    assert fare["seats_left"] == 0
