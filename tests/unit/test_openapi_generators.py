"""Tests for OpenAPI generators (server F2 + client F4)."""

from pathlib import Path
from unittest.mock import patch

import pytest

from aicreator.core.generator import GeneratorConfig
from aicreator.generators.openapi_client import OpenAPIClientGenerator
from aicreator.generators.openapi_server import OpenAPIServerGenerator

TEMPLATES_DIR = Path(__file__).parents[2] / "src" / "aicreator" / "templates" / "go-server"


@pytest.fixture()
def server_gen() -> OpenAPIServerGenerator:
    return OpenAPIServerGenerator()


@pytest.fixture()
def client_gen() -> OpenAPIClientGenerator:
    return OpenAPIClientGenerator()


@pytest.fixture()
def config() -> GeneratorConfig:
    return GeneratorConfig(
        tool_path="/opt/openapi-generator/openapi-generator-cli.jar",
        template_dir=TEMPLATES_DIR,
        additional_properties={"router": "mux"},
        timeout=60,
    )


@pytest.fixture()
def config_no_template() -> GeneratorConfig:
    return GeneratorConfig(
        tool_path="/opt/openapi-generator/openapi-generator-cli.jar",
        timeout=60,
    )


class TestValidate:
    def test_validate_valid_openapi_spec(self, server_gen: OpenAPIServerGenerator, openapi_spec_path: Path) -> None:
        result = server_gen.validate(openapi_spec_path)
        assert result.valid is True
        assert result.errors == []

    def test_validate_not_yaml(self, server_gen: OpenAPIServerGenerator, tmp_path: Path) -> None:
        txt = tmp_path / "spec.txt"
        txt.write_text("not yaml at all")
        result = server_gen.validate(txt)
        assert result.valid is False
        assert any(".yaml" in e or ".yml" in e for e in result.errors)

    def test_validate_missing_openapi_key(self, server_gen: OpenAPIServerGenerator, tmp_path: Path) -> None:
        spec = tmp_path / "no_openapi.yaml"
        spec.write_text("info:\n  title: Not OpenAPI\n  version: '1.0'\n")
        result = server_gen.validate(spec)
        assert result.valid is False
        assert any("openapi" in e.lower() for e in result.errors)

    def test_validate_nonexistent_file(self, server_gen: OpenAPIServerGenerator, tmp_path: Path) -> None:
        result = server_gen.validate(tmp_path / "nonexistent.yaml")
        assert result.valid is False

    def test_client_validate_same_logic(self, client_gen: OpenAPIClientGenerator, openapi_spec_path: Path) -> None:
        result = client_gen.validate(openapi_spec_path)
        assert result.valid is True


class TestServerGenerate:
    def test_server_generate_calls_subprocess(
        self,
        server_gen: OpenAPIServerGenerator,
        openapi_spec_path: Path,
        tmp_path: Path,
        config: GeneratorConfig,
    ) -> None:
        output_dir = tmp_path / "output"
        mock_result = type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()

        with patch("aicreator.generators.openapi_base.subprocess.run", return_value=mock_result) as mock_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "api.go").write_text("package api\n")

            result = server_gen.generate(openapi_spec_path, output_dir, config)

        assert result.success is True
        call_args = mock_run.call_args[0][0]
        assert "go-server" in call_args
        assert "-i" in call_args
        assert "-t" in call_args

    def test_generate_includes_template_dir(
        self,
        server_gen: OpenAPIServerGenerator,
        openapi_spec_path: Path,
        tmp_path: Path,
        config: GeneratorConfig,
    ) -> None:
        output_dir = tmp_path / "output"
        mock_result = type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()

        with patch("aicreator.generators.openapi_base.subprocess.run", return_value=mock_result) as mock_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            server_gen.generate(openapi_spec_path, output_dir, config)

        call_args = mock_run.call_args[0][0]
        template_idx = call_args.index("-t")
        assert str(TEMPLATES_DIR) == call_args[template_idx + 1]

    def test_generate_no_template_dir_when_missing(
        self,
        server_gen: OpenAPIServerGenerator,
        openapi_spec_path: Path,
        tmp_path: Path,
        config_no_template: GeneratorConfig,
    ) -> None:
        output_dir = tmp_path / "output"
        mock_result = type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()

        with patch("aicreator.generators.openapi_base.subprocess.run", return_value=mock_result) as mock_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            server_gen.generate(openapi_spec_path, output_dir, config_no_template)

        call_args = mock_run.call_args[0][0]
        assert "-t" not in call_args

    def test_generate_failure_captures_stderr(
        self,
        server_gen: OpenAPIServerGenerator,
        openapi_spec_path: Path,
        tmp_path: Path,
        config: GeneratorConfig,
    ) -> None:
        output_dir = tmp_path / "output"
        mock_result = type("Result", (), {"returncode": 1, "stdout": "", "stderr": "generator error"})()

        with patch("aicreator.generators.openapi_base.subprocess.run", return_value=mock_result):
            result = server_gen.generate(openapi_spec_path, output_dir, config)

        assert result.success is False
        assert "generator error" in (result.error or "")


class TestClientGenerate:
    def test_client_generate_calls_subprocess(
        self,
        client_gen: OpenAPIClientGenerator,
        openapi_spec_path: Path,
        tmp_path: Path,
        config_no_template: GeneratorConfig,
    ) -> None:
        output_dir = tmp_path / "output"
        mock_result = type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()

        with patch("aicreator.generators.openapi_base.subprocess.run", return_value=mock_result) as mock_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "client.go").write_text("package client\n")

            result = client_gen.generate(openapi_spec_path, output_dir, config_no_template)

        assert result.success is True
        call_args = mock_run.call_args[0][0]
        # F4 uses "go" generator (client), not "go-server"
        assert "go" in call_args
        assert "go-server" not in call_args
