"""CLI for the Py2048 game."""

import click

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(
    None, "-v", "--version", prog_name="Py2048", message="%(prog)s version %(version)s"
)
def py2048():
    """Py2048 is a Python implementation of the popular 2048 sliding puzzle game."""


if __name__ == "__main__":
    py2048()  # pragma: no cover
