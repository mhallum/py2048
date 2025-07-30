"""Exceptions for the 2048 game core module."""


class InvalidGameBoard(Exception):
    """Raised when the game board is invalid."""


class SpawnTileError(Exception):
    """Raised when a tile cannot be spawned on the game board."""
