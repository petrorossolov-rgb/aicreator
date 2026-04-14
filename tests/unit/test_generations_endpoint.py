"""Unit tests for GET /api/v1/generations/{id}."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from aicreator.api.app import create_app
from aicreator.api.dependencies import get_db
from aicreator.db.models import Base, Generation, GenerationStatus


@pytest.fixture()
def _db_session():
    """In-memory SQLite with generations table."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine)
    session = testing_session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(_db_session: Session):
    app = create_app()

    def _override_db():
        yield _db_session

    app.dependency_overrides[get_db] = _override_db

    with TestClient(app) as c:
        yield c


class TestGetExistingGeneration:
    def test_returns_all_fields(self, client: TestClient, _db_session: Session):
        gen_id = uuid4()
        now = datetime.now(UTC)
        gen = Generation(
            id=gen_id,
            spec_type="openapi",
            language="go",
            function="server",
            status=GenerationStatus.COMPLETED.value,
            input_hash="abc123" * 10 + "abcd",
            created_at=now,
            completed_at=now,
            duration_ms=42,
        )
        _db_session.add(gen)
        _db_session.commit()

        resp = client.get(f"/api/v1/generations/{gen_id}")

        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == str(gen_id)
        assert data["function"] == "server"
        assert data["language"] == "go"
        assert data["spec_type"] == "openapi"
        assert data["status"] == "completed"
        assert data["duration_ms"] == 42
        assert data["error"] is None


class TestGetNonexistentGeneration:
    def test_returns_404(self, client: TestClient):
        random_id = uuid4()
        resp = client.get(f"/api/v1/generations/{random_id}")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()


class TestGetInvalidUuid:
    def test_returns_422(self, client: TestClient):
        resp = client.get("/api/v1/generations/not-a-uuid")
        assert resp.status_code == 422
