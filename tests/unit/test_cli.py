"""Unit tests for CLI commands."""

import json
import zipfile
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4

import httpx
import pytest
from typer.testing import CliRunner

from aicreator.cli.app import app

runner = CliRunner()


def _zip_bytes(filenames: list[str]) -> bytes:
    """Create a ZIP archive with dummy files."""
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name in filenames:
            zf.writestr(name, f"// {name}\n")
    return buf.getvalue()


class TestGenerateSendsCorrectRequest:
    """Verify that generate command sends correct multipart request to API."""

    def test_sends_multipart_with_metadata(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs"
        spec_dir.mkdir()
        (spec_dir / "order.proto").write_text("syntax = 'proto3';")

        gen_id = str(uuid4())
        zip_content = _zip_bytes(["main.go"])

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.content = zip_content
        mock_response.headers = {"X-Generation-ID": gen_id, "content-type": "application/zip"}

        with patch("aicreator.cli.commands.generate.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value = mock_client

            output_dir = tmp_path / "out"
            result = runner.invoke(
                app,
                [
                    "generate",
                    "--function",
                    "f1",
                    "--spec",
                    str(spec_dir),
                    "--output",
                    str(output_dir),
                ],
            )

            assert result.exit_code == 0, result.output

            call_args = mock_client.post.call_args
            assert "/api/v1/generate" in call_args.args[0]

            # Verify metadata contains correct spec_type
            metadata_str = call_args.kwargs["data"]["metadata"]
            metadata = json.loads(metadata_str)
            assert metadata["function"] == "f1"
            assert metadata["spec_type"] == "proto"
            assert metadata["language"] == "go"


class TestGenerateSavesZipToOutput:
    """Verify that ZIP response is extracted to output directory."""

    def test_extracts_zip_files(self, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.yaml"
        spec_file.write_text("openapi: '3.0.3'")

        zip_content = _zip_bytes(["api/handler.go", "api/model.go"])

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.content = zip_content
        mock_response.headers = {"X-Generation-ID": str(uuid4()), "content-type": "application/zip"}

        with patch("aicreator.cli.commands.generate.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value = mock_client

            output_dir = tmp_path / "out"
            result = runner.invoke(
                app,
                [
                    "generate",
                    "--function",
                    "f2",
                    "--spec",
                    str(spec_file),
                    "--output",
                    str(output_dir),
                ],
            )

            assert result.exit_code == 0, result.output
            assert (output_dir / "api" / "handler.go").exists()
            assert (output_dir / "api" / "model.go").exists()


class TestGenerateApiError:
    """Verify error handling on API failure."""

    def test_500_shows_error_and_exits_1(self, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.yaml"
        spec_file.write_text("openapi: '3.0.3'")

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.text = '{"detail": "generation exploded"}'
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"detail": "generation exploded"}

        with patch("aicreator.cli.commands.generate.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "generate",
                    "--function",
                    "f2",
                    "--spec",
                    str(spec_file),
                    "--output",
                    str(tmp_path / "out"),
                ],
            )

            assert result.exit_code == 1
            assert "generation exploded" in result.output

    def test_connection_error_exits_1(self, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.yaml"
        spec_file.write_text("openapi: '3.0.3'")

        with patch("aicreator.cli.commands.generate.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = httpx.ConnectError("Connection refused")
            mock_client_cls.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "generate",
                    "--function",
                    "f1",
                    "--spec",
                    str(spec_file),
                    "--output",
                    str(tmp_path / "out"),
                ],
            )

            assert result.exit_code == 1
            assert "Cannot connect" in result.output


class TestStatusDisplaysMetadata:
    """Verify status command displays generation metadata."""

    def test_shows_rich_table(self) -> None:
        gen_id = str(uuid4())
        api_data = {
            "id": gen_id,
            "function": "f1",
            "language": "go",
            "spec_type": "proto",
            "status": "completed",
            "input_hash": "abc123",
            "created_at": "2026-04-14T10:00:00",
            "completed_at": "2026-04-14T10:00:05",
            "duration_ms": 5000,
            "error": None,
        }

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = api_data

        with patch("aicreator.cli.commands.status.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = mock_response
            mock_client_cls.return_value = mock_client

            result = runner.invoke(app, ["status", gen_id])

            assert result.exit_code == 0, result.output
            assert "completed" in result.output
            assert "f1" in result.output

    def test_not_found_exits_1(self) -> None:
        gen_id = str(uuid4())

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 404

        with patch("aicreator.cli.commands.status.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = mock_response
            mock_client_cls.return_value = mock_client

            result = runner.invoke(app, ["status", gen_id])

            assert result.exit_code == 1
            assert "not found" in result.output


class TestHealthOk:
    """Verify health command."""

    def test_healthy_api(self) -> None:
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok", "version": "0.1.0"}

        with patch("aicreator.cli.commands.health.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = mock_response
            mock_client_cls.return_value = mock_client

            result = runner.invoke(app, ["health"])

            assert result.exit_code == 0, result.output
            assert "healthy" in result.output
            assert "0.1.0" in result.output

    def test_unhealthy_exits_1(self) -> None:
        with patch("aicreator.cli.commands.health.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.side_effect = httpx.ConnectError("Connection refused")
            mock_client_cls.return_value = mock_client

            result = runner.invoke(app, ["health"])

            assert result.exit_code == 1
            assert "Cannot connect" in result.output


class TestGenerateUnknownFunction:
    """Verify unknown function is rejected."""

    def test_unknown_function_exits_1(self, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.yaml"
        spec_file.write_text("openapi: '3.0.3'")

        result = runner.invoke(
            app,
            [
                "generate",
                "--function",
                "f99",
                "--spec",
                str(spec_file),
                "--output",
                str(tmp_path / "out"),
            ],
        )

        assert result.exit_code == 1
        assert "Unknown function" in result.output


class TestHelpAutoGenerated:
    """Verify --help works for all commands."""

    @pytest.mark.parametrize("cmd", ["generate", "status", "health"])
    def test_help_flag(self, cmd: str) -> None:
        result = runner.invoke(app, [cmd, "--help"])
        assert result.exit_code == 0
        assert "Usage" in result.output or "--help" in result.output
