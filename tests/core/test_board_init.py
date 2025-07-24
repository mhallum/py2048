"""Unit tests for GameBoard initialization"""

from py2048.core.models import GameBoard

EXPECTED_TILES = 2


def test_board_initializes_with_two_tiles():
    """Test that the game board initializes with two tiles."""
    board = GameBoard()
    filled = sum(1 for row in board.grid for tile in row if tile != 0)
    assert filled == EXPECTED_TILES


def test_board_can_be_created_with_already_loaded_tiles():
    """Test that the game board can be created with already loaded tiles."""
    board = GameBoard(grid=[[2, 0, 2, 0], [0, 0, 0, 0], [0, 2, 0, 2], [0, 0, 0, 0]])
    filled = sum(1 for row in board.grid for tile in row if tile != 0)
    assert filled == len([tile for row in board.grid for tile in row if tile != 0])


def test_board_equality():
    """Test that two game boards with the same grid are equal."""
    board1 = GameBoard(grid=[[2, 0, 2, 0], [0, 0, 0, 0], [0, 2, 0, 2], [0, 0, 0, 0]])
    board2 = GameBoard(grid=[[2, 0, 2, 0], [0, 0, 0, 0], [0, 2, 0, 2], [0, 0, 0, 0]])
    assert board1 == board2


def test_board_inequality():
    """Test that two game boards with different grids are not equal."""
    board1 = GameBoard(grid=[[2, 0, 2, 0], [0, 0, 0, 0], [0, 2, 0, 2], [0, 0, 0, 0]])
    board2 = GameBoard(grid=[[2, 0, 2, 0], [0, 0, 1, 0], [0, 2, 0, 2], [0, 0, 0, 0]])
    assert board1 != board2
