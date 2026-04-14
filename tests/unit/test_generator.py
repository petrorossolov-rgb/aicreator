"""Tests for core generator abstractions."""

from pathlib import Path

import pytest

from aicreator.core.generator import BaseGenerator, GenerationResult, GeneratorConfig, ValidationResult


class StubGenerator(BaseGenerator):
    """Concrete generator for testing."""

    def validate(self, spec_path: Path) -> ValidationResult:
        if not spec_path.exists():
            return ValidationResult(valid=False, errors=[f"Path not found: {spec_path}"])
        return ValidationResult(valid=True)

    def generate(self, spec_path: Path, output_dir: Path, config: GeneratorConfig) -> GenerationResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        stub_file = output_dir / "stub_output.go"
        stub_file.write_text("package stub\n")
        return GenerationResult(
            output_dir=output_dir,
            files_generated=1,
            duration_ms=10,
            success=True,
        )


def test_base_generator_is_abstract() -> None:
    with pytest.raises(TypeError, match="abstract method"):
        BaseGenerator()  # type: ignore[abstract]


def test_stub_generator_implements_interface(tmp_path: Path) -> None:
    gen = StubGenerator()
    spec_path = tmp_path / "specs"
    spec_path.mkdir()

    result = gen.validate(spec_path)
    assert result.valid is True
    assert result.errors == []

    output_dir = tmp_path / "output"
    gen_result = gen.generate(spec_path, output_dir, GeneratorConfig())
    assert gen_result.success is True
    assert gen_result.files_generated == 1
    assert (output_dir / "stub_output.go").exists()


def test_generation_result_fields() -> None:
    result = GenerationResult(
        output_dir=Path("/tmp/out"),
        files_generated=5,
        duration_ms=123,
        success=True,
        error=None,
    )
    assert result.output_dir == Path("/tmp/out")
    assert result.files_generated == 5
    assert result.duration_ms == 123
    assert result.success is True
    assert result.error is None


def test_generation_result_with_error() -> None:
    result = GenerationResult(
        output_dir=Path("/tmp/out"),
        files_generated=0,
        duration_ms=50,
        success=False,
        error="buf generate failed",
    )
    assert result.success is False
    assert result.error == "buf generate failed"


def test_validation_result_invalid() -> None:
    result = ValidationResult(valid=False, errors=["missing buf.yaml", "no .proto files"])
    assert result.valid is False
    assert len(result.errors) == 2
