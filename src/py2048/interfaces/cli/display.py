"""This module provides the display interface for the CLI version of Py2048."""

from dataclasses import dataclass

from blessed import Terminal
from rich.console import Console

# pylint: disable=too-few-public-methods


@dataclass
class DisplayIO:
    """Encapsulates the terminal and console for display purposes."""

    term: Terminal
    console: Console
