"""Unit tests for GameBoard initialization"""

from py2048.core.game_board import GameBoard

EXPECTED_TILES = 2


def test_board_initializes_with_two_tiles():
    """Test that the game board initializes with two tiles."""
    board = GameBoard()
    filled = sum(1 for row in board.grid for tile in row if tile != 0)
    assert filled == EXPECTED_TILES
