"""E2E tests for F1: Proto → Go code generation."""

import json
import zipfile
from io import BytesIO
from pathlib import Path

import httpx


class TestF1ProtoGoGeneration:
    """Upload proto specs → receive ZIP → extract → contains .go files."""

    def test_generates_go_files_from_proto(self, api_url: str, proto_specs_dir: Path, tmp_path: Path) -> None:
        """F1 E2E: upload proto specs, verify ZIP contains .go files with protobuf types."""
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

        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        assert resp.headers["content-type"] == "application/zip"

        gen_id = resp.headers.get("X-Generation-ID")
        assert gen_id is not None

        # Extract and verify .go files
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        with zipfile.ZipFile(BytesIO(resp.content)) as zf:
            zf.extractall(output_dir)

        go_files = list(output_dir.rglob("*.go"))
        assert len(go_files) > 0, "Expected at least one .go file in generated output"

        # Verify protobuf type names from our fixtures exist in generated code
        all_go_content = "\n".join(f.read_text() for f in go_files)
        assert "Order" in all_go_content or "order" in all_go_content, "Expected Order type in generated Go code"

    def test_determinism_same_hash(self, api_url: str, proto_specs_dir: Path) -> None:
        """P1 Determinism: same input produces same input_hash."""
        files = []
        for f in sorted(proto_specs_dir.iterdir()):
            if f.is_file():
                files.append(("files", (f.name, f.read_bytes())))

        metadata = json.dumps({"function": "f1", "language": "go", "spec_type": "proto"})

        ids = []
        with httpx.Client(timeout=120.0) as client:
            for _ in range(2):
                # Re-create files list each time (httpx consumes file objects)
                run_files = []
                for f in sorted(proto_specs_dir.iterdir()):
                    if f.is_file():
                        run_files.append(("files", (f.name, f.read_bytes())))

                resp = client.post(
                    f"{api_url}/api/v1/generate",
                    files=run_files,
                    data={"metadata": metadata},
                )
                assert resp.status_code == 200
                ids.append(resp.headers["X-Generation-ID"])

            # Fetch both generation records and compare input_hash
            hashes = []
            for gen_id in ids:
                status_resp = client.get(f"{api_url}/api/v1/generations/{gen_id}")
                assert status_resp.status_code == 200
                hashes.append(status_resp.json()["input_hash"])

        assert hashes[0] == hashes[1], f"Input hashes differ: {hashes[0]} vs {hashes[1]}"
