"""
database.py
------------
This file sets up the connection to our SQLite database using SQLAlchemy.

Think of SQLAlchemy as a translator between Python code and SQL.
Instead of writing raw SQL like "INSERT INTO events VALUES (...)",
we write normal Python objects and SQLAlchemy converts that into SQL for us.

Three important things live here:
1. engine       -> the actual connection to the SQLite file on disk
2. SessionLocal -> a factory that creates new "conversations" (sessions) with the database
3. Base         -> a base class that all our table models (Event, Bus) will inherit from
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# This is the path to our SQLite database file.
# SQLite stores the entire database in a single file called "urban_intel.db".
# It will be created automatically the first time the app runs.
SQLALCHEMY_DATABASE_URL = "sqlite:///./urban_intel.db"

# check_same_thread=False is required ONLY for SQLite.
# FastAPI can handle multiple requests using different threads, and by default
# SQLite only allows the thread that created a connection to use it.
# This setting relaxes that restriction, which is safe for our simple use case.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal is a "factory" — every time we call SessionLocal(), we get a
# new database session (a temporary workspace for talking to the database).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class for our table models (app/models/event.py, app/models/bus.py).
# When those files do "class Event(Base):", SQLAlchemy knows Event should become a table.
Base = declarative_base()


def get_db():
    """
    This function provides a database session to any API route that needs one.

    FastAPI calls this automatically because of "Depends(get_db)" in our routes
    (this pattern is called "dependency injection" — FastAPI supplies the
    dependency, the route function doesn't have to create it manually).

    The "yield" pauses this function, hands the session to the route,
    and once the route is done, execution resumes here and closes the session.
    This guarantees the connection is always closed, even if an error happens.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
