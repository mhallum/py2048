"""Unit tests for the main Game model in the py2048 game."""

import pytest

from py2048.core import models
from py2048.core.exceptions import InvalidMove

EXPECTED_INITIAL_TILES = 2


def test_can_create_new_game():
    """Test the creation of a new game using the Py2048Game.create_new_game() class method.

    This test verifies that:
    - The game board is initialized with the expected number of non-zero tiles.
    - The initial score is set to zero.
    - The moves history is empty upon game creation.
    """

    new_game = models.Py2048Game.create_new_game("test_game")

    # Check that the game board is initialized with two tiles
    filled = sum(1 for row in new_game.state.board.grid for tile in row if tile != 0)
    assert filled == EXPECTED_INITIAL_TILES

    # Check that the initial score is 0
    assert new_game.state.score == 0

    # Check that the moves history is empty
    assert len(new_game.moves) == 0


def test_game_hashes_and_equality_based_on_game_uuid():
    """Test that Py2048Game objects with the same uuid have the same hash."""
    game_uuid = "game_123"
    board = models.GameBoard()
    state = models.GameState(board=board, score=0)

    game1 = models.Py2048Game(game_uuid=game_uuid, state=state)
    game2 = models.Py2048Game(game_uuid=game_uuid, state=state)
    game3 = models.Py2048Game(game_uuid="game_456", state=state)

    assert hash(game1) == hash(game2)
    assert game1 == game2
    assert hash(game1) != hash(game3)
    assert game1 != game3
    some_string = "not a game"
    assert game1 != some_string


def test_game_can_be_used_in_set():
    """Test that Py2048Game objects are hashable and can be added to a set."""
    state = models.GameState(board=models.GameBoard(), score=0)

    game = models.Py2048Game(state=state)
    games = {game}

    assert game in games


def test_can_make_move():
    """Test making a move in the game."""
    initial_board = models.GameBoard(
        grid=((2, 0, 2, 0), (0, 0, 0, 0), (0, 2, 0, 2), (0, 0, 0, 0))
    )
    initial_state = models.GameState(board=initial_board, score=0)
    game = models.Py2048Game(state=initial_state, moves=[])

    # Make a move
    game.move(models.MoveDirection.LEFT)

    # Check that a move was recorded
    assert len(game.moves) == 1

    # Check that the score has been updated
    expected_score = 8  # 4 + 4 from the merges
    assert game.state.score == expected_score

    # Check that a tile was spawned
    filled = sum(1 for row in game.state.board.grid for tile in row if tile != 0)
    expected_num_tiles_after_merging = 2
    assert filled == expected_num_tiles_after_merging + 1  # One tile should be spawned

    # Check that the game state has been updated
    assert game.state != initial_state


@pytest.mark.parametrize(
    "direction",
    [
        models.MoveDirection.UP,
        models.MoveDirection.DOWN,
        models.MoveDirection.LEFT,
        models.MoveDirection.RIGHT,
    ],
)
def test_error_is_raised_on_attempt_to_move_after_game_over(
    direction: models.MoveDirection,
):
    """Test that an error is raised when trying to make a move after the game is over."""
    board = models.GameBoard(
        grid=((2, 4, 8, 16), (4, 8, 32, 64), (2, 4, 8, 16), (4, 8, 32, 64))
    )
    state = models.GameState(board=board)
    game = models.Py2048Game(state=state)

    # Attempt to make a move after the game is over
    with pytest.raises(InvalidMove):
        game.move(direction)


@pytest.mark.parametrize(
    "grid, direction",
    [
        (
            ((2, 0, 2, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
            models.MoveDirection.UP,
        ),
        (
            ((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (2, 0, 0, 2)),
            models.MoveDirection.DOWN,
        ),
        (
            ((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (2, 4, 2, 0)),
            models.MoveDirection.LEFT,
        ),
        (
            ((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 2, 4)),
            models.MoveDirection.RIGHT,
        ),
    ],
)
def test_move_that_does_not_change_board_is_not_recorded(
    grid: tuple[tuple[int, ...], ...], direction: models.MoveDirection
):
    """Test that a move that does not change the board is not recorded."""

    initial_board = models.GameBoard(grid=grid)
    initial_state = models.GameState(board=initial_board)
    game = models.Py2048Game(state=initial_state)

    # Attempt to make a move that does not change the board
    game.move(direction)

    # Check that no move was recorded
    assert len(game.moves) == 0

    # Check that the state has not changed
    assert game.state == initial_state


def test_attempting_to_undo_without_moves_raises_error():
    """Test that attempting to undo without any moves raises an error."""
    game = models.Py2048Game(state=models.GameState())

    with pytest.raises(ValueError, match="No moves to undo."):
        game.undo_last_move()


def test_undo_last_move():
    """Test that the last move can be undone."""
    initial_board = models.GameBoard(
        grid=((2, 0, 2, 0), (0, 0, 0, 0), (0, 2, 0, 2), (0, 0, 0, 0))
    )
    initial_state = models.GameState(board=initial_board, score=0)
    game = models.Py2048Game(state=initial_state, moves=[])

    # Make a move
    game.move(models.MoveDirection.LEFT)

    # Undo the last move
    game.undo_last_move()

    # Check that the moves history is empty
    assert len(game.moves) == 0

    # Check that the board and score are back to their initial state
    assert game.state.board == initial_board
    assert game.state.score == 0
