"""This module defines the abstract base class for game repositories
and an in-memory implementation of the game repository for the py2048 game.
"""

import abc

from py2048.core.models import Py2048Game


class AbstractGameRepository(abc.ABC):
    """Abstract base class for game repositories."""

    def __init__(self):
        self.seen: set[Py2048Game] = set()

    def add(self, game: Py2048Game) -> None:
        """Add a game to the repository."""
        self._add(game)
        self.seen.add(game)

    def get(self, game_id: str) -> Py2048Game:
        """Retrieve a game by its ID.

        Args:
            game_id (str): The unique identifier for the game.

        Returns:
            Py2048Game: The game instance associated with the given ID.
        """

        if game := self._get(game_id):
            self.seen.add(game)
        return game

    @abc.abstractmethod
    def _add(self, game: Py2048Game) -> None:
        """Abstract method to add a game to the repository."""
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def _get(self, game_id: str) -> Py2048Game:
        """Abstract method to retrieve a game by its ID."""
        raise NotImplementedError  # pragma: no cover


class InMemoryGameRepository(AbstractGameRepository):
    """In-memory implementation of the game repository."""

    def __init__(self):
        super().__init__()
        self._games: set[Py2048Game] = set()

    def _add(self, game: Py2048Game) -> None:
        """Add a game to the in-memory repository."""
        self._games.add(game)

    def _get(self, game_id: str) -> Py2048Game:
        """Retrieve a game by its ID from the in-memory repository."""
        for game in self._games:
            if game.game_id == game_id:
                return game
        raise KeyError(f"Game with ID {game_id} not found in repository.")
