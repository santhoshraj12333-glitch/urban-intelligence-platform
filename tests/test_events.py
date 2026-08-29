"""
tests/test_events.py
---------------------
Tests for POST /events, GET /events, GET /events/{event_id}.

Run with:  pytest tests/test_events.py -v
"""

SAMPLE_EVENT = {
    "event_id": "EVT-0001",
    "bus_id": "BUS-001",
    "camera_id": "FRONT-01",
    "event_type": "POTHOLE",
    "confidence": 0.92,
    "timestamp": "2026-08-26T10:32:14.630",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "frame_id": 1420,
    "evidence_path": "events/EVT-0001.jpg",
}


def test_create_event_success(client):
    response = client.post("/events", json=SAMPLE_EVENT)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["event_id"] == "EVT-0001"


def test_create_duplicate_event_returns_409(client):
    client.post("/events", json=SAMPLE_EVENT)
    response = client.post("/events", json=SAMPLE_EVENT)
    assert response.status_code == 409
    assert response.json()["detail"] == "Event ID already exists"


def test_create_event_invalid_confidence(client):
    bad_event = dict(SAMPLE_EVENT, event_id="EVT-0002", confidence=1.5)
    response = client.post("/events", json=bad_event)
    assert response.status_code == 422  # Pydantic validation error


def test_create_event_invalid_latitude(client):
    bad_event = dict(SAMPLE_EVENT, event_id="EVT-0003", latitude=999)
    response = client.post("/events", json=bad_event)
    assert response.status_code == 422


def test_get_events_returns_created_event(client):
    client.post("/events", json=SAMPLE_EVENT)
    response = client.get("/events")
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 1
    assert events[0]["event_id"] == "EVT-0001"


def test_get_events_filter_by_type(client):
    client.post("/events", json=SAMPLE_EVENT)
    response = client.get("/events?event_type=POTHOLE")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response_empty = client.get("/events?event_type=TRAFFIC")
    assert response_empty.status_code == 200
    assert len(response_empty.json()) == 0


def test_get_single_event_found(client):
    client.post("/events", json=SAMPLE_EVENT)
    response = client.get("/events/EVT-0001")
    assert response.status_code == 200
    assert response.json()["bus_id"] == "BUS-001"


def test_get_single_event_not_found(client):
    response = client.get("/events/EVT-9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"
