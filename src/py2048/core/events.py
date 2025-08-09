"""Event classes for the 2048 game."""

# pylint: disable=too-few-public-methods

from dataclasses import dataclass


class Event:
    """Base class for all events in the game."""


@dataclass
class NewGameStarted(Event):
    """Event triggered when a new game is started."""

    slot_id: str
    game_uuid: str


@dataclass
class GameOver(Event):
    """Event triggered when the game is over."""

    slot_id: str
    game_uuid: str
    final_score: int
    max_tile: int
    number_of_moves: int
