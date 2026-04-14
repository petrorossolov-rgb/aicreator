"""Tests for health endpoint, request ID middleware, and OpenAPI schema."""

import logging

from fastapi.testclient import TestClient

from aicreator.api.app import create_app


def get_client() -> TestClient:
    return TestClient(create_app())


def test_health_returns_ok() -> None:
    client = get_client()
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"


def test_request_id_header() -> None:
    client = get_client()
    resp = client.get("/api/v1/health")
    assert "X-Request-ID" in resp.headers
    # Should be a valid UUID-like string
    assert len(resp.headers["X-Request-ID"]) >= 32


def test_request_id_passthrough() -> None:
    client = get_client()
    custom_id = "test-request-123"
    resp = client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
    assert resp.headers["X-Request-ID"] == custom_id


def test_openapi_schema_accessible() -> None:
    client = get_client()
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert "paths" in schema
    assert "/api/v1/health" in schema["paths"]


def test_logging_includes_request_id() -> None:
    from aicreator.core.logging import RequestIdFilter, request_id_ctx

    # Test that RequestIdFilter injects request_id from context var
    log_filter = RequestIdFilter()
    record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)

    # Default value
    log_filter.filter(record)
    assert getattr(record, "request_id", None) == "-"

    # With context var set (simulates what middleware does)
    token = request_id_ctx.set("trace-abc-456")
    try:
        record2 = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        log_filter.filter(record2)
        assert getattr(record2, "request_id", None) == "trace-abc-456"
    finally:
        request_id_ctx.reset(token)
