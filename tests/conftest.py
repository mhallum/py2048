"""pytest configuration file for the py2048 project."""

import pytest

from py2048.core import models


@pytest.fixture
def test_game() -> models.Py2048Game:
    """Fixture to create a test game instance."""
    board = models.GameBoard(
        grid=((0, 0, 2, 0), (0, 0, 0, 0), (0, 0, 2, 0), (0, 0, 0, 0))
    )
    state = models.GameState(board=board, score=0)
    return models.Py2048Game(game_id="test_game", state=state)
