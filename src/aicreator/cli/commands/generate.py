"""aicreator generate — run code generation via API."""

import json
import zipfile
from io import BytesIO
from pathlib import Path

import httpx
import typer
from rich.console import Console

from aicreator.cli.output import print_error, print_success

FUNCTION_SPEC_MAP: dict[str, str] = {
    "f1": "proto",
    "f2": "openapi",
    "f4": "openapi",
}

console = Console(stderr=True)


def generate(
    function: str = typer.Option(..., "--function", "-f", help="Generation function: f1, f2, or f4"),
    spec: Path = typer.Option(..., "--spec", "-s", help="Path to spec file or directory"),
    output: Path = typer.Option(..., "--output", "-o", help="Output directory for generated files"),
    language: str = typer.Option("go", "--language", "-l", help="Target language"),
    api_url: str = typer.Option("http://localhost:8000", "--api-url", help="API base URL"),
) -> None:
    """Run code generation from specifications."""
    spec_type = FUNCTION_SPEC_MAP.get(function)
    if spec_type is None:
        print_error(f"Unknown function '{function}'. Supported: {', '.join(FUNCTION_SPEC_MAP)}")
        raise typer.Exit(code=1)

    if not spec.exists():
        print_error(f"Spec path does not exist: {spec}")
        raise typer.Exit(code=1)

    # Collect files to upload
    files_to_upload: list[tuple[str, tuple[str, bytes]]] = []
    if spec.is_dir():
        for file_path in sorted(spec.iterdir()):
            if file_path.is_file():
                files_to_upload.append(("files", (file_path.name, file_path.read_bytes())))
    else:
        files_to_upload.append(("files", (spec.name, spec.read_bytes())))

    if not files_to_upload:
        print_error(f"No files found in {spec}")
        raise typer.Exit(code=1)

    metadata = json.dumps({"function": function, "language": language, "spec_type": spec_type})

    url = f"{api_url.rstrip('/')}/api/v1/generate"

    with console.status("[bold cyan]Generating code..."):
        try:
            with httpx.Client(timeout=300.0) as client:
                response = client.post(url, files=files_to_upload, data={"metadata": metadata})
        except httpx.ConnectError:
            print_error(f"Cannot connect to API at {api_url}. Is the server running?")
            raise typer.Exit(code=1)

    if response.status_code != 200:
        content_type = response.headers.get("content-type", "")
        if content_type.startswith("application/json"):
            detail = response.json().get("detail", response.text)
        else:
            detail = response.text
        print_error(f"API error ({response.status_code}): {detail}")
        raise typer.Exit(code=1)

    # Extract ZIP to output directory
    output.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(BytesIO(response.content)) as zf:
        zf.extractall(output)

    gen_id = response.headers.get("X-Generation-ID", "unknown")
    file_count = len(zipfile.ZipFile(BytesIO(response.content)).namelist())

    print_success(f"Generated {file_count} files → {output}")
    console.print(f"  Generation ID: [bold]{gen_id}[/bold]", highlight=False)
