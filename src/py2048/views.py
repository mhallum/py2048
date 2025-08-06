"""Views for the 2048 game, providing game board and screen values."""

from enum import Enum
from typing import TypedDict

from py2048.service_layer import unit_of_work


class GameScreenValues(TypedDict):
    """Typed dictionary for game screen values."""

    grid: tuple[tuple[int, ...], ...]
    score: int
    high_score: int


class GameStatus(str, Enum):
    """Enumeration for game status."""

    NEW = "new"
    IN_PROGRESS = "in_progress"
    OVER = "over"


def game_screen_values(
    game_id: str, uow: unit_of_work.AbstractUnitOfWork
) -> GameScreenValues:
    """Get the game screen values for a specific game ID."""

    game = uow.games.get(game_id)
    grid = game.state.board.grid
    score = game.state.score
    high_score = 0  # Placeholder for high score, will be implemented later
    return {"grid": grid, "score": score, "high_score": high_score}


def game_status(game_id: str, uow: unit_of_work.AbstractUnitOfWork) -> GameStatus:
    """Get the status of the game."""
    game = uow.games.get(game_id)
    if game.is_over:
        return GameStatus.OVER
    if len(game.moves) == 0:
        return GameStatus.NEW
    return GameStatus.IN_PROGRESS
