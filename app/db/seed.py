from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.db.models import Fare, PartnerAPIKey
from app.db.session import SessionLocal
from app.services.auth import hash_secret


def seed_database() -> None:
    db = SessionLocal()
    try:
        existing_fares = db.query(Fare).count()
        if existing_fares == 0:
            now = datetime.now(timezone.utc)
            fares = [
                Fare(
                    id=1,
                    origin="LHE",
                    destination="KHI",
                    airline="PIA",
                    flight_number="PK-201",
                    departure_time=now + timedelta(days=3),
                    arrival_time=now + timedelta(days=3, hours=1),
                    base_price_paisa=8425050,
                    taxes_paisa=200000,
                    total_price_paisa=8625050,
                    seats_left=6,
                    fare_rules="Economy Saver. Bags included.",
                    refundable=False,
                    active=True,
                ),
                Fare(
                    id=2,
                    origin="KHI",
                    destination="DXB",
                    airline="Emirates",
                    flight_number="EK-201",
                    departure_time=now + timedelta(days=4),
                    arrival_time=now + timedelta(days=4, hours=3),
                    base_price_paisa=12000000,
                    taxes_paisa=350000,
                    total_price_paisa=12350000,
                    seats_left=12,
                    fare_rules="Flexible fare with checked baggage.",
                    refundable=True,
                    active=True,
                ),
                Fare(
                    id=3,
                    origin="ISB",
                    destination="JED",
                    airline="Saudi",
                    flight_number="SV-501",
                    departure_time=now + timedelta(days=2),
                    arrival_time=now + timedelta(days=2, hours=4),
                    base_price_paisa=16500000,
                    taxes_paisa=450000,
                    total_price_paisa=16950000,
                    seats_left=1,
                    fare_rules="Limited change option. Non-refundable.",
                    refundable=False,
                    active=True,
                ),
                Fare(
                    id=4,
                    origin="LHE",
                    destination="KHI",
                    airline="AirBlue",
                    flight_number="AB-112",
                    departure_time=now + timedelta(days=5),
                    arrival_time=now + timedelta(days=5, hours=1),
                    base_price_paisa=9500000,
                    taxes_paisa=200000,
                    total_price_paisa=9700000,
                    seats_left=4,
                    fare_rules="Standard fare; refund permitted within 24h.",
                    refundable=True,
                    active=True,
                ),
                Fare(
                    id=5,
                    origin="KHI",
                    destination="DXB",
                    airline="Qatar",
                    flight_number="QR-310",
                    departure_time=now + timedelta(days=6),
                    arrival_time=now + timedelta(days=6, hours=3),
                    base_price_paisa=14500000,
                    taxes_paisa=500000,
                    total_price_paisa=15000000,
                    seats_left=8,
                    fare_rules="Refundable with fare rules.",
                    refundable=True,
                    active=True,
                ),
                Fare(
                    id=6,
                    origin="ISB",
                    destination="JED",
                    airline="FlyJinnah",
                    flight_number="FJ-223",
                    departure_time=now + timedelta(days=8),
                    arrival_time=now + timedelta(days=8, hours=4),
                    base_price_paisa=17800000,
                    taxes_paisa=600000,
                    total_price_paisa=18400000,
                    seats_left=7,
                    fare_rules="Tickets are final; no refund after purchase.",
                    refundable=False,
                    active=True,
                ),
            ]
            db.add_all(fares)

        existing_partner_keys = db.query(PartnerAPIKey).count()
        if existing_partner_keys == 0:
            db.add_all(
                [
                    PartnerAPIKey(key_id="partner-admin", key_hash=hash_secret("partner-admin"), scopes="fares:read holds:create payments:create bookings:read bookings:cancel", active=True),
                    PartnerAPIKey(key_id="partner-readonly", key_hash=hash_secret("partner-readonly"), scopes="", active=True),
                ]
            )

        db.commit()
    finally:
        db.close()
