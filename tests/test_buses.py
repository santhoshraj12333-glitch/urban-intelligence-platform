"""
tests/test_buses.py
--------------------
Tests for GET /buses.

Note: the startup seed (app/database/seed.py) only runs on the app's
"startup" event, which TestClient triggers when used as a context manager
(see conftest.py's `with TestClient(app) as test_client:`).
"""


def test_list_buses_returns_seeded_data(client):
    response = client.get("/buses")
    assert response.status_code == 200
    buses = response.json()
    assert len(buses) == 5
    bus_ids = [b["bus_id"] for b in buses]
    assert "BUS-001" in bus_ids


def test_bus_has_expected_fields(client):
    response = client.get("/buses")
    bus = response.json()[0]
    assert "bus_id" in bus
    assert "route_name" in bus
    assert "status" in bus
    assert "latitude" in bus
    assert "longitude" in bus
