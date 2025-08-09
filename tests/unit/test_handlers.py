"""Unit tests for the handlers in the py2048 service layer."""

# pylint: disable=too-few-public-methods

import random
from collections.abc import Iterable
from pprint import pformat

import pytest

from py2048 import bootstrap
from py2048.adapters.repositories import (
    AbstractGameRepository,
    AbstractRecordsRepository,
)
from py2048.core import commands, models
from py2048.core.models.record import GameRecord
from py2048.service_layer.unit_of_work import AbstractUnitOfWork


class FakeGameRepository(AbstractGameRepository):
    """A fake game repository for testing purposes."""

    def __init__(self, games: Iterable[models.Py2048Game] = ()):
        super().__init__()
        self._games: dict[str, models.Py2048Game] = {}
        for game in games:
            self._games[game.slot_id] = game

    def _add(self, game: models.Py2048Game) -> None:
        """Add a game to the fake repository."""
        self._games[game.slot_id] = game

    def _get(self, slot_id: str) -> models.Py2048Game | None:
        """Retrieve the game in the specified slot."""
        return self._games.get(slot_id)

    def _get_by_uuid(self, game_uuid: str) -> models.Py2048Game | None:
        """Retrieve a game by its UUID."""
        for game in self._games.values():
            if game.game_uuid == game_uuid:
                return game
        return None

    def _delete(self, slot_id: str) -> None:
        """Delete the game in the specified slot."""
        if slot_id in self._games:
            del self._games[slot_id]


class FakeRecordRepository(AbstractRecordsRepository):
    """A fake record repository for testing purposes."""

    def __init__(self, records: Iterable[GameRecord] = ()):
        self._records: dict[str, GameRecord] = {}
        for record in records:
            self._records[record.game_uuid] = record

    def add(self, record: GameRecord) -> None:
        """Add a game record to the fake repository."""
        self._records[record.game_uuid] = record

    def get(self, game_uuid: str) -> GameRecord | None:
        """Retrieve a game record by its UUID."""
        return self._records.get(game_uuid)

    def save(self) -> None:
        """No-op for the fake repository."""

    def list(self) -> list[GameRecord]:
        """Return a list of all game records."""
        return list(self._records.values())


class FakeUnitOfWork(AbstractUnitOfWork):
    """A fake unit of work for testing purposes."""

    def __init__(self):
        self.games = FakeGameRepository([])
        self.records = FakeRecordRepository([])
        self.committed = False

    def _commit(self) -> None:
        """Commit the current unit of work."""
        self.committed = True

    def rollback(self) -> None:
        """Rollback the current unit of work."""
        # No-op for the fake unit of work


def bootstrap_test_app():
    """Bootstrap a test application with a fake unit of work and seeded rng."""
    uow = FakeUnitOfWork()
    rng = random.Random(42)  # Seeded RNG for reproducibility
    return bootstrap.bootstrap(uow=uow, rng=rng)


# TODO: add tests to make sure game is created correctly
class TestCreateNewGame:
    """Test suite for creating a new game."""

    @staticmethod
    def test_create_new_game():
        """Test creating a new game using the start_new_game handler."""
        bus = bootstrap_test_app()

        slot_id = "current_game"
        bus.handle(commands.StartNewGame(slot_id=slot_id))

        new_game = bus.uow.games.get(slot_id)
        assert new_game is not None
        assert new_game.slot_id == slot_id


