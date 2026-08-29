"""
schemas/event.py
-----------------
Pydantic schemas for EVENTS.

These are different from app/models/event.py:
- models/event.py    -> describes a row in the SQLite table (SQLAlchemy)
- schemas/event.py   -> describes and VALIDATES the JSON coming in/out of the API (Pydantic)

When a POST /events request arrives, FastAPI uses EventCreate to check that
every field is present and correctly typed/ranged BEFORE our code ever touches it.
If validation fails, FastAPI automatically returns a clean 422 error — we don't
have to write that error-handling ourselves.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class EventCreate(BaseModel):
    """
    Shape of the JSON that Person 3's event engine sends to POST /events.
    Field names match the shared contract EXACTLY — do not rename these.
    """

    event_id: str = Field(..., min_length=1)
    bus_id: str = Field(..., min_length=1)
    camera_id: str = Field(..., min_length=1)
    event_type: str = Field(..., min_length=1)

    # ge = "greater than or equal", le = "less than or equal".
    # Pydantic will auto-reject 1.5 or -0.1 before our code runs.
    confidence: float = Field(..., ge=0.0, le=1.0)

    timestamp: datetime

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

    frame_id: int = Field(..., ge=0)

    evidence_path: Optional[str] = None


class EventResponse(BaseModel):
    """
    Shape of an event when we SEND it back out (e.g. in GET /events).
    Includes the internal database id and created_at, which callers
    might find useful but which are never supplied by the caller.
    """

    model_config = ConfigDict(from_attributes=True)
    # from_attributes=True lets us pass a SQLAlchemy Event object directly
    # into this schema (e.g. EventResponse.model_validate(db_event)) and have
    # Pydantic read its attributes automatically, instead of manually
    # building a dict field by field.

    id: int
    event_id: str
    bus_id: str
    camera_id: str
    event_type: str
    confidence: float
    timestamp: datetime
    latitude: float
    longitude: float
    frame_id: int
    evidence_path: Optional[str] = None
    created_at: Optional[datetime] = None


class EventCreateResponse(BaseModel):
    """Simple confirmation returned after successfully creating an event."""

    success: bool
    event_id: str
