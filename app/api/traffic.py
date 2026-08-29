"""
api/traffic.py
---------------
HTTP route for GET /traffic.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.bus import TrafficResponse
from app.services import traffic_service

router = APIRouter()


@router.get("/traffic", response_model=TrafficResponse)
def get_traffic(db: Session = Depends(get_db)):
    """Return an aggregated traffic snapshot for the dashboard."""
    summary = traffic_service.get_traffic_summary(db)
    return summary
