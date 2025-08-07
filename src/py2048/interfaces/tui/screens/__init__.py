"""Module containing TUI screens for the Py2048 game."""

from .game_over_screen import GameOverScreen
from .game_screen import GameScreen
from .main_menu import MainMenu

__all__ = ["GameScreen", "MainMenu", "GameOverScreen"]
# This allows for easy import of all screens in the TUI interface.
