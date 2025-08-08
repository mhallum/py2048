"""Core domain models for the Py2048 game.

This package defines the fundamental types that form the heart of the 2048 game domain,
including the game board, game state, move logic, and aggregate root.

Modules:
    - game_board: Immutable 2D grid representing the 2048 board and tile shifting logic.
    - game_state: Snapshot of the current board and score, with game-over detection.
    - move: Records individual directional moves and resulting state transitions.
    - py2048_game: Aggregate root encapsulating gameplay, move history, and domain events.

Exports:
    Move: A single directional move.
    MoveDirection: Enum representing up/down/left/right directions.
    GameBoard: The 2D grid model with shift/spawn behavior.
    GameState: Immutable container for board and score.
    Py2048Game: Aggregate root managing the full game session lifecycle.
"""

from .game_board import GameBoard, MoveDirection
from .game_state import GameState
from .move import Move
from .py2048_game import Py2048Game

__all__ = ["Move", "MoveDirection", "GameBoard", "GameState", "Py2048Game"]
