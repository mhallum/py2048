"""Views for the 2048 game, providing game board and screen values."""

from typing import TypedDict

from py2048.service_layer import unit_of_work


class GameScreenValues(TypedDict):
    """Typed dictionary for game screen values."""

    board: tuple[tuple[int, ...], ...]
    score: int
    high_score: int


def game_screen_values(
    game_id: str, uow: unit_of_work.AbstractUnitOfWork
) -> GameScreenValues:
    """Get the game screen values for a specific game ID."""

    game = uow.games.get(game_id)
    board = game.state.board.grid
    score = game.state.score
    high_score = 0  # Placeholder for high score, will be implemented later
    return {"board": board, "score": score, "high_score": high_score}
