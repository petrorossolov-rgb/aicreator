"""aicreator health — check API health."""

import httpx
import typer
from rich.console import Console

from aicreator.cli.output import print_error, print_success

console = Console(stderr=True)


def health(
    api_url: str = typer.Option("http://localhost:8000", "--api-url", help="API base URL"),
) -> None:
    """Check API health status."""
    url = f"{api_url.rstrip('/')}/api/v1/health"

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
    except httpx.ConnectError:
        print_error(f"Cannot connect to API at {api_url}. Is the server running?")
        raise typer.Exit(code=1)

    if response.status_code != 200:
        print_error(f"API unhealthy ({response.status_code}): {response.text}")
        raise typer.Exit(code=1)

    data = response.json()
    print_success(f"API healthy — version {data.get('version', 'unknown')}")
