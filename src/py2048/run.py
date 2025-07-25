"""Unified entry point for Py2048.
This script allows launching the game in CLI, GUI, or Web mode."""

import click

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(
    None, "-v", "--version", prog_name="Py2048", message="%(prog)s version %(version)s"
)
def main():
    """Launch Py2048 in CLI, GIU, or Web mode."""


if __name__ == "__main__":
    main()  # pragma: no cover
