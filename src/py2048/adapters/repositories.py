"""This module defines the abstract base class for game repositories
and an in-memory implementation of the game repository for the py2048 game.
"""

import abc

from py2048.core.models import Py2048Game


class AbstractGameRepository(abc.ABC):
    """Abstract base class for game repositories."""

    @abc.abstractmethod
    def add(self, game: Py2048Game) -> None:
        """Add a game to the repository."""

    @abc.abstractmethod
    def get(self, game_id: str) -> Py2048Game:
        """Retrieve a game by its ID.

        Args:
            game_id (str): The unique identifier for the game.

        Returns:
            Py2048Game: The game instance associated with the given ID.
        """


class InMemoryGameRepository(AbstractGameRepository):
    """In-memory implementation of the game repository."""

    def __init__(self):
        self._games: set[Py2048Game] = set()

    def add(self, game: Py2048Game) -> None:
        """Add a game to the in-memory repository."""
        self._games.add(game)

    def get(self, game_id: str) -> Py2048Game:
        """Retrieve a game by its ID from the in-memory repository."""
        for game in self._games:
            if game.game_id == game_id:
                return game
        raise KeyError(f"Game with ID {game_id} not found in repository.")
