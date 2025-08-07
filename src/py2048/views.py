"""Views for the 2048 game, providing game board and screen values."""

from dataclasses import dataclass
from enum import Enum

from py2048.service_layer import unit_of_work

# pylint: disable=too-few-public-methods


class GameStatus(str, Enum):
    """Enumeration for game status."""

    NEW = "new"
    IN_PROGRESS = "in_progress"
    OVER = "over"


@dataclass(frozen=True)
class GameScreenDTO:
    """Data Transfer Object for values to be displayed on the game screen."""

    grid: tuple[tuple[int, ...], ...]
    score: int
    high_score: int
    status: GameStatus


def game_screen_values(
    game_id: str, uow: unit_of_work.AbstractUnitOfWork
) -> GameScreenDTO:
    """Get the game screen values for a specific game ID."""

    game = uow.games.get(game_id)
    grid = game.state.board.grid
    score = game.state.score
    high_score = 0  # Placeholder for high score, will be implemented later
    if game.is_over:
        status = GameStatus.OVER
    elif len(game.moves) == 0:
        status = GameStatus.NEW
    else:
        status = GameStatus.IN_PROGRESS
    return GameScreenDTO(grid=grid, score=score, high_score=high_score, status=status)
