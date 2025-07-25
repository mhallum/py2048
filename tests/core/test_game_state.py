"""Test cases for the GameState class in the py2048 game."""

from py2048.core import models


def test_game_state_initialization():
    """Test that the GameState initializes with a GameBoard."""
    game_state = models.GameState()
    assert game_state.board is not None
    assert isinstance(game_state.board, models.GameBoard)
