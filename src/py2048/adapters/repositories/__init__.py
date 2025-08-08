"""package containing repositories for the game."""

from .game_repositories import AbstractGameRepository, JsonGameRepository

__all__ = [
    "AbstractGameRepository",
    "JsonGameRepository",
]
