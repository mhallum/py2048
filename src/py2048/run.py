"""Unified entry point for Py2048.
This script allows launching the game in CLI, GUI, or Web mode."""

from typing import Literal
from enum import Enum

import click


class Mode(str, Enum):
    """Enumeration for game modes."""

    CLI = "cli"
    GUI = "gui"
    WEB = "web"


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(
    None, "-v", "--version", prog_name="Py2048", message="%(prog)s version %(version)s"
)
@click.option(
    "-m",
    "--mode",
    type=click.Choice([m.value for m in Mode], case_sensitive=False),
    default=Mode.CLI.value,
    help="Select the mode to run the game: CLI, GUI, or Web.",
)
def main(mode: Literal["cli", "gui", "web"] = "cli") -> None:
    """Launch Py2048 in CLI, GUI, or Web mode."""
    match Mode(mode.lower()):
        case Mode.CLI:
            click.echo("Launching Py2048 in CLI mode")
            # call_cli()
        case Mode.GUI:
            click.echo("Launching Py2048 in GUI mode (Coming soon)")
            # call_gui()
        case Mode.WEB:
            click.echo("Launching Py2048 in Web mode (Coming soon)")
            # call_web()
        case _:
            click.echo("Invalid mode selected.")


if __name__ == "__main__":
    main()  # pragma: no cover
