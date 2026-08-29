"""
tests/conftest.py
------------------
Shared test setup (a "fixture") used by all test files.

Why do we need this? If our tests used the REAL urban_intel.db file, they'd
leave test data lying around and could conflict with real events. Instead,
each test run gets a fresh, temporary, in-memory SQLite database that
disappears when the tests finish.

pytest automatically finds this file and makes `client` available to any
test function that asks for it as a parameter.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database.database import Base, get_db
from app.database import seed
from app.main import app

# In-memory SQLite database — exists only for the duration of the test run.
#
# StaticPool is important here: by default, SQLAlchemy opens a NEW SQLite
# connection per request, and ":memory:" databases are wiped the moment
# their connection closes — meaning each request would see an empty,
# separate database. StaticPool forces every session to reuse the SAME
# single connection, so all our test requests share one in-memory database.
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Swap in the test database session instead of the real one."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    """
    Creates fresh tables before each test and drops them afterward, so
    every test starts with a clean, empty database.

    Note: app.main's own @app.on_event("startup") seeding uses the REAL
    database session (imported directly from database.py), not this
    overridden test session — so it won't seed our in-memory test database.
    We seed it here instead, using the same test session the app will
    actually query against.
    """
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db

    seed_db = TestingSessionLocal()
    seed.seed_buses(seed_db)
    seed_db.close()

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
