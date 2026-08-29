"""
tests/test_traffic.py
----------------------
Tests for GET /traffic.
"""


def test_traffic_returns_default_summary(client):
    response = client.get("/traffic")
    assert response.status_code == 200
    data = response.json()
    assert data["total_vehicles"] == 148  # fallback mock value when no VEHICLE events exist
    assert data["traffic_level"] == "HIGH"
    assert "cars" in data
    assert "motorcycles" in data
    assert "buses" in data
    assert "trucks" in data


def test_traffic_reflects_real_vehicle_events(client):
    vehicle_event = {
        "event_id": "EVT-VEH-1",
        "bus_id": "BUS-001",
        "camera_id": "FRONT-01",
        "event_type": "VEHICLE",
        "confidence": 0.8,
        "timestamp": "2026-08-26T10:32:14.630",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "frame_id": 1,
        "evidence_path": None,
    }
    client.post("/events", json=vehicle_event)

    response = client.get("/traffic")
    data = response.json()
    # 1 real VEHICLE event now exists, so the summary reflects that count
    # instead of the 148 mock fallback (fallback only applies when count is 0)
    assert data["total_vehicles"] == 1
