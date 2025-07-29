"""Test cases for the GameState class in the py2048 game."""

from py2048.core import models


def test_game_state_initialization():
    """Test that the GameState initializes with a GameBoard."""
    game_state = models.GameState()
    assert game_state.board is not None
    assert isinstance(game_state.board, models.GameBoard)


def test_game_state_can_list_possible_moves():
    """Test that the GameState can list possible moves."""
    game_state = models.GameState(
        board=models.GameBoard(
            ((2, 4, 8, 16), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0))
        )
    )
    moves = game_state.possible_moves

    assert models.MoveDirection.LEFT not in moves
    assert models.MoveDirection.RIGHT not in moves
    assert models.MoveDirection.UP not in moves
    assert models.MoveDirection.DOWN in moves


def test_game_state_can_check_if_game_over():
    """Test that the GameState can determine if the game is over."""
    game_state = models.GameState(
        board=models.GameBoard(
            ((2, 4, 8, 16), (2, 4, 8, 16), (2, 4, 8, 16), (2, 4, 8, 16))
        )
    )

    assert game_state.is_over is False

    game_state = models.GameState(
        board=models.GameBoard(
            ((2, 4, 8, 16), (4, 8, 16, 32), (8, 16, 32, 64), (16, 32, 64, 128))
        )
    )

    assert game_state.is_over is True
