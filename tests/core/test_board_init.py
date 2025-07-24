"""Unit tests for GameBoard initialization"""

from py2048.core import models
from py2048.core.models import GameBoard

EXPECTED_TILES = 2


def test_spawn_tile_on_empty_board():
    """Test that a new tile is spawned on the board on an empty board."""
    board = GameBoard(grid=[[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
    new_board = models.spawn_tile(board)
    filled_after_spawn = sum(1 for row in new_board.grid for tile in row if tile != 0)
    assert filled_after_spawn == 1


def new_test_spawn_tile_on_non_empty_board():
    """Test that a new tile is spawned on the board on a non-empty board."""
    board = GameBoard(grid=[[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
    new_board = models.spawn_tile(board)
    filled_after_spawn = sum(1 for row in new_board.grid for tile in row if tile != 0)
    expected_n_tiles = 2
    assert filled_after_spawn == expected_n_tiles


def test_board_initializes_with_empty_grid_by_default():
    """Test that the game board initializes with an empty grid."""
    board = GameBoard()
    filled = sum(1 for row in board.grid for tile in row if tile != 0)
    assert filled == 0


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
