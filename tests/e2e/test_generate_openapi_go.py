"""E2E tests for F2 (OpenAPI → Go server) and F4 (OpenAPI → Go client)."""

import json
import zipfile
from io import BytesIO
from pathlib import Path

import httpx


class TestF2OpenAPIGoServer:
    """Upload OpenAPI spec → receive ZIP → contains Go server with mux router."""

    def test_generates_go_server(self, api_url: str, openapi_spec_path: Path, tmp_path: Path) -> None:
        files = [("files", (openapi_spec_path.name, openapi_spec_path.read_bytes()))]
        metadata = json.dumps({"function": "f2", "language": "go", "spec_type": "openapi"})

        with httpx.Client(timeout=120.0) as client:
            resp = client.post(
                f"{api_url}/api/v1/generate",
                files=files,
                data={"metadata": metadata},
            )

        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

        output_dir = tmp_path / "server"
        output_dir.mkdir()
        with zipfile.ZipFile(BytesIO(resp.content)) as zf:
            zf.extractall(output_dir)

        go_files = list(output_dir.rglob("*.go"))
        assert len(go_files) > 0, "Expected Go server files"

        # Verify server-specific content (mux router)
        all_content = "\n".join(f.read_text() for f in go_files)
        assert (
            "mux" in all_content.lower() or "router" in all_content.lower() or "Route" in all_content
        ), "Expected mux router references in Go server code"


class TestF4OpenAPIGoClient:
    """Upload OpenAPI spec → receive ZIP → contains Go client."""

    def test_generates_go_client(self, api_url: str, openapi_spec_path: Path, tmp_path: Path) -> None:
        files = [("files", (openapi_spec_path.name, openapi_spec_path.read_bytes()))]
        metadata = json.dumps({"function": "f4", "language": "go", "spec_type": "openapi"})

        with httpx.Client(timeout=120.0) as client:
            resp = client.post(
                f"{api_url}/api/v1/generate",
                files=files,
                data={"metadata": metadata},
            )

        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

        output_dir = tmp_path / "client"
        output_dir.mkdir()
        with zipfile.ZipFile(BytesIO(resp.content)) as zf:
            zf.extractall(output_dir)

        go_files = list(output_dir.rglob("*.go"))
        assert len(go_files) > 0, "Expected Go client files"

        # Verify client-specific content
        all_content = "\n".join(f.read_text() for f in go_files)
        assert (
            "Client" in all_content or "client" in all_content or "http" in all_content
        ), "Expected client references in Go client code"
