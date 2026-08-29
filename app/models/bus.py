"""
models/bus.py
--------------
Defines the BUSES TABLE. This is a small, simple table that stores
basic info about each bus in our fleet — mainly so /buses and /traffic
have something realistic to return.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database.database import Base


class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True)
    bus_id = Column(String, unique=True, index=True, nullable=False)
    route_name = Column(String, nullable=False)

    # status examples: ACTIVE, INACTIVE, MAINTENANCE
    status = Column(String, default="ACTIVE")

    last_latitude = Column(Float, nullable=False)
    last_longitude = Column(Float, nullable=False)

    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
