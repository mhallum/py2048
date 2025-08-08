"""Scoring logic for the 2048 game.

This module defines the function responsible for calculating the score earned
from a single player move. It compares the game board state before and after
a move, detects which tiles were merged, and computes the total score
contributed by those merges.

Functions:
    determine_score_from_shifted_board: Returns the score based on merged tiles between two board states.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game_board import GameBoard  # pragma: no cover


def determine_score_from_shifted_board(
    before_board: "GameBoard", shifted_board: "GameBoard"
) -> int:
    """Calculate the score gained from merging tiles during a move.

    Compares the tile counts between the board states before and after a move.
    Assumes merges only occur between identical tiles (2048 rules), and merged
    values must be >= 4 to contribute to score.

    Args:
        before_board (GameBoard): The game board before the move.
        shifted_board (GameBoard): The game board after the move.

    Returns:
        int: The score gained from the move, based on merged tiles.
    """

    before_values = before_board.tile_values
    after_values = shifted_board.tile_values

    # Consider all tile values that appeared in either board
    all_tile_values = sorted(before_values | after_values, reverse=True)

    score = 0
    merged_tile_buffer = 0  # Tracks how many source tiles were consumed by merges

    for value in all_tile_values:
        before_count = before_board.get_tile_count(value) - merged_tile_buffer
        after_count = shifted_board.get_tile_count(value)

        if value >= 4 and after_count > before_count:  # pylint: disable=magic-value-comparison
            # If the tile count increased, it means tiles were merged
            # and the score should be updated accordingly
            score += (after_count - before_count) * value
            # Each new tile of this value comes from two merged tiles
            merged_tile_buffer = (after_count - before_count) * 2
        else:
            # If the tile count did not increase, tiles with value value/2 did not merge
            merged_tile_buffer = 0
    return score
