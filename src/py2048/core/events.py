"""Event classes for the 2048 game."""

# pylint: disable=too-few-public-methods

from dataclasses import dataclass


class Event:
    """Base class for all events in the game."""


@dataclass
class NewGameStarted(Event):
    """Event triggered when a new game is started."""

    game_id: str


@dataclass
class GameOver(Event):
    """Event triggered when the game is over."""

    game_id: str
    score: int
    final_grid: tuple[tuple[int, ...], ...]
