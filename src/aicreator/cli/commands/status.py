"""aicreator status — check generation status via API."""

import httpx
import typer
from rich.console import Console

from aicreator.cli.output import print_error, print_generation_table

console = Console(stderr=True)


def status(
    generation_id: str = typer.Argument(..., help="Generation UUID"),
    api_url: str = typer.Option("http://localhost:8000", "--api-url", help="API base URL"),
) -> None:
    """Display generation status and metadata."""
    url = f"{api_url.rstrip('/')}/api/v1/generations/{generation_id}"

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url)
    except httpx.ConnectError:
        print_error(f"Cannot connect to API at {api_url}. Is the server running?")
        raise typer.Exit(code=1)

    if response.status_code == 404:
        print_error(f"Generation {generation_id} not found")
        raise typer.Exit(code=1)

    if response.status_code == 422:
        print_error(f"Invalid generation ID: {generation_id}")
        raise typer.Exit(code=1)

    if response.status_code != 200:
        print_error(f"API error ({response.status_code}): {response.text}")
        raise typer.Exit(code=1)

    print_generation_table(response.json())
