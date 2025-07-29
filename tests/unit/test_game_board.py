"""Unit tests for the core game logic, specifically for moves in the game board."""

import pytest

from py2048.core.models import GameBoard, determine_score_from_shifted_board


def test_determine_score_from_shifted_board_helper_function():
    """Test score calculation from a shifted board."""
    before_board = GameBoard(
        grid=((2, 2, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0))
    )
    shifted_board = GameBoard(
        grid=((4, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0))
    )
    score = determine_score_from_shifted_board(before_board, shifted_board)
    assert score == 4  # pylint: disable=magic-value-comparison


def test_board_initializes_with_empty_grid_by_default():
    """Test that the game board initializes with an empty grid."""
    board = GameBoard()
    filled = sum(1 for row in board.grid for tile in row if tile != 0)
    assert filled == 0


def test_board_can_be_created_with_already_loaded_tiles():
    """Test that the game board can be created with already loaded tiles."""
    board = GameBoard(grid=((2, 0, 2, 0), (0, 0, 0, 0), (0, 2, 0, 2), (0, 0, 0, 0)))
    filled = sum(1 for row in board.grid for tile in row if tile != 0)
    assert filled == len([tile for row in board.grid for tile in row if tile != 0])


def test_board_will_not_initialize_with_invalid_grid():
    """Test that the game board raises an error when initialized with inconsistant row lengths."""
    with pytest.raises(ValueError):
        GameBoard(grid=((2, 0, 2), (0, 0, 0, 0), (0, 2, 0, 2), (0, 0, 0, 0)))


def test_board_will_not_initialize_with_invalid_tile_values():
    """Test that the game board raises an error when initialized with invalid tile values."""
    with pytest.raises(ValueError):
        GameBoard(grid=((2, 0, 2, 0), (0, 0, 0, 0), (0, 2, 1, 2), (0, 0, 0, 0)))


def test_board_equality():
    """Test that two game boards with the same grid are equal."""
    board1 = GameBoard(grid=((2, 0, 2, 0), (0, 0, 0, 0), (0, 2, 0, 2), (0, 0, 0, 0)))
    board2 = GameBoard(grid=((2, 0, 2, 0), (0, 0, 0, 0), (0, 2, 0, 2), (0, 0, 0, 0)))
    assert board1 == board2


def test_board_inequality():
    """Test that two game boards with different grids are not equal."""
    board1 = GameBoard(grid=((2, 0, 2, 0), (0, 0, 0, 0), (0, 2, 0, 2), (0, 0, 0, 0)))
    board2 = GameBoard(grid=((2, 0, 2, 0), (0, 0, 4, 0), (0, 2, 0, 2), (0, 0, 0, 0)))
    assert board1 != board2


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


def test_board_can_get_all_tile_values():
    """Test that the game board can retrieve all tile values."""
    board = GameBoard(((2, 0, 2, 0), (0, 0, 4, 0), (0, 2, 0, 2), (0, 0, 16, 0)))
    assert board.tile_values == {2, 4, 16}


def test_board_can_get_tile_count():
    """Test that the game board can count tiles of a specific value."""
    board = GameBoard(((2, 0, 2, 0), (0, 0, 0, 0), (0, 2, 0, 2), (0, 0, 0, 0)))
    count_2 = board.get_tile_count(2)
    count_4 = board.get_tile_count(4)
    assert count_2 == 4  # pylint: disable=magic-value-comparison
    assert count_4 == 0
