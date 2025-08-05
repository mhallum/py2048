"""Command module for the 2048 game."""

# pylint: disable=too-few-public-methods

from dataclasses import dataclass


class Command:
    """Base class for commands in the game."""


@dataclass
class StartNewGame(Command):
    """Command to start a new game."""

    game_id: str


@dataclass
class MakeMove(Command):
    """Command to make a move in the game."""

    game_id: str
    direction: str


@dataclass
class ResumeGame(Command):
    """Command to resume a game."""

    game_id: str
