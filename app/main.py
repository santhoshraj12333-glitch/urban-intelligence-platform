"""
main.py
-------
This is the entry point of the backend. Running:

    uvicorn app.main:app --reload

starts this file's `app` object as a live web server.

This file's job is just to WIRE THINGS TOGETHER:
- create the FastAPI app
- turn on CORS so React can call us
- create database tables if they don't exist yet
- seed starter bus data
- plug in the three route files (events, buses, traffic)

It intentionally contains almost no actual logic — that all lives in
api/*.py and services/*.py.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import engine, Base, SessionLocal
from app.database import seed
from app.api import events, buses, traffic

# This line tells SQLAlchemy: "look at every model that inherits from Base
# (Event, Bus) and create their tables in the SQLite file if they don't
# already exist." Safe to run every time the app starts.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Urban Intelligence Platform API",
    description="Backend for SIH26124 — AI-Powered Mobile Urban Intelligence Platform Using Public Transport Fleet",
    version="1.0.0",
)

# ---- CORS SETUP ----
# By default, browsers block a React app running on localhost:5173 from
# calling an API on localhost:8000 ("cross-origin" request). This middleware
# tells the browser that requests from our React dev server are allowed.
#
# REQUIRED for the 5-day MVP (React frontend won't be able to call us without it).
# For future production deployment, allow_origins would list the real deployed
# frontend domain instead of localhost.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """
    Runs once when the server starts.
    We use it to insert our seed bus data (see database/seed.py).
    """
    db = SessionLocal()
    try:
        seed.seed_buses(db)
    finally:
        db.close()


# ---- ROUTES ----
# include_router pulls in every @router.get/@router.post defined in those
# files and attaches them to this app, as if they'd been written here directly.
app.include_router(events.router, tags=["Events"])
app.include_router(buses.router, tags=["Buses"])
app.include_router(traffic.router, tags=["Traffic"])


@app.get("/health", tags=["Health"])
def health_check():
    """Simple endpoint to confirm the server is running. Useful for Person 6's integration testing."""
    return {"status": "ok"}
