from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import backend.database as database
import backend.app as app_module


def setup_test_db(tmp_path: Path):
    db_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    database.engine = engine
    database.SessionLocal = TestingSessionLocal
    app_module.SessionLocal = TestingSessionLocal
    database.Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


def test_create_lead_happy_path(tmp_path):
    setup_test_db(tmp_path)
    client = TestClient(app_module.app)

    response = client.post(
        "/api/lead",
        data={
            "site_slug": "water-damage-restoration_dallas",
            "name": "Jane Doe",
            "phone": "555-123-4567",
            "email": "jane@example.com",
            "service": "Water Extraction",
            "message": "Test message",
        },
    )

    assert response.status_code == 200
    assert "message" in response.json()

    db = database.SessionLocal()
    try:
        leads = db.query(database.Lead).all()
        sites = db.query(database.Site).all()
        assert len(leads) == 1
        assert len(sites) == 1
        assert leads[0].site_id == sites[0].id
        assert sites[0].slug == "water-damage-restoration_dallas"
    finally:
        db.close()


def test_create_lead_missing_required_field(tmp_path):
    setup_test_db(tmp_path)
    client = TestClient(app_module.app)

    response = client.post(
        "/api/lead",
        data={
            "site_slug": "water-damage-restoration_dallas",
            "name": "Jane Doe",
            "phone": "",
        },
    )

    assert response.status_code in (400, 422)


def test_create_lead_slug_without_city(tmp_path):
    setup_test_db(tmp_path)
    client = TestClient(app_module.app)

    response = client.post(
        "/api/lead",
        data={
            "site_slug": "water-damage-restoration",
            "name": "Jane Doe",
            "phone": "555-123-4567",
        },
    )

    assert response.status_code == 200

    db = database.SessionLocal()
    try:
        site = db.query(database.Site).filter_by(slug="water-damage-restoration").first()
        assert site is not None
        assert site.city == "Unknown"
    finally:
        db.close()
