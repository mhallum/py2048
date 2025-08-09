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


def query_high_score(uow: unit_of_work.AbstractUnitOfWork) -> int:
    """Get the high score from the game records.

    Args:
        uow (unit_of_work.AbstractUnitOfWork): The unit of work for database operations

    Returns:
        int: The highest score recorded in the game records.
    """

    if not (records := uow.records.list()):
        return 0
    return max(record.final_score for record in records)


def final_score_query(
    uow: unit_of_work.AbstractUnitOfWork, game_uuid: str
) -> int | None:
    """Get the final score of a game by its UUID.

    Args:
        uow (unit_of_work.AbstractUnitOfWork): The unit of work for database operations
        game_uuid (str): The UUID of the game to retrieve the final score for

    Returns:
        int: The final score of the game, or None if the game is not found.
    """
    record = uow.records.get(game_uuid)
    return record.final_score if record else None


def query_game_screen_values_by_slot(
    slot_id: str, uow: unit_of_work.AbstractUnitOfWork
) -> GameScreenDTO | None:
    """Get the values needed to display the game in the given slot to the game screen.

    Args:
        slot_id (str): The identifier for the game slot.
        uow (unit_of_work.AbstractUnitOfWork): The unit of work for database operations
    """

    if not (game := uow.games.get(slot_id)):
        return None
    grid = game.state.board.grid
    score = game.state.score
    return GameScreenDTO(grid=grid, score=score)
