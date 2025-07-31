"""Funcional tests for the CLI interface of Py2048."""

from unittest.mock import MagicMock, patch

from blessed import Terminal
from blessed.keyboard import Keystroke
from pytest import CaptureFixture

from py2048.interfaces.cli.main import run_cli

KEY_DOWN = 258
KEY_ENTER = 343
KEY_UP = 259
KEY_ESCAPE = 27

TITLE_MARKER = "Welcome to Py2048!"  # Expected title in the CLI menu
EXIT_MESSAGE = "Goodbye!"  # Expected message when exiting the CLI
EXIT_MENU_ITEM = "Exit"  # Expected exit menu item
NEW_GAME_MENU_ITEM = "New Game"  # Expected new game menu item


def fake_key(code: int, name: str) -> MagicMock:
    """Create a mock key press."""
    key = MagicMock()
    key.code = code
    key.name = name
    return key


def test_running_cli_opens_main_menu(capsys: CaptureFixture[str]):
    """Test that running the CLI opens the main menu."""
    term = Terminal()
    with patch.object(term, "inkey", side_effect=[Keystroke("q")]):
        # Run the CLI interface
        run_cli(term=term)
        captured = capsys.readouterr()

    # Menu title is displayed
    assert TITLE_MARKER in captured.out

    # New Game is the first item and is highlighted
    assert "> " + NEW_GAME_MENU_ITEM in captured.out

    # Exit is the second item and is not highlighted
    assert EXIT_MENU_ITEM in captured.out


def test_menu_navigation(capsys: CaptureFixture[str]):
    """Test that the menu can be navigated using arrow keys."""
    term = Terminal()

    # The user experiments with the menu controls
    with patch.object(
        term,
        "inkey",
        side_effect=[
            fake_key(KEY_DOWN, "KEY_DOWN"),  # User presses down (Exit is selected)
            fake_key(KEY_UP, "KEY_UP"),  # User presses up (New Game is selected)
            fake_key(KEY_DOWN, "KEY_DOWN"),  # User presses down again
            fake_key(KEY_ENTER, "KEY_ENTER"),  # User presses enter (selected Exit)
        ],
    ):
        # Run the CLI interface
        run_cli(term=term)
        captured = capsys.readouterr()

    loops = captured.out.split("↑ ↓ to navigate | Enter to select | Esc/Q to quit")

    # Check output after User presses down
    assert "> " + EXIT_MENU_ITEM in loops[1]
    assert "> " + NEW_GAME_MENU_ITEM not in loops[1]

    # Check output after User presses up
    assert "> " + NEW_GAME_MENU_ITEM in loops[2]
    assert "> " + EXIT_MENU_ITEM not in loops[2]

    # Check output after User presses down again
    assert "> " + EXIT_MENU_ITEM in loops[3]
    assert "> " + NEW_GAME_MENU_ITEM not in loops[3]

    # Check output after User presses enter
    assert EXIT_MESSAGE in loops[4]
