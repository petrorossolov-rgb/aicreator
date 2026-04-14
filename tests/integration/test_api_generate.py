"""Integration tests for POST /api/v1/generate."""

import io
import json
import zipfile
from pathlib import Path
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from aicreator.api.app import create_app
from aicreator.api.dependencies import get_db, get_orchestrator
from aicreator.core.generator import BaseGenerator, GenerationResult, GeneratorConfig, ValidationResult
from aicreator.core.orchestrator import Orchestrator
from aicreator.db.models import Base, Generation

# -- Stub generator for tests (no real subprocess) --


class _TestStubGenerator(BaseGenerator):
    """Generator that writes a file without external tools."""

    def validate(self, spec_path: Path) -> ValidationResult:
        return ValidationResult(valid=True)

    def generate(self, spec_path: Path, output_dir: Path, config: GeneratorConfig) -> GenerationResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "main.go").write_text("package main\n")
        return GenerationResult(output_dir=output_dir, files_generated=1, duration_ms=5, success=True)


class _FailingGenerator(BaseGenerator):
    """Generator that always raises."""

    def validate(self, spec_path: Path) -> ValidationResult:
        return ValidationResult(valid=True)

    def generate(self, spec_path: Path, output_dir: Path, config: GeneratorConfig) -> GenerationResult:
        raise RuntimeError("generation exploded")


# -- Fixtures --


@pytest.fixture()
def _db_session():
    """In-memory SQLite session + table creation (thread-safe for TestClient)."""
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
    """TestClient with overridden DB and orchestrator dependencies."""
    app = create_app()

    def _override_db():
        yield _db_session

    def _override_orchestrator():
        orch = Orchestrator()
        return orch

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_orchestrator] = _override_orchestrator

    with TestClient(app) as c:
        yield c


def _metadata_json(
    function: str = "server",
    language: str = "go",
    spec_type: str = "openapi",
) -> str:
    return json.dumps({"function": function, "language": language, "spec_type": spec_type})


def _upload_file(name: str = "spec.yaml", content: bytes = b"openapi: '3.0.3'") -> tuple[str, tuple[str, io.BytesIO]]:
    return ("files", (name, io.BytesIO(content)))


# -- Tests --


class TestGenerateValidRequest:
    """POST /api/v1/generate — happy path."""

    def test_returns_zip(self, client: TestClient):
        Orchestrator.reset_registry()
        Orchestrator.register("openapi", "go", "server")(_TestStubGenerator)

        resp = client.post(
            "/api/v1/generate",
            data={"metadata": _metadata_json()},
            files=[_upload_file()],
        )

        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/zip"

        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        assert "main.go" in zf.namelist()

    def test_response_has_generation_id_header(self, client: TestClient):
        Orchestrator.reset_registry()
        Orchestrator.register("openapi", "go", "server")(_TestStubGenerator)

        resp = client.post(
            "/api/v1/generate",
            data={"metadata": _metadata_json()},
            files=[_upload_file()],
        )

        gen_id = resp.headers.get("X-Generation-ID")
        assert gen_id is not None
        UUID(gen_id)  # validates format


class TestGenerateInvalidMetadata:
    def test_missing_function_field(self, client: TestClient):
        resp = client.post(
            "/api/v1/generate",
            data={"metadata": json.dumps({"language": "go", "spec_type": "openapi"})},
            files=[_upload_file()],
        )
        assert resp.status_code == 422

    def test_malformed_json(self, client: TestClient):
        resp = client.post(
            "/api/v1/generate",
            data={"metadata": "not-json"},
            files=[_upload_file()],
        )
        assert resp.status_code == 422


class TestGenerateNoFiles:
    def test_no_files_returns_422(self, client: TestClient):
        resp = client.post(
            "/api/v1/generate",
            data={"metadata": _metadata_json()},
        )
        assert resp.status_code == 422


class TestGenerateUnsupportedCombination:
    def test_unregistered_combo_returns_400(self, client: TestClient):
        Orchestrator.reset_registry()
        # no generators registered

        resp = client.post(
            "/api/v1/generate",
            data={"metadata": _metadata_json(function="unknown", language="cobol", spec_type="wsdl")},
            files=[_upload_file()],
        )
        assert resp.status_code == 400
        assert "No generator registered" in resp.json()["detail"]


class TestGenerateCreatesDbRecord:
    def test_db_record_created(self, client: TestClient, _db_session: Session):
        Orchestrator.reset_registry()
        Orchestrator.register("openapi", "go", "server")(_TestStubGenerator)

        resp = client.post(
            "/api/v1/generate",
            data={"metadata": _metadata_json()},
            files=[_upload_file()],
        )

        assert resp.status_code == 200
        gen_id = UUID(resp.headers["X-Generation-ID"])
        record = _db_session.get(Generation, gen_id)
        assert record is not None
        assert record.status == "completed"
        assert record.input_hash != ""
        assert record.duration_ms is not None


class TestGenerateFailureReturnsError:
    def test_generation_error_returns_500(self, client: TestClient, _db_session: Session):
        Orchestrator.reset_registry()
        Orchestrator.register("openapi", "go", "server")(_FailingGenerator)

        resp = client.post(
            "/api/v1/generate",
            data={"metadata": _metadata_json()},
            files=[_upload_file()],
        )

        assert resp.status_code == 500
        assert "generation exploded" in resp.json()["detail"]
