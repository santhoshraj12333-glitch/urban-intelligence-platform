"""
api/buses.py
------------
HTTP route for GET /buses.
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.bus import Bus
from app.schemas.bus import BusResponse

router = APIRouter()


@router.get("/buses", response_model=List[BusResponse])
def list_buses(db: Session = Depends(get_db)):
    """
    Return all buses in the fleet.

    This is a simple query with no filters — for the MVP, the whole
    fleet is small enough (5 seeded buses) that we just return everything.

    Note: BusResponse expects fields named `latitude`/`longitude`, but our
    database model stores `last_latitude`/`last_longitude`. Because
    BusResponse.model_config has from_attributes=True, Pydantic normally
    reads matching attribute names automatically — since the names differ
    here, we build the response dict manually below.
    """
    buses = db.query(Bus).all()

    return [
        BusResponse(
            bus_id=bus.bus_id,
            route_name=bus.route_name,
            status=bus.status,
            latitude=bus.last_latitude,
            longitude=bus.last_longitude,
            last_updated=bus.last_updated,
        )
        for bus in buses
    ]
