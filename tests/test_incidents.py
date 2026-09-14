from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = (
    "postgresql://test:test@localhost:5433/opsboard_test"
)

test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=test_engine)

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_incident():
    incident = {
        "title": "Database is down",
        "description": "PostgreSQL is not responding",
        "severity": "P1",
        "status": "OPEN",
    }

    response = client.post("/incidents", json=incident)

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Database is down"
    assert data["severity"] == "P1"


def test_get_incidents():
    response = client.get("/incidents")

    assert response.status_code == 200
    assert isinstance(response.json(), list)