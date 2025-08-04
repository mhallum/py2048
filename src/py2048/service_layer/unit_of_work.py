"""Unit of Work Module"""

# pylint: disable=too-few-public-methods

import abc
from pathlib import Path
from typing import Any

from py2048.adapters import repositories
from py2048.core.events import Event


class AbstractUnitOfWork(abc.ABC):
    """Abstract base class for a Unit of Work.

    Coordinates changes to the game repository and collects new domain events
    emitted by aggregates (Py2048Game instances).
    """

    games: repositories.AbstractGameRepository

    def __enter__(self) -> "AbstractUnitOfWork":
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit the runtime context related to this object."""
        self.rollback()

    def commit(self) -> None:
        """Commit the current unit of work."""
        self._commit()

    def collect_new_events(self):
        """Collect new events from the games tracked in this unit of work.

        Returns:
           list[Event]: All domain events emitted during this Unit of Work session.
        """

        events: list[Event] = []

        for game in self.games.seen:
            events.extend(game.events)
            game.events.clear()

        return events

    @abc.abstractmethod
    def _commit(self) -> None:
        """Abstract method to commit the current unit of work."""

    @abc.abstractmethod
    def rollback(self) -> None:
        """Rollback the current unit of work.

        This method should revert any changes made during the current unit of work.
        """


class JsonUnitOfWork(AbstractUnitOfWork):
    """JSON file-based implementation of the unit of work.
    This class provides a repository that persists game instances to a JSON file.
    """

    def __init__(self, folder: str | Path):
        self.games = repositories.JsonGameRepository(folder)

    def _commit(self):
        """Commit the current unit of work."""
        self.games.save()

    def rollback(self):
        """Rollback the current unit of work."""
        # In a JSON repository, rollback is not typically supported.
        # This method will therefore not do anything.
