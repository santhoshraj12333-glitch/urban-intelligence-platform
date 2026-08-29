"""
models/event.py
----------------
This file defines the EVENTS TABLE structure using SQLAlchemy.

This is a "model" — it describes what a row in the database looks like.
It is NOT the same as a Pydantic schema (that's for validating incoming
JSON from the API). This file is purely about the database.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database.database import Base


class Event(Base):
    # This tells SQLAlchemy the table should be called "events" in SQLite.
    __tablename__ = "events"

    # Internal auto-incrementing primary key. This is separate from event_id
    # (which comes from Person 3's system) — this "id" is just for the database's
    # own bookkeeping.
    id = Column(Integer, primary_key=True, index=True)

    # event_id must be unique — this is how we detect duplicate events.
    # unique=True makes SQLite reject a second row with the same event_id
    # (we also check for this ourselves in the service layer for a cleaner error).
    event_id = Column(String, unique=True, index=True, nullable=False)

    bus_id = Column(String, index=True, nullable=False)
    camera_id = Column(String, nullable=False)

    # event_type examples: POTHOLE, VEHICLE, TRAFFIC, INCIDENT
    event_type = Column(String, index=True, nullable=False)

    confidence = Column(Float, nullable=False)

    # We store the timestamp the event happened at (comes from Person 3's engine).
    timestamp = Column(DateTime, nullable=False)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    frame_id = Column(Integer, nullable=False)
    evidence_path = Column(String, nullable=True)

    # created_at is set automatically by the database when the row is inserted.
    # This tracks when OUR backend received the event, which can be different
    # from "timestamp" (when the event actually happened on the bus).
    created_at = Column(DateTime(timezone=True), server_default=func.now())
