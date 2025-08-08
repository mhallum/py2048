"""Encapsulates a move made during a 2048 game.

This module defines the `Move` class, which represents a single move action
taken by the player. Each move captures the direction and the game state
before and after the move, enabling undo functionality and move history tracking.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game_state import GameState, MoveDirection  # pragma: no cover


@dataclass(frozen=True)
class Move:
    """Represents a single move taken during a 2048 game.

    Each Move captures:
    - The direction of the move.
    - The game state before the move.
    - The resulting game state after the move.

    Moves are used to support features like undo and move history tracking.

    Attributes:
        direction (MoveDirection): The direction of the move (left, right, up, or down).
        before_state (GameState): The game state before the move was applied.
        after_state (GameState): The resulting game state after the move.
    """

    direction: "MoveDirection"
    before_state: "GameState"
    after_state: "GameState"
