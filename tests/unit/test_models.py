"""Tests for Generation model and repository functions."""

from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker

from aicreator.db.models import Base, GenerationStatus
from aicreator.db.repository import create_generation, get_generation, update_generation_status


@pytest.fixture
def db_session() -> Session:  # type: ignore[misc]
    """Create in-memory SQLite session for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session  # type: ignore[misc]
    session.close()


def test_create_generation(db_session: Session) -> None:
    gen = create_generation(
        db_session,
        spec_type="proto",
        language="go",
        function="F1",
        input_hash="abc123def456",
    )
    assert gen.id is not None
    # Verify it's a valid UUID (stored as string in SQLite)
    UUID(str(gen.id))
    assert gen.spec_type == "proto"
    assert gen.language == "go"
    assert gen.function == "F1"
    assert gen.status == GenerationStatus.PENDING.value
    assert gen.input_hash == "abc123def456"
    assert gen.created_at is not None


def test_get_generation_not_found(db_session: Session) -> None:
    result = get_generation(db_session, uuid4())
    assert result is None


def test_update_status(db_session: Session) -> None:
    gen = create_generation(
        db_session,
        spec_type="openapi",
        language="go",
        function="F2",
        input_hash="hash789",
    )
    gen_id = UUID(str(gen.id))

    # pending -> running
    updated = update_generation_status(db_session, gen_id, GenerationStatus.RUNNING)
    assert updated is not None
    assert updated.status == GenerationStatus.RUNNING.value
    assert updated.completed_at is None

    # running -> completed
    updated = update_generation_status(db_session, gen_id, GenerationStatus.COMPLETED, duration_ms=1234)
    assert updated is not None
    assert updated.status == GenerationStatus.COMPLETED.value
    assert updated.completed_at is not None
    assert updated.duration_ms == 1234


def test_input_hash_indexed(db_session: Session) -> None:
    engine = db_session.get_bind()
    inspector = inspect(engine)
    indexes = inspector.get_indexes("generations")
    index_names = [idx["name"] for idx in indexes]
    assert "ix_generations_input_hash" in index_names
