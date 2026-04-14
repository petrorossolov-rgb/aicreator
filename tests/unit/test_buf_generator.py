"""Tests for BufGoGenerator."""

from pathlib import Path
from unittest.mock import patch

import pytest

from aicreator.core.generator import GeneratorConfig
from aicreator.generators.buf import BufGoGenerator


@pytest.fixture()
def generator() -> BufGoGenerator:
    return BufGoGenerator()


@pytest.fixture()
def config() -> GeneratorConfig:
    return GeneratorConfig(timeout=60)


class TestValidate:
    def test_validate_valid_proto_dir(self, generator: BufGoGenerator, proto_specs_dir: Path) -> None:
        result = generator.validate(proto_specs_dir)
        assert result.valid is True
        assert result.errors == []

    def test_validate_missing_buf_yaml(self, generator: BufGoGenerator, tmp_path: Path) -> None:
        (tmp_path / "test.proto").write_text('syntax = "proto3";')
        result = generator.validate(tmp_path)
        assert result.valid is False
        assert any("buf.yaml" in e for e in result.errors)

    def test_validate_empty_dir(self, generator: BufGoGenerator, tmp_path: Path) -> None:
        (tmp_path / "buf.yaml").write_text("version: v2\n")
        result = generator.validate(tmp_path)
        assert result.valid is False
        assert any(".proto" in e for e in result.errors)

    def test_validate_not_a_directory(self, generator: BufGoGenerator, tmp_path: Path) -> None:
        file_path = tmp_path / "not_a_dir.txt"
        file_path.write_text("hello")
        result = generator.validate(file_path)
        assert result.valid is False
        assert any("not a directory" in e for e in result.errors)


class TestGenerate:
    def test_generate_calls_subprocess(
        self, generator: BufGoGenerator, proto_specs_dir: Path, tmp_path: Path, config: GeneratorConfig
    ) -> None:
        output_dir = tmp_path / "output"
        mock_result = type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()

        with patch("aicreator.generators.buf.subprocess.run", return_value=mock_result) as mock_run:
            # Create a fake .go file so file count > 0
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "test.go").write_text("package test\n")

            result = generator.generate(proto_specs_dir, output_dir, config)

        assert result.success is True
        assert result.files_generated == 1
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert "buf" in call_args[0][0]
        assert "generate" in call_args[0][0]
        assert "--template" in call_args[0][0]

    def test_generate_failure_captures_stderr(
        self, generator: BufGoGenerator, proto_specs_dir: Path, tmp_path: Path, config: GeneratorConfig
    ) -> None:
        output_dir = tmp_path / "output"
        mock_result = type("Result", (), {"returncode": 1, "stdout": "", "stderr": "buf: unknown plugin go"})()

        with patch("aicreator.generators.buf.subprocess.run", return_value=mock_result):
            result = generator.generate(proto_specs_dir, output_dir, config)

        assert result.success is False
        assert "unknown plugin" in (result.error or "")

    def test_generate_timeout(
        self, generator: BufGoGenerator, proto_specs_dir: Path, tmp_path: Path, config: GeneratorConfig
    ) -> None:
        import subprocess

        output_dir = tmp_path / "output"

        with patch(
            "aicreator.generators.buf.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="buf", timeout=60),
        ):
            result = generator.generate(proto_specs_dir, output_dir, config)

        assert result.success is False
        assert "timed out" in (result.error or "")

    def test_generate_no_template(self, generator: BufGoGenerator, tmp_path: Path, config: GeneratorConfig) -> None:
        spec_dir = tmp_path / "specs"
        spec_dir.mkdir()
        output_dir = tmp_path / "output"

        result = generator.generate(spec_dir, output_dir, config)
        assert result.success is False
        assert "template" in (result.error or "").lower()
