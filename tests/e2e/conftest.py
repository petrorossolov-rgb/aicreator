"""E2E test fixtures — Docker Compose management and API client."""

import subprocess
import time
from pathlib import Path

import httpx
import pytest

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
DOCKER_COMPOSE_FILE = Path(__file__).parent.parent.parent / "docker" / "docker-compose.yml"

API_URL = "http://localhost:8000"
HEALTH_URL = f"{API_URL}/api/v1/health"
MAX_WAIT_SECONDS = 120


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Mark all tests in e2e/ with @pytest.mark.e2e."""
    for item in items:
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)


@pytest.fixture(scope="session")
def api_url() -> str:
    """Return the base URL for the running API."""
    return API_URL


@pytest.fixture(scope="session", autouse=True)
def docker_compose_up():  # type: ignore[no-untyped-def]
    """Start Docker Compose with prod profile, wait for health, tear down after tests."""
    # Start services
    subprocess.run(
        ["docker", "compose", "-f", str(DOCKER_COMPOSE_FILE), "--profile", "prod", "up", "-d", "--build"],
        check=True,
        capture_output=True,
        text=True,
    )

    # Wait for API to become healthy
    start = time.monotonic()
    while time.monotonic() - start < MAX_WAIT_SECONDS:
        try:
            resp = httpx.get(HEALTH_URL, timeout=5.0)
            if resp.status_code == 200:
                break
        except (httpx.ConnectError, httpx.ReadTimeout):
            pass
        time.sleep(2)
    else:
        # Dump logs for debugging
        logs = subprocess.run(
            ["docker", "compose", "-f", str(DOCKER_COMPOSE_FILE), "--profile", "prod", "logs", "api-prod"],
            capture_output=True,
            text=True,
        )
        pytest.fail(f"API did not become healthy within {MAX_WAIT_SECONDS}s.\nLogs:\n{logs.stdout}\n{logs.stderr}")

    yield

    # Tear down
    subprocess.run(
        ["docker", "compose", "-f", str(DOCKER_COMPOSE_FILE), "--profile", "prod", "down", "-v"],
        capture_output=True,
        text=True,
    )


@pytest.fixture()
def proto_specs_dir() -> Path:
    """Path to valid proto specs directory."""
    return FIXTURES_DIR / "proto"


@pytest.fixture()
def openapi_spec_path() -> Path:
    """Path to valid OpenAPI spec file."""
    return FIXTURES_DIR / "openapi" / "logistics.yaml"


@pytest.fixture()
def invalid_proto_dir() -> Path:
    """Path to invalid proto specs directory."""
    return FIXTURES_DIR / "invalid" / "proto"
