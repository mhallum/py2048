"""package containing repositories for the game."""

from .game_repositories import AbstractGameRepository, JsonGameRepository
from .records_repositories import AbstractRecordsRepository, JsonRecordRepository

__all__ = [
    "AbstractGameRepository",
    "JsonGameRepository",
    "AbstractRecordsRepository",
    "JsonRecordRepository",
]
