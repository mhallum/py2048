"""Command module for the 2048 game."""

# pylint: disable=too-few-public-methods

from dataclasses import dataclass


class Command:
    """Base class for commands in the game."""


@dataclass
class StartNewGame(Command):
    """Command to start a new game."""

    game_id: str
