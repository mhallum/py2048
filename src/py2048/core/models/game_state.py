"""Value object representing a snapshot of the 2048 game.

This module defines the `GameState` class, which captures the immutable state
of the game at a particular moment — including the board configuration and score.
It provides logic for determining legal moves and detecting game-over conditions.
"""

from dataclasses import dataclass
from functools import cached_property

from .game_board import GameBoard, MoveDirection


@dataclass(frozen=True)
class GameState:
    """Class representing the state of the 2048 game.

    Attributes:
        board (GameBoard): The current state of the game board.
        score (int): The current score of the game.

    Properties:
        possible_moves (list[MoveDirection]): Returns a list of directions where moves are possible,
            determined by checking if shifting the board in any direction results in a change.
        is_over (bool): Indicates whether the game is over, which occurs when no moves are possible.
    """

    board: GameBoard = GameBoard()
    score: int = 0

    @cached_property
    def possible_moves(self) -> list[MoveDirection]:
        """Return a list of possible moves based on the current board state.

        Checks if the board can be shifted in any direction (left, right, up, down)
        by attempting to shift and checking if the resulting board is different.

        Returns:
            list[MoveDirection]: A list of directions where moves are possible.
        """
        possible_moves: list[MoveDirection] = []
        for direction in MoveDirection:
            if getattr(self.board, f"shift_{direction.value}")() != self.board:
                possible_moves.append(direction)
        return possible_moves

    @cached_property
    def is_over(self) -> bool:
        """Check if the game is over.

        The game is considered over if there are no possible moves left.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        return not self.possible_moves
