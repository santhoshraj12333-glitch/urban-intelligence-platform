"""
services/traffic_service.py
----------------------------
Service layer for the /traffic endpoint.

MVP NOTE: Real per-vehicle-type counts (cars/motorcycles/trucks) would come
from Person 1's vehicle detection module once fully integrated. For the
5-day MVP, we use simple seeded/mock numbers, as the spec allows.
This keeps Day 1-2 backend work fully independent of Person 1's AI module,
so integration later (Day 3-4) doesn't block anyone.

FUTURE / PRODUCTION: this function would instead query the events table,
count VEHICLE-type events grouped by a "vehicle_subtype" field, and compute
traffic_level from real density over a rolling time window.
"""

from sqlalchemy.orm import Session
from app.models.event import Event


def get_traffic_summary(db: Session) -> dict:
    """
    Returns an aggregated traffic snapshot.

    We do a lightweight real count of how many VEHICLE-type events exist
    in the database (so the number isn't 100% fake), then split that
    total across vehicle types using fixed, realistic-looking proportions.
    This is intentionally simple — see MVP NOTE above.
    """
    vehicle_event_count = (
        db.query(Event).filter(Event.event_type == "VEHICLE").count()
    )

    # Fallback so the dashboard never looks empty before real events arrive.
    total_vehicles = vehicle_event_count if vehicle_event_count > 0 else 148

    cars = round(total_vehicles * 0.54)
    motorcycles = round(total_vehicles * 0.30)
    buses = round(total_vehicles * 0.05)
    trucks = total_vehicles - cars - motorcycles - buses  # remainder, avoids rounding drift

    if total_vehicles >= 120:
        traffic_level = "HIGH"
    elif total_vehicles >= 60:
        traffic_level = "MEDIUM"
    else:
        traffic_level = "LOW"

    return {
        "total_vehicles": total_vehicles,
        "cars": cars,
        "motorcycles": motorcycles,
        "buses": buses,
        "trucks": trucks,
        "traffic_level": traffic_level,
    }
