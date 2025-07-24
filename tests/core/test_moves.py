"""Unit tests for the core game logic, specifically for moves in the game board."""

from py2048.core.models import GameBoard
import pytest


def test_board_can_spawn_tile():
    """Test that a new tile is spawned on the board."""
    board = GameBoard(grid=((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)))
    new_board = board.spawn_tile()
    filled_after_spawn = sum(1 for row in new_board.grid for tile in row if tile != 0)
    assert filled_after_spawn == 1


def test_raises_error_on_invalid_spawn():
    """Test that spawning a tile on a full board raises an error."""
    board = GameBoard(grid=((2, 2, 2, 2), (4, 4, 4, 4), (8, 8, 8, 8), (16, 16, 16, 16)))
    with pytest.raises(Exception):
        board.spawn_tile()


def test_board_can_shift_left():
    """Test that the game board shifts tiles to the left correctly."""
    board = GameBoard(((2, 2, 2, 2), (4, 4, 4, 0), (2, 0, 2, 0), (0, 0, 0, 0)))
    assert board.shift_left() == GameBoard(
        ((4, 4, 0, 0), (8, 4, 0, 0), (4, 0, 0, 0), (0, 0, 0, 0))
    )


def test_board_can_shift_right():
    """Test that the game board shifts tiles to the right correctly."""
    board = GameBoard(((2, 2, 2, 2), (0, 4, 4, 4), (0, 2, 0, 2), (0, 0, 0, 0)))
    assert board.shift_right() == GameBoard(
        ((0, 0, 4, 4), (0, 0, 4, 8), (0, 0, 0, 4), (0, 0, 0, 0))
    )


def test_board_can_shift_up():
    """Test that the game board shifts tiles up correctly."""
    board = GameBoard(((2, 2, 2, 2), (2, 2, 0, 2), (0, 2, 2, 4), (0, 2, 0, 0)))
    assert board.shift_up() == GameBoard(
        ((4, 4, 4, 4), (0, 4, 0, 4), (0, 0, 0, 0), (0, 0, 0, 0))
    )


def test_board_can_shift_down():
    """Test that the game board shifts tiles down correctly."""
    board = GameBoard(((0, 2, 0, 0), (2, 2, 2, 2), (2, 2, 0, 2), (0, 2, 2, 4)))
    assert board.shift_down() == GameBoard(
        ((0, 0, 0, 0), (0, 0, 0, 0), (0, 4, 0, 4), (4, 4, 4, 4))
    )
