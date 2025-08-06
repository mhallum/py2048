"""Unified entry point for Py2048.
This script allows launching the game in CLI, GUI, or Web mode."""

from enum import Enum
from typing import Literal

import click

import py2048.interfaces.gui.main as gui_main
import py2048.interfaces.web.main as web_main
from py2048.bootstrap import bootstrap
from py2048.interfaces.tui.app import Py2048TUIApp


class Mode(str, Enum):
    """Enumeration for game modes."""

    TERM = "terminal"
    GUI = "gui"
    WEB = "web"


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

bus = bootstrap()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(
    None, "-v", "--version", prog_name="Py2048", message="%(prog)s version %(version)s"
)
@click.option(
    "-m",
    "--mode",
    type=click.Choice([m.value for m in Mode], case_sensitive=False),
    default=Mode.TERM.value,
    help="Select the mode to run the game: terminal, gui, or web.",
)
def main(mode: Literal["terminal", "gui", "web"] = "terminal") -> None:
    """Launch Py2048 in Terminal, GUI, or Web mode."""
    match Mode(mode.lower()):
        case Mode.TERM:
            app = Py2048TUIApp(bus=bus)
            app.run()
        case Mode.GUI:
            gui_main.run_gui()
        case Mode.WEB:
            web_main.run_web()


if __name__ == "__main__":
    main()  # pragma: no cover
