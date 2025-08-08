"""Unit tests for the handlers in the py2048 service layer."""

# pylint: disable=too-few-public-methods

import random
from collections.abc import Iterable

from py2048 import bootstrap
from py2048.adapters.repositories import AbstractGameRepository
from py2048.core import commands, models
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


class FakeUnitOfWork(AbstractUnitOfWork):
    """A fake unit of work for testing purposes."""

    def __init__(self):
        self.games = FakeGameRepository([])
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
    def test_make_move(test_game: models.Py2048Game):
        """Test making a move using the make_move handler."""
        bus = bootstrap_test_app()

        # Add the test game to the in-memory unit of work.
        # The test_game fixture creates a game with a specific board state
        # so we can test the move functionality
        # the score is initialized to 0, there are no recorded moves.
        # and the board has two tiles with value 2 in the same column
        # This means that an upward move will merge them
        # and the score will increase by 4.

        bus.uow.games.add(test_game)
        game_uuid = test_game.game_uuid
        starting_board = test_game.state.board.grid

        # Make an initial move
        bus.handle(commands.MakeMove(game_uuid=game_uuid, direction="up"))

        # Verify that the move was processed
        game = bus.uow.games.get_by_uuid(game_uuid)
        assert game is not None
        assert len(game.moves) == 1  # move recorded
        expected_direction = "up"
        assert game.moves[0].direction == expected_direction  # correct move recorded
        expected_score = 4  # 2 + 2 from the merge
        assert game.state.score == expected_score  # score updated
        assert game.state.board.grid != starting_board  # board updated
        expected_empty_tiles = 14  # 16 total tiles - 2 merged + 1 spawned
        assert len(game.state.board.empty_tile_positions) == expected_empty_tiles
