"""Unit tests for the handlers in the py2048 service layer."""

# pylint: disable=too-few-public-methods

import random
from collections.abc import Iterable

from py2048 import bootstrap
from py2048.adapters.notifications import AbstractNotifications
from py2048.adapters.repositories import AbstractGameRepository
from py2048.core import commands, models
from py2048.service_layer.unit_of_work import AbstractUnitOfWork


class FakeGameRepository(AbstractGameRepository):
    """A fake game repository for testing purposes."""

    def __init__(self, games: Iterable[models.Py2048Game] = ()):
        super().__init__()
        self._games = set(games)

    def _add(self, game: models.Py2048Game) -> None:
        """Add a game to the fake repository."""
        self._games.add(game)

    def _get(self, game_id: str) -> models.Py2048Game:
        """Retrieve a game by its ID from the fake repository."""
        for game in self._games:
            if game.game_id == game_id:
                return game
        raise KeyError(f"Game with ID {game_id} not found in repository.")


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


class FakeNotifications(AbstractNotifications):
    """A fake notifications handler for testing purposes."""

    def __init__(self):
        self.sent: list[str] = []

    def send(self, message: str) -> None:
        """Simulate sending a notification."""
        self.sent.append(message)


def bootstrap_test_app():
    """Bootstrap a test application with a fake unit of work and seeded rng."""
    uow = FakeUnitOfWork()
    notifications = FakeNotifications()
    rng = random.Random(42)  # Seeded RNG for reproducibility
    return bootstrap.bootstrap(uow=uow, notifications=notifications, rng=rng)


class TestCreateNewGame:
    """Test suite for creating a new game."""

    @staticmethod
    def test_create_new_game():
        """Test creating a new game using the start_new_game handler."""
        bus = bootstrap_test_app()
        game_id = "new_game"
        bus.handle(commands.StartNewGame(game_id=game_id))
        assert bus.uow.games.get(game_id) is not None
        assert bus.uow.games.get(game_id).game_id == game_id


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
        game_id = test_game.game_id
        starting_board = test_game.state.board.grid

        # Make an initial move
        bus.handle(commands.MakeMove(game_id=game_id, direction="up"))

        # Verify that the move was processed
        game = bus.uow.games.get(game_id)
        assert len(game.moves) == 1  # move recorded
        expected_direction = "up"
        assert game.moves[0].direction == expected_direction  # correct move recorded
        expected_score = 4  # 2 + 2 from the merge
        assert game.state.score == expected_score  # score updated
        assert game.state.board.grid != starting_board  # board updated
        expected_empty_tiles = 14  # 16 total tiles - 2 merged + 1 spawned
        assert len(game.state.board.empty_tile_positions) == expected_empty_tiles

    @staticmethod
    def test_notification_sent_on_game_over(test_game: models.Py2048Game):
        """Test that a notification is sent when the game is over."""
        fake_notifications = FakeNotifications()
        bus = bootstrap.bootstrap(
            uow=FakeUnitOfWork(),
            notifications=fake_notifications,
            rng=random.Random(42),
        )
        test_game = models.Py2048Game(
            game_id="current_game",
            state=models.GameState(
                board=models.GameBoard(
                    grid=(
                        (2, 4, 8, 2),
                        (4, 8, 4, 8),
                        (2, 16, 8, 16),
                        (8, 8, 4, 32),
                    )
                ),
                score=104,
            ),
        )
        bus.uow.games.add(test_game)
        game_id = test_game.game_id

        cmd = commands.MakeMove(game_id=game_id, direction="left")
        bus.handle(cmd)
        print(test_game.state.board.grid)
        expected_message = "Game Over! Final score: 120"
        assert expected_message in fake_notifications.sent
