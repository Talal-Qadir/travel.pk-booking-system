from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.auth import require_partner_scope
from app.services.expiry import expire_booking_if_needed

router = APIRouter()


@router.get("/fares")
def list_fares(
    request: Request,
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    require_partner_scope(db, authorization, "fares:read")
    expire_booking_if_needed(db)
    from app.db.models import Fare

    fares = db.query(Fare).filter(Fare.active.is_(True)).all()
    return [
        {
            "id": fare.id,
            "origin": fare.origin,
            "destination": fare.destination,
            "airline": fare.airline,
            "flight_number": fare.flight_number,
            "departure_time": fare.departure_time.isoformat(),
            "arrival_time": fare.arrival_time.isoformat(),
            "base_price_paisa": fare.base_price_paisa,
            "taxes_paisa": fare.taxes_paisa,
            "total_price_paisa": fare.total_price_paisa,
            "seats_left": fare.seats_left,
            "fare_rules": fare.fare_rules,
            "refundable": fare.refundable,
        }
        for fare in fares
    ]
