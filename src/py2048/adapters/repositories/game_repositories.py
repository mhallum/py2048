"""Abstract base class for game repositories.

Repositories manage Py2048Game instances, organized by:

- `slot_id`: A stable, user-facing name for saving/resuming games.
- `game_uuid`: A globally unique identifier for the specific game instance.

All implementations must support CRUD operations and track seen games
for unit-of-work-style coordination.
"""

import abc
import json
import logging
from pathlib import Path
from typing import cast

from py2048.adapters.schemas import GameSchema
from py2048.core.models import Py2048Game

logger = logging.getLogger(__name__)


class MissingGameError(Exception):
    """Exception raised when a game is not found in the repository."""


class AbstractGameRepository(abc.ABC):
    """Abstract base class for game repositories."""

    def __init__(self):
        self.seen: set[Py2048Game] = set()

    def add(self, game: Py2048Game) -> None:
        """Add a new game to the repository.

        Fails or raises an error if the slot is already occupied.
        """
        if self.get(game.slot_id) is not None:
            raise ValueError(f"Slot {game.slot_id} is already occupied.")
        self._add(game)
        self.seen.add(game)
        logger.info("Game %s added to slot %s", game.game_uuid, game.slot_id)

    def delete(self, slot_id: str) -> None:
        """Delete the game in the specified game slot."""

        if game := self.get(slot_id):
            self._delete(slot_id)
            self.seen.discard(game)
            logger.info("Slot %s deleted", slot_id)

    def get(self, slot_id: str) -> Py2048Game | None:
        """Retrieve the game stored in the slot.

        Args:
            slot_id (str): The game slot

        Returns:
            Py2048Game: The game instance associated with the given ID.
        """

        if game := self._get(slot_id):
            self.seen.add(game)
        return game

    def get_by_uuid(self, game_uuid: str) -> Py2048Game | None:
        """Retrieve a game by its UUID.

        Args:
            game_uuid (str): The UUID of the game to retrieve.

        Returns:
            Py2048Game: The game instance associated with the given UUID.
        """

        if game := self._get_by_uuid(game_uuid):
            self.seen.add(game)
        return game

    @abc.abstractmethod
    def _add(self, game: Py2048Game) -> None:
        """Abstract method to add a game to the repository."""
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def _delete(self, slot_id: str) -> None:
        """Abstract method to delete a game by its slot ID."""
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def _get(self, slot_id: str) -> Py2048Game | None:
        """Abstract method to retrieve the game in the specified slot."""
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def _get_by_uuid(self, game_uuid: str) -> Py2048Game | None:
        """Abstract method to retrieve a game by its UUID."""
        raise NotImplementedError  # pragma: no cover

    def save(self) -> None:
        """Save the current state of the repository (if applicable)."""


class JsonGameRepository(AbstractGameRepository):
    """JSON file-based implementation of the game repository."""

    def __init__(self, folder: str | Path):
        super().__init__()
        self._save_game_path = Path(folder) / "games.json"
        self._games: dict[str, Py2048Game] = {}
        self._load()

    def _add(self, game: Py2048Game) -> None:
        """Add a game to the JSON repository."""
        self._games[game.slot_id] = game

    def _get(self, slot_id: str) -> Py2048Game | None:
        """Retrieve the game in the specified slot."""
        return self._games.get(slot_id)

    def _delete(self, slot_id: str) -> None:
        """Delete the game in the specified slot."""
        if slot_id in self._games:
            del self._games[slot_id]

    def _get_by_uuid(self, game_uuid: str) -> Py2048Game | None:
        """Retrieve a game by its UUID."""
        for game in self._games.values():
            if game.game_uuid == game_uuid:
                return game
        return None

    def _load(self) -> None:
        """Load games from the JSON file into the repository."""
        if not self._save_game_path.exists():
            return

        with self._save_game_path.open("r", encoding="utf-8") as file:
            raw_data = json.load(file)

        if not raw_data:
            return  # Empty file, nothing to load

        games = cast(list[Py2048Game], GameSchema().load(raw_data, many=True))

        self._games = {game.slot_id: game for game in games}

    def list(self) -> list[Py2048Game]:
        """List all games in the repository."""
        return list(self._games.values())

    def save(self) -> None:
        """Save all games to the JSON file."""
        if not self._save_game_path.parent.exists():
            self._save_game_path.parent.mkdir(parents=True)

        with self._save_game_path.open("w", encoding="utf-8") as file:
            json.dump(GameSchema().dump(self._games.values(), many=True), file)
