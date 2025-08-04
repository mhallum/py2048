"""This module defines the abstract base class for game repositories
and an in-memory implementation of the game repository for the py2048 game.
"""

import abc
import json
from pathlib import Path
from typing import cast

from py2048.adapters.schemas import GameSchema
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

    def save(self) -> None:
        """Save the current state of the repository."""


class JsonGameRepository(AbstractGameRepository):
    """JSON file-based implementation of the game repository."""

    def __init__(self, folder: str | Path):
        super().__init__()
        self._save_game_path = Path(folder) / "games.json"
        self._games: dict[str, Py2048Game] = {}
        self._load()

    def _add(self, game: Py2048Game) -> None:
        """Add a game to the JSON repository."""
        self._games[game.game_id] = game

    def _get(self, game_id: str) -> Py2048Game:
        """Retrieve a game by its ID from the JSON repository."""

        if game := self._games.get(game_id):
            return game
        raise KeyError(f"Game with ID {game_id} not found in repository.")

    def _load(self) -> None:
        """Load games from the JSON file into the repository."""
        if not self._save_game_path.exists():
            return

        with self._save_game_path.open("r", encoding="utf-8") as file:
            raw_data = json.load(file)

        if not raw_data:
            return  # Empty file, nothing to load

        games = cast(list[Py2048Game], GameSchema().load(raw_data, many=True))

        self._games = {game.game_id: game for game in games}

    def list(self) -> list[Py2048Game]:
        """List all games in the repository."""
        return list(self._games.values())

    def save(self) -> None:
        """Save all games to the JSON file."""
        if not self._save_game_path.parent.exists():
            self._save_game_path.parent.mkdir(parents=True)

        with self._save_game_path.open("w", encoding="utf-8") as file:
            json.dump(
                GameSchema().dump(self._games.values(), many=True), file, indent=4
            )
