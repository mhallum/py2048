"""Unified entry point for Py2048.
This script allows launching the game in CLI, GUI, or Web mode."""

from typing import Literal
from enum import Enum

import click

import py2048.interfaces.cli.main as cli_main
import py2048.interfaces.gui.main as gui_main
import py2048.interfaces.web.main as web_main


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
            cli_main.run_cli()
        case Mode.GUI:
            gui_main.run_gui()
        case Mode.WEB:
            web_main.run_web()


if __name__ == "__main__":
    main()  # pragma: no cover
