"""
api/events.py
--------------
HTTP routes for events. This file should stay "thin" — it just:
1. Receives the HTTP request
2. Calls the service layer to do the real work
3. Returns an HTTP response (or raises an HTTPException for errors)

APIRouter lets us define these routes in their own file and then plug them
into the main FastAPI app (see app/main.py) with app.include_router(...).
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.event import EventCreate, EventResponse, EventCreateResponse
from app.services import event_service

router = APIRouter()


@router.post("/events", response_model=EventCreateResponse, status_code=201)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """
    Receive a new event from Person 3's event engine.

    Depends(get_db) is FastAPI's dependency injection: it calls get_db()
    (from database.py), grabs a fresh database session, hands it to us as
    `db`, and automatically closes it after this function finishes.

    `event: EventCreate` means FastAPI will:
      - parse the incoming JSON body
      - validate every field against EventCreate's rules
      - reject the request with a 422 error automatically if validation fails
    By the time we're inside this function, `event` is guaranteed valid.
    """

    # Check for duplicate event_id before inserting.
    existing = event_service.get_event_by_event_id(db, event.event_id)
    if existing:
        raise HTTPException(status_code=409, detail="Event ID already exists")

    event_service.create_event(db, event)

    return EventCreateResponse(success=True, event_id=event.event_id)


@router.get("/events", response_model=List[EventResponse])
def list_events(
    event_type: Optional[str] = None,
    bus_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Return stored events, newest first.

    event_type and bus_id are OPTIONAL query parameters, e.g.:
      GET /events
      GET /events?event_type=POTHOLE
      GET /events?bus_id=BUS-001
      GET /events?event_type=POTHOLE&bus_id=BUS-001

    FastAPI automatically reads these from the URL's query string because
    they're plain function parameters with default value None.
    """
    events = event_service.get_events(db, event_type=event_type, bus_id=bus_id)
    return events


@router.get("/events/{event_id}", response_model=EventResponse)
def get_single_event(event_id: str, db: Session = Depends(get_db)):
    """
    Return one event by its event_id, e.g. GET /events/EVT-0001.

    {event_id} in the route path becomes the `event_id` function parameter.
    """
    event = event_service.get_event_by_event_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
