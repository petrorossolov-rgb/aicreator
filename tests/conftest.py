from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture()
def proto_specs_dir() -> Path:
    """Path to valid proto specs directory (buf.yaml + .proto files)."""
    return FIXTURES_DIR / "proto"


@pytest.fixture()
def openapi_spec_path() -> Path:
    """Path to valid OpenAPI spec file."""
    return FIXTURES_DIR / "openapi" / "logistics.yaml"


@pytest.fixture()
def invalid_proto_dir() -> Path:
    """Path to invalid proto specs directory (broken.proto)."""
    return FIXTURES_DIR / "invalid" / "proto"


@pytest.fixture()
def invalid_openapi_path() -> Path:
    """Path to invalid OpenAPI spec (missing paths key)."""
    return FIXTURES_DIR / "invalid" / "openapi" / "logistics.yaml"
