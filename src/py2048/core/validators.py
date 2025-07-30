"""Validators for the 2048 game core module."""

from typing import TYPE_CHECKING


from py2048.core.exceptions import InvalidGameBoard

if TYPE_CHECKING:
    from py2048.core.models import GameBoard  # pragma: no cover


# ============================================================================
# Game Board Validators
# ============================================================================


def validate_game_board_shape(board: "GameBoard") -> None:
    """Validate that the game board has a consistent shape."""
    if not all(len(row) == len(board.grid[0]) for row in board.grid):
        raise InvalidGameBoard("All rows in the game board must have the same length.")


def validate_game_board_tile_values(board: "GameBoard") -> None:
    """Validate that all tiles in the game board are 0 or a power of two."""
    for value in board.tile_values:
        if value < 0:
            raise InvalidGameBoard(
                f"Invalid tile value: {value}. Must be non-negative."
            )
        if value != 0 and (value & (value - 1)) != 0:
            raise InvalidGameBoard(
                f"Invalid tile value: {value}. Must be 0 or a power of two."
            )
