from pathlib import Path

import pytest

from aicreator.core.generator import BaseGenerator, GenerationResult, GeneratorConfig, ValidationResult

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class StubGenerator(BaseGenerator):
    """Concrete generator for testing — returns canned results."""

    def __init__(self, *, should_fail_validation: bool = False) -> None:
        self._should_fail_validation = should_fail_validation

    def validate(self, spec_path: Path) -> ValidationResult:
        if self._should_fail_validation:
            return ValidationResult(valid=False, errors=["stub validation failure"])
        return ValidationResult(valid=True)

    def generate(self, spec_path: Path, output_dir: Path, config: GeneratorConfig) -> GenerationResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "stub_output.go").write_text("package stub\n")
        return GenerationResult(
            output_dir=output_dir,
            files_generated=1,
            duration_ms=10,
            success=True,
        )


@pytest.fixture()
def stub_generator() -> StubGenerator:
    return StubGenerator()


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
