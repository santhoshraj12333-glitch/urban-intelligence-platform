# Urban Intelligence Platform — Backend

Backend for **SIH26124 — AI-Powered Mobile Urban Intelligence Platform Using Public Transport Fleet** (Bharat Electronics Limited).

Built by **Person 4 — Backend Engineer**.

This is a deliberately simple FastAPI + SQLite backend for a 5-day hackathon MVP. It is **not** meant to be production-grade — see the "MVP vs Future" notes below.

---

## 1. Tech Stack

- Python 3
- FastAPI — web framework
- Pydantic — request/response validation
- SQLAlchemy — talks to the database in Python instead of raw SQL
- SQLite — single-file database, zero setup
- Uvicorn — the server that actually runs FastAPI

No Docker, no auth, no message queues, no cloud database — all of that is future/production-only, not needed for the demo.

---

## 2. Setup

```bash
# 1. Create and activate a virtual environment (recommended but optional)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server (from the backend/ folder)
uvicorn app.main:app --reload
```

The server starts at: **http://localhost:8000**

Interactive API docs (Swagger UI): **http://localhost:8000/docs**

On first run, this automatically:
- creates `urban_intel.db` (the SQLite file) in the `backend/` folder
- creates the `events` and `buses` tables
- seeds 5 starter buses (BUS-001 to BUS-005) with real Chennai coordinates

---

## 3. Project Structure

```
backend/
├── README.md
├── requirements.txt
├── urban_intel.db          ← created automatically on first run (not committed to git)
│
├── app/
│   ├── main.py              ← FastAPI app, CORS, startup seeding, route wiring
│   ├── api/                 ← HTTP routes (thin — just calls services/)
│   │   ├── events.py
│   │   ├── traffic.py
│   │   └── buses.py
│   ├── models/               ← SQLAlchemy table definitions
│   │   ├── event.py
│   │   └── bus.py
│   ├── schemas/               ← Pydantic request/response validation
│   │   ├── event.py
│   │   └── bus.py
│   ├── database/
│   │   ├── database.py       ← engine, session, get_db()
│   │   └── seed.py           ← starter bus data
│   └── services/              ← actual business logic / DB queries
│       ├── event_service.py
│       └── traffic_service.py
│
└── tests/
    ├── conftest.py           ← shared test setup (in-memory test DB)
    ├── test_events.py
    ├── test_traffic.py
    └── test_buses.py
```

**Request flow (how a file connects to another):**

```
POST /events (Person 3's event engine)
        ↓
app/api/events.py         (receives request, validates via schema)
        ↓
app/schemas/event.py      (EventCreate — Pydantic validation)
        ↓
app/services/event_service.py   (business logic: duplicate check, insert)
        ↓
app/models/event.py       (SQLAlchemy table definition)
        ↓
SQLite (urban_intel.db)
        ↓
app/api/events.py  → GET /events  → React (Person 5) → Leaflet map
```

---

## 4. API Endpoints

| Method | Path                  | Purpose                              |
|--------|-----------------------|---------------------------------------|
| GET    | `/health`              | Confirm the server is running         |
| POST   | `/events`              | Receive a new event                   |
| GET    | `/events`              | List events (optional filters)        |
| GET    | `/events/{event_id}`   | Get one event by ID                   |
| GET    | `/buses`               | List all buses                        |
| GET    | `/traffic`             | Aggregated traffic snapshot           |

### Example: create an event

```bash
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "EVT-0001",
    "bus_id": "BUS-001",
    "camera_id": "FRONT-01",
    "event_type": "POTHOLE",
    "confidence": 0.92,
    "timestamp": "2026-08-26T10:32:14.630",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "frame_id": 1420,
    "evidence_path": "events/EVT-0001.jpg"
  }'
```

Response (201 Created):
```json
{ "success": true, "event_id": "EVT-0001" }
```

Posting the same `event_id` again returns **409 Conflict**:
```json
{ "detail": "Event ID already exists" }
```

### Example: list events

```bash
curl http://localhost:8000/events
curl http://localhost:8000/events?event_type=POTHOLE
curl http://localhost:8000/events?bus_id=BUS-001
```

### Example: get one event

```bash
curl http://localhost:8000/events/EVT-0001
```

Not found → **404**: `{ "detail": "Event not found" }`

### Example: buses and traffic

```bash
curl http://localhost:8000/buses
curl http://localhost:8000/traffic
```

---

## 5. Running Tests

```bash
pip install pytest httpx
pytest tests/ -v
```

Tests use a temporary in-memory database, so they never touch `urban_intel.db`.

---

## 6. MVP vs Future Production

| Feature | 5-Day MVP | Future Production |
|---|---|---|
| SQLite | ✅ Required | ❌ Replace with PostgreSQL for concurrent writes at scale |
| CORS allowing `localhost:5173` | ✅ Required | Replace with real deployed frontend domain |
| No authentication | ✅ Fine for demo | ❌ Add JWT/API-key auth so only real buses can POST events |
| Mock/seeded traffic numbers | ✅ Acceptable | Replace with real aggregation across live VEHICLE events |
| Duplicate check via unique `event_id` | ✅ Sufficient | Add idempotency keys + retry-safe ingestion for flaky bus connectivity |
| Single FastAPI process | ✅ Sufficient for demo | Add a message queue (e.g. Kafka) to buffer bursts of events from hundreds of buses |
| Swagger UI open to anyone | ✅ Fine for demo | Restrict/disable in production |

---

## 7. Integration Notes

- **Person 3 (GPS + Event Engine)** → sends `POST /events` using the exact shared JSON contract. Field names are fixed; do not rename them.
- **Person 5 (Frontend + GIS)** → consumes `GET /events`, `GET /events/{event_id}`, `GET /buses`, `GET /traffic`. React must run on `http://localhost:5173` for CORS to work out of the box.
- React should **never** touch `urban_intel.db` directly — it only talks to this API.
