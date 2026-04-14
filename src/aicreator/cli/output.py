"""Rich formatting helpers for CLI output."""

from rich.console import Console
from rich.table import Table

err_console = Console(stderr=True)
console = Console()


def print_error(message: str) -> None:
    """Print error message to stderr in red."""
    err_console.print(f"[bold red]Error:[/bold red] {message}")


def print_success(message: str) -> None:
    """Print success message in green."""
    console.print(f"[bold green]OK[/bold green] {message}")


def print_generation_table(data: dict) -> None:  # type: ignore[type-arg]
    """Display generation metadata as a Rich table."""
    table = Table(title="Generation Details", show_header=True)
    table.add_column("Field", style="bold cyan")
    table.add_column("Value")

    field_order = [
        ("id", "ID"),
        ("function", "Function"),
        ("language", "Language"),
        ("spec_type", "Spec Type"),
        ("status", "Status"),
        ("input_hash", "Input Hash"),
        ("created_at", "Created At"),
        ("completed_at", "Completed At"),
        ("duration_ms", "Duration (ms)"),
        ("error", "Error"),
    ]

    for key, label in field_order:
        value = data.get(key)
        if value is None:
            value = "-"
        table.add_row(label, str(value))

    console.print(table)
