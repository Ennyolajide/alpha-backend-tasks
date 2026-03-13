# tests/test_briefings.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

@pytest.fixture()
def client():
    # Setup in-memory SQLite
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_create_briefing_base_flow(client: TestClient):
    """Verifies that the core briefing record can be created and fetched."""
    payload = {
        "companyName": "Test Tech",
        "ticker": "TT",
        "sector": "Software",
        "analystName": "Jide",
        "summary": "Example summary",
        "recommendation": "Hold",
        "keyPoints": ["P1", "P2"], # Sent, but service will ignore for now
        "risks": ["R1"]
    }
    
    # Create
    resp = client.post("/briefings", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["company_name"] == "Test Tech"
    
    # List
    list_resp = client.get("/briefings")
    assert len(list_resp.json()) == 1

def test_get_invalid_briefing(client: TestClient):
    """Check 404 behavior"""
    resp = client.get("/briefings/999")
    assert resp.status_code == 404