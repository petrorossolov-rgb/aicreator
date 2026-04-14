"""E2E tests for error handling — invalid inputs and unsupported combinations."""

import json
import subprocess
from pathlib import Path

import httpx


class TestInvalidProtoInput:
    """Upload broken proto specs → receive error response."""

    def test_broken_proto_returns_error(self, api_url: str, invalid_proto_dir: Path) -> None:
        """Error E2E: upload broken proto → receive 500 with error mentioning parse error."""
        files = []
        for f in sorted(invalid_proto_dir.iterdir()):
            if f.is_file():
                files.append(("files", (f.name, f.read_bytes())))

        metadata = json.dumps({"function": "f1", "language": "go", "spec_type": "proto"})

        with httpx.Client(timeout=120.0) as client:
            resp = client.post(
                f"{api_url}/api/v1/generate",
                files=files,
                data={"metadata": metadata},
            )

        assert resp.status_code == 500, f"Expected 500 for broken proto, got {resp.status_code}"
        detail = resp.json().get("detail", "")
        assert detail, "Expected error detail in response"


class TestUnsupportedCombination:
    """Unsupported spec_type/language/function → 400."""

    def test_asyncapi_returns_400(self, api_url: str) -> None:
        """Error E2E: unsupported combination → receive 400."""
        files = [("files", ("spec.yaml", b"asyncapi: '2.0.0'"))]
        metadata = json.dumps({"function": "f1", "language": "go", "spec_type": "asyncapi"})

        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{api_url}/api/v1/generate",
                files=files,
                data={"metadata": metadata},
            )

        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
        assert "No generator registered" in resp.json().get("detail", "")


class TestCliE2E:
    """CLI end-to-end: aicreator generate + status via subprocess."""

    def test_cli_generate_produces_files(self, api_url: str, proto_specs_dir: Path, tmp_path: Path) -> None:
        """CLI E2E: aicreator generate --function f1 produces files."""
        output_dir = tmp_path / "cli_output"

        result = subprocess.run(
            [
                "uv",
                "run",
                "aicreator",
                "generate",
                "--function",
                "f1",
                "--spec",
                str(proto_specs_dir),
                "--output",
                str(output_dir),
                "--api-url",
                api_url,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        assert result.returncode == 0, f"CLI failed: {result.stderr}\n{result.stdout}"
        assert output_dir.exists()

        go_files = list(output_dir.rglob("*.go"))
        assert len(go_files) > 0, f"Expected .go files in {output_dir}"

    def test_cli_status_after_generate(self, api_url: str, proto_specs_dir: Path, tmp_path: Path) -> None:
        """Status E2E: after generation, aicreator status {id} shows completed."""
        # First, generate via API to get a generation ID
        files = []
        for f in sorted(proto_specs_dir.iterdir()):
            if f.is_file():
                files.append(("files", (f.name, f.read_bytes())))

        metadata = json.dumps({"function": "f1", "language": "go", "spec_type": "proto"})

        with httpx.Client(timeout=120.0) as client:
            resp = client.post(
                f"{api_url}/api/v1/generate",
                files=files,
                data={"metadata": metadata},
            )

        assert resp.status_code == 200
        gen_id = resp.headers["X-Generation-ID"]

        # Now check status via CLI
        result = subprocess.run(
            [
                "uv",
                "run",
                "aicreator",
                "status",
                gen_id,
                "--api-url",
                api_url,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"CLI status failed: {result.stderr}\n{result.stdout}"
        assert "completed" in result.stdout.lower(), f"Expected 'completed' in output: {result.stdout}"
