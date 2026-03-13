import pytest
from collections.abc import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from faker import Faker

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Briefing # noqa: F401

fake = Faker()

"""
Integration test suite for the briefings API.
Covers the core pipeline: creation, validation, Jinja2 rendering, and HTML persistence.
Uses Faker for dynamic data and an in-memory SQLite override
"""

@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    # isolated sqlite in-memory db for testing
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
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

    # swap the production db for the testing one
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # clear overrides and drop tables after each test run
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def generate_briefing_payload(**kwargs) -> dict:
    # helper to build valid briefing data; lets us override specific fields for edge cases
    payload = {
        "companyName": fake.company(),
        "ticker": fake.lexify(text='????').lower(),
        "sector": fake.bs(),
        "analystName": fake.name(),
        "summary": fake.paragraph(),
        "recommendation": fake.sentence(),
        "keyPoints": [fake.sentence() for _ in range(3)],
        "risks": [fake.sentence() for _ in range(2)],
        "metrics": [
            {"name": fake.word(), "value": fake.numerify(text='##%')},
            {"name": fake.word(), "value": fake.numerify(text='##.#x')}
        ]
    }
    payload.update(kwargs)
    return payload


def test_briefing_lifecycle(client: TestClient):
    # happy path: create -> retrieve -> generate report -> fetch html
    payload = generate_briefing_payload()
    name = payload["companyName"]
    tick = payload["ticker"]

    # create
    res = client.post("/briefings", json=payload)
    assert res.status_code == 201
    briefing_id = res.json()["id"]

    # verify data exists and ticker is normalized to uppercase
    get_res = client.get(f"/briefings/{briefing_id}")
    assert get_res.status_code == 200
    assert get_res.json()["ticker"] == tick.upper()

    # trigger html generation
    gen_res = client.post(f"/briefings/{briefing_id}/generate")
    assert gen_res.status_code == 200
    assert gen_res.json()["status"] == "generated"

    # fetch html and check for injected content
    html_res = client.get(f"/briefings/{briefing_id}/html")
    assert html_res.status_code == 200
    assert name in html_res.text


def test_optional_metrics_handling(client: TestClient):
    # ensure it doesn't crash if metrics are omitted
    payload = generate_briefing_payload(metrics=None)
    res = client.post("/briefings", json=payload)
    assert res.status_code == 201
    assert res.json()["metrics"] == []


def test_briefing_validation_constraints(client: TestClient):
    # checks the min-item constraints on the schema
    
    # Rule: At least 2 key points
    invalid_points = generate_briefing_payload(keyPoints=[fake.sentence()])
    res = client.post("/briefings", json=invalid_points)
    assert res.status_code == 422
    assert "at least 2 item" in res.text

    # Rule: At least 1 risk
    invalid_risks = generate_briefing_payload(risks=[])
    res = client.post("/briefings", json=invalid_risks)
    assert res.status_code == 422
    assert "at least 1 item" in res.text

    # Rule: Unique metric names within the same briefing
    metric_name = fake.word()
    dups = generate_briefing_payload(
        metrics=[{"name": metric_name, "value": "1"}, {"name": metric_name, "value": "2"}]
    )
    res = client.post("/briefings", json=dups)
    assert res.status_code == 422
    # assert "Metric names must be unique" in res.text


def test_404_handling(client: TestClient):
    # verify all id-based routes return 404 for missing records
    non_existent_id = 12345
    # retrieve
    assert client.get(f"/briefings/{non_existent_id}").status_code == 404
    # generate
    assert client.post(f"/briefings/{non_existent_id}/generate").status_code == 404
    # fetch HTML
    assert client.get(f"/briefings/{non_existent_id}/html").status_code == 404



def test_briefing_complex_data_integrity(client: TestClient) -> None:
    """
    Test that large sets of data (multiple points, risks, and metrics) render correctly.
    """
    payload = generate_briefing_payload(
        keyPoints=[f"Point {i}: {fake.sentence()}" for i in range(10)],
        risks=[f"Risk {i}: {fake.sentence()}" for i in range(5)],
        metrics=[{"name": f"Metric {i}", "value": f"{i}%"} for i in range(8)]
    )
    
    # 1. Create
    create_res = client.post("/briefings", json=payload)
    assert create_res.status_code == 201
    briefing_id = create_res.json()["id"]

    # 2. Generate Report
    gen_res = client.post(f"/briefings/{briefing_id}/generate")
    assert gen_res.status_code == 200

    # 3. Fetch HTML
    html_res = client.get(f"/briefings/{briefing_id}/html")
    assert html_res.status_code == 200
    html_text = html_res.text
    
    # 4. Verify all data exists in HTML
    for point in payload["keyPoints"]:
        assert point in html_text
    for risk in payload["risks"]:
        assert risk in html_text
    for metric in payload["metrics"]:
        assert metric["name"].title() in html_text
        assert metric["value"] in html_text

def test_briefing_isolation(client: TestClient):
    # ensure two separate briefings don't leak data into each other
    id_a = client.post("/briefings", json=generate_briefing_payload(companyName="Alpha")).json()["id"]
    id_b = client.post("/briefings", json=generate_briefing_payload(companyName="Beta")).json()["id"]

    assert client.get(f"/briefings/{id_a}").json()["company_name"] == "Alpha"
    assert client.get(f"/briefings/{id_b}").json()["company_name"] == "Beta"


def test_list_all_briefings(client: TestClient):
    # check empty state and collection retrieval
    assert len(client.get("/briefings").json()) == 0

    for _ in range(3):
        client.post("/briefings", json=generate_briefing_payload())

    res = client.get("/briefings")
    assert res.status_code == 200
    assert len(res.json()) == 3