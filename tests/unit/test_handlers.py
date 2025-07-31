"""Unit tests for the handlers in the py2048 service layer."""

# pylint: disable=too-few-public-methods

from py2048 import bootstrap
from py2048.core import commands
from py2048.service_layer.unit_of_work import InMemoryUnitOfWork


def bootstrap_test_app():
    """Bootstrap a test application with an in-memory unit of work."""
    uow = InMemoryUnitOfWork()
    return bootstrap.bootstrap(uow=uow)


class TestCreateNewGame:
    """Test suite for creating a new game."""

    @staticmethod
    def test_create_new_game():
        """Test creating a new game using the start_new_game handler."""
        bus = bootstrap_test_app()
        game_id = "test_game"
        bus.handle(commands.StartNewGame(game_id=game_id))
        assert bus.uow.games.get(game_id) is not None
        assert bus.uow.games.get(game_id).game_id == game_id
