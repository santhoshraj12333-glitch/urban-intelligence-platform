"""
schemas/bus.py
---------------
Pydantic schemas for BUSES and the TRAFFIC summary endpoint.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BusResponse(BaseModel):
    """Shape of a single bus returned by GET /buses."""

    model_config = ConfigDict(from_attributes=True)

    bus_id: str
    route_name: str
    status: str
    latitude: float  # note: renamed from last_latitude for a cleaner API response
    longitude: float
    last_updated: Optional[datetime] = None


class TrafficResponse(BaseModel):
    """Shape of the aggregated traffic summary returned by GET /traffic."""

    total_vehicles: int
    cars: int
    motorcycles: int
    buses: int
    trucks: int
    traffic_level: str
