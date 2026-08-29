"""
services/event_service.py
--------------------------
This is the SERVICE LAYER for events.

Why have a separate service layer instead of putting database logic
directly inside app/api/events.py?

- It keeps the API route functions short and focused on "handle the HTTP request".
- It keeps the database logic reusable and easy to test on its own.
- If we ever change how events are stored, we only edit this file —
  the routes in api/events.py don't need to change.

Every function here takes a SQLAlchemy `db` session (passed in from the route)
and does one clear job.
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.event import Event
from app.schemas.event import EventCreate


def get_event_by_event_id(db: Session, event_id: str) -> Optional[Event]:
    """Look up a single event by its unique event_id string (e.g. 'EVT-0001')."""
    return db.query(Event).filter(Event.event_id == event_id).first()


def create_event(db: Session, event_data: EventCreate) -> Event:
    """
    Save a new event to the database.

    event_data has ALREADY been validated by Pydantic (EventCreate) by the
    time it gets here — we don't need to re-check confidence ranges, etc.
    Duplicate-id checking happens in the route BEFORE this is called.
    """
    db_event = Event(
        event_id=event_data.event_id,
        bus_id=event_data.bus_id,
        camera_id=event_data.camera_id,
        event_type=event_data.event_type,
        confidence=event_data.confidence,
        timestamp=event_data.timestamp,
        latitude=event_data.latitude,
        longitude=event_data.longitude,
        frame_id=event_data.frame_id,
        evidence_path=event_data.evidence_path,
    )

    db.add(db_event)      # stage the new row
    db.commit()           # write it to the SQLite file
    db.refresh(db_event)  # reload it so db_event.id and created_at are filled in

    return db_event


def get_events(
    db: Session,
    event_type: Optional[str] = None,
    bus_id: Optional[str] = None,
    limit: int = 100,
):
    """
    Fetch stored events, optionally filtered by event_type and/or bus_id.
    Results are sorted newest-first (by timestamp) since that's usually
    most useful for a live dashboard.
    """
    query = db.query(Event)

    if event_type:
        query = query.filter(Event.event_type == event_type)

    if bus_id:
        query = query.filter(Event.bus_id == bus_id)

    query = query.order_by(desc(Event.timestamp)).limit(limit)

    return query.all()
