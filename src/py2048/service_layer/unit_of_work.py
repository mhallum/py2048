"""Unit of Work Module"""

# pylint: disable=too-few-public-methods

import abc

from py2048.adapters import repositories
from py2048.core.events import Event


class AbstractUnitOfWork(abc.ABC):
    """Abstract base class for a Unit of Work.

    Coordinates changes to the game repository and collects new domain events
    emitted by aggregates (Py2048Game instances).
    """

    games: repositories.AbstractGameRepository

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


class InMemoryUnitOfWork(AbstractUnitOfWork):
    """In-memory implementation of the unit of work.
    This class provides an in-memory repository for managing game instances.
    """

    def __init__(self):
        self.games = repositories.InMemoryGameRepository()
