"""
database/seed.py
-----------------
Populates the `buses` table with a handful of starter buses so /buses and
/traffic have realistic-looking data to show even before Person 3's event
engine sends anything real.

This runs automatically once, on app startup (see app/main.py), and only
inserts buses if the table is currently empty — so restarting the server
doesn't create duplicates.
"""

from sqlalchemy.orm import Session
from app.models.bus import Bus

SEED_BUSES = [
    {
        "bus_id": "BUS-001",
        "route_name": "Chennai Central - Tambaram",
        "status": "ACTIVE",
        "last_latitude": 13.0827,
        "last_longitude": 80.2707,
    },
    {
        "bus_id": "BUS-002",
        "route_name": "T Nagar - Velachery",
        "status": "ACTIVE",
        "last_latitude": 13.0418,
        "last_longitude": 80.2341,
    },
    {
        "bus_id": "BUS-003",
        "route_name": "Adyar - Anna Nagar",
        "status": "ACTIVE",
        "last_latitude": 13.0012,
        "last_longitude": 80.2565,
    },
    {
        "bus_id": "BUS-004",
        "route_name": "Guindy - Sholinganallur",
        "status": "ACTIVE",
        "last_latitude": 13.0100,
        "last_longitude": 80.2206,
    },
    {
        "bus_id": "BUS-005",
        "route_name": "Egmore - Porur",
        "status": "INACTIVE",
        "last_latitude": 13.0778,
        "last_longitude": 80.1957,
    },
]


def seed_buses(db: Session):
    """Insert seed buses only if the buses table is currently empty."""
    existing_count = db.query(Bus).count()
    if existing_count > 0:
        return  # already seeded, don't insert duplicates

    for bus_data in SEED_BUSES:
        db.add(Bus(**bus_data))

    db.commit()
