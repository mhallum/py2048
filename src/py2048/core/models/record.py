"""Defines the GameRecord data model for tracking completed games in Py2048.

A GameRecord captures summary statistics of a finished game, including
its unique identifier, final score, highest tile reached, and number of moves.

This model is intended for tracking player statistics.
It is immutable and should be created only when a game has ended.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GameRecord:
    """Immutable record of a completed Py2048 game.

    Attributes:
        game_uuid: Unique ID of the completed game.
        final_score: The score at the end of the game.
        max_tile: The largest tile reached during the game.
        number_of_moves: Total number of moves made.
    """

    game_uuid: str
    final_score: int
    max_tile: int
    number_of_moves: int
