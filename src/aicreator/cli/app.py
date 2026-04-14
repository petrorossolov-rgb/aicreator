"""CLI entry point for aicreator."""

import typer

from aicreator import __version__
from aicreator.cli.commands.generate import generate
from aicreator.cli.commands.health import health
from aicreator.cli.commands.status import status

app = typer.Typer(
    name="aicreator",
    help="AICreator — deterministic code generation from specifications.",
    no_args_is_help=True,
)

app.command("generate")(generate)
app.command("status")(status)
app.command("health")(health)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"aicreator {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-V", callback=version_callback, is_eager=True, help="Show version"
    ),
) -> None:
    """AICreator CLI."""
