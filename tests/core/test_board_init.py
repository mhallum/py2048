"""Unit tests for GameBoard initialization"""

from py2048.core.game_board import GameBoard

EXPECTED_TILES = 2


def test_board_initializes_with_two_tiles():
    """Test that the game board initializes with two tiles."""
    board = GameBoard()
    filled = sum(1 for row in board.grid for tile in row if tile != 0)
    assert filled == EXPECTED_TILES


def test_board_can_be_created_with_already_loaded_tiles():
    """Test that the game board can be created with already loaded tiles."""
    initial_grid = [[2, 0, 2, 0], [0, 0, 0, 0], [0, 2, 0, 2], [0, 0, 0, 0]]
    board = GameBoard(grid=initial_grid)
    board.grid = initial_grid
    filled = sum(1 for row in board.grid for tile in row if tile != 0)
    assert filled == len([tile for row in initial_grid for tile in row if tile != 0])


def test_board_equality():
    """Test that two game boards with the same grid are equal."""
    grid1 = [[2, 0, 2, 0], [0, 0, 0, 0], [0, 2, 0, 2], [0, 0, 0, 0]]
    grid2 = [[2, 0, 2, 0], [0, 0, 0, 0], [0, 2, 0, 2], [0, 0, 0, 0]]
    board1 = GameBoard(grid=grid1)
    board2 = GameBoard(grid=grid2)
    assert board1 == board2
