"""Unit tests for the core game logic, specifically for moves in the game board."""

from py2048.core.game_board import GameBoard


def test_shift_board_left():
    """Test that the game board shifts tiles to the left correctly."""
    board = GameBoard()
    board.grid = [[2, 2, 0, 0], [4, 4, 0, 0], [2, 0, 2, 0], [0, 0, 0, 0]]
    board.shift_left()
    assert board.grid == [[4, 0, 0, 0], [8, 0, 0, 0], [4, 0, 0, 0], [0, 0, 0, 0]]


def test_shift_board_left_does_not_double_merge():
    """Test that the game board does not double merge tiles."""
    board = GameBoard()
    board.grid = [[2, 2, 2, 2], [4, 4, 4, 0], [2, 0, 2, 0], [0, 0, 0, 0]]
    board.shift_left()
    assert board.grid == [[4, 4, 0, 0], [8, 4, 0, 0], [4, 0, 0, 0], [0, 0, 0, 0]]


def test_shift_board_right():
    """Test that the game board shifts tiles to the right correctly."""
    board = GameBoard()
    board.grid = [[0, 0, 2, 2], [0, 0, 4, 4], [0, 2, 0, 2], [0, 0, 0, 0]]
    board.shift_right()
    assert board.grid == [[0, 0, 0, 4], [0, 0, 0, 8], [0, 0, 0, 4], [0, 0, 0, 0]]


def test_shift_board_right_does_not_double_merge():
    """Test that the game board does not double merge tiles when shifting right."""
    board = GameBoard()
    board.grid = [[2, 2, 2, 2], [0, 4, 4, 4], [0, 2, 0, 2], [0, 0, 0, 0]]
    board.shift_right()
    assert board.grid == [[0, 0, 4, 4], [0, 0, 4, 8], [0, 0, 0, 4], [0, 0, 0, 0]]


def test_shift_board_up():
    """Test that the game board shifts tiles up correctly."""
    board = GameBoard()
    board.grid = [[2, 2, 2, 2], [2, 2, 0, 2], [0, 2, 2, 4], [0, 2, 0, 0]]
    board.shift_up()
    assert board.grid == [[4, 4, 4, 4], [0, 4, 0, 4], [0, 0, 0, 0], [0, 0, 0, 0]]


def test_shift_board_down():
    """Test that the game board shifts tiles down correctly."""
    board = GameBoard()
    board.grid = [[0, 2, 0, 0], [2, 2, 2, 2], [2, 2, 0, 2], [0, 2, 2, 4]]
    board.shift_down()
    assert board.grid == [[0, 0, 0, 0], [0, 0, 0, 0], [0, 4, 0, 4], [4, 4, 4, 4]]