class TestMakeMove:
    """Test suite for making a move in the game."""

    @staticmethod
    def test_move_is_added_to_history(test_game: models.Py2048Game):
        """Test that move is added to the game's move history after successful completion."""

        # test_game is a game with initially no moves recorded
        initial_num_moves = len(test_game.moves)  # 0

        bus = bootstrap_test_app()
        bus.uow.games.add(test_game)
        game_uuid = test_game.game_uuid

        move_direction = "up"
        bus.handle(commands.MakeMove(game_uuid=game_uuid, direction=move_direction))

        assert len(test_game.moves) == initial_num_moves + 1
        assert test_game.moves[-1].direction == move_direction

    # TODO: test_no_tile_is_spawned_if_board_does_not_change

    # TODO: test_move_that_makes_no_changes_does_not_add_to_history

    # TODO: test_move_on_non_existent_game_raises_error

    # TODO: test_that_move_handler_commits

    # TODO: test_that_correct_move_is_added_to_history

    @pytest.mark.parametrize(
        "move_direction, expected_gain",
        [
            # moving up merges two tiles with value 2 into a single tile with value 4
            # so gain is 4
            ("up", 4),
            # moving down merges two tiles with value 2 into a single tile with value 4
            # so gain is 4
            ("down", 4),
            # moving left does not merge any tiles, so gain is 0
            ("left", 0),
            # moving right does not merge any tiles, so gain is 0
            ("right", 0),
        ],
    )
    @staticmethod
    def test_move_updates_score(
        test_game: models.Py2048Game, move_direction: str, expected_gain: int
    ):
        """Test that making a move updates the score correctly."""

        # test_game is a game with an initial score of 0
        initial_score = test_game.state.score

        bus = bootstrap_test_app()
        bus.uow.games.add(test_game)
        game_uuid = test_game.game_uuid

        bus.handle(commands.MakeMove(game_uuid=game_uuid, direction=move_direction))

        assert test_game.state.score == initial_score + expected_gain

    # TODO: test_move_updates_board

    @pytest.mark.parametrize(
        "move_direction, expected_updated_board",
        [
            # moving up merges two tiles with value 2 into a single tile with value 4
            # and spawns a new tile
            ("up", ((0, 0, 0, 4), (0, 0, 0, 0), (0, 0, 0, 2), (0, 0, 0, 0))),
            # moving down merges two tiles with value 2 into a single tile with value 4
            # and spawns a new tile
            ("down", ((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 2, 0), (0, 0, 0, 4))),
            # moving left shifts the tiles, but does not merge any tiles
            # a new tile is spawned
            ("left", ((2, 0, 0, 0), (0, 0, 0, 0), (2, 0, 0, 0), (2, 0, 0, 0))),
            # board cannot change by moving right since there are no tiles to merge or move
            # no tiles are spawned
            ("right", ((0, 0, 0, 2), (0, 0, 0, 0), (0, 0, 0, 2), (0, 0, 0, 0))),
        ],
    )
    @staticmethod
    def test_move_updates_board(
        test_game: models.Py2048Game,
        move_direction: str,
        expected_updated_board: tuple[tuple[int, ...], ...],
    ):
        """Test that making a move updates the game board correctly.

        Test that the make_move handler updates the game board according to the rules of 2048.
        i.e., if the move results in a merge, the tiles should be combined and a new tile spawned.
        If the move does not result in a merge, the tiles should shift without merging,
        and a new tile should be spawned.
        If the move results in a merge, the tiles should be combined and a new tile spawned.
        If there is no space for the tiles to move in the given direction, and no tiles
        can be merged, the board should remain unchanged, and no new tile should be spawned.
        """

        bus = bootstrap_test_app()
        bus.uow.games.add(test_game)
        game_uuid = test_game.game_uuid

        bus.handle(commands.MakeMove(game_uuid=game_uuid, direction=move_direction))

        result = test_game.state.board.grid
        assert result == expected_updated_board, (
            f"For move: {move_direction}\n"
            f"Expected:\n{pformat(expected_updated_board)}\n"
            f"Got:\n{pformat(result)}"
        )

    # TODO: test_that_making_a_move_on_an_already_ended_game_raises_error

    # TODO: test_that_making_a_move_on_a_game_with_no_tiles_raises_error

    # TODO: test_that_move_is_logged

    @staticmethod
    def test_game_is_deleted_after_game_over(almost_over_test_game: models.Py2048Game):
        """Test that the game is deleted after game over."""
        bus = bootstrap_test_app()
        bus.uow.games.add(almost_over_test_game)
        game_uuid = almost_over_test_game.game_uuid

        # Simulate a move that results in game over
        bus.handle(commands.MakeMove(game_uuid=game_uuid, direction="up"))

        assert bus.uow.games.get_by_uuid(game_uuid) is None, (
            f"Game with UUID {game_uuid} should be deleted after game over, but it still exists."
        )

    @staticmethod
    def test_game_record_is_added_to_repository_after_game_over(
        almost_over_test_game: models.Py2048Game,
    ):
        """Test that a game record is added to the repository after game over."""
        bus = bootstrap_test_app()
        bus.uow.games.add(almost_over_test_game)
        game_uuid = almost_over_test_game.game_uuid

        # Simulate a move that results in game over
        bus.handle(commands.MakeMove(game_uuid=game_uuid, direction="up"))

        # Check if the record was created
        record = bus.uow.records.get(game_uuid)
        assert record is not None, "Record should have been created, but was not."
        expected_record = GameRecord(
            game_uuid=record.game_uuid,
            final_score=1716,
            max_tile=128,
            number_of_moves=1,
        )
        assert record == expected_record, (
            f"Expected record:\n{pformat(expected_record)}\nGot:\n{pformat(record)}"
        )
