"""Functional tests for the CLI of Py2048."""

from pathlib import Path
from random import Random
from unittest.mock import MagicMock, patch

import pytest
from blessed import Terminal
from blessed.keyboard import Keystroke
from pytest import CaptureFixture
from rich.console import Console

from py2048.bootstrap import bootstrap
from py2048.interfaces.cli.game_runner import LOOP_TERMINATION_DELIMITER
from py2048.interfaces.cli.main import run_cli
from py2048.service_layer.unit_of_work import JsonUnitOfWork

from .console_parser import ConsoleGameScreenParser, split_console_output_loops

KEY_UP = 259
KEY_DOWN = 258
KEY_LEFT = 260
KEY_RIGHT = 261
KEY_ENTER = 343
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


@pytest.mark.functional
def test_running_cli_opens_main_menu(
    fake_user_data_folder: Path, capsys: CaptureFixture[str]
):
    """Test that running the CLI opens the main menu."""
    term = Terminal()
    console = Console()
    bus = bootstrap(uow=JsonUnitOfWork(fake_user_data_folder))
    with patch.object(
        term,
        "inkey",
        side_effect=[
            fake_key(KEY_DOWN, "KEY_DOWN"),  # User presses down to select Exit
            fake_key(KEY_ENTER, "KEY_ENTER"),  # User presses enter (selected Exit)
        ],
    ):
        # Run the CLI interface
        run_cli(bus=bus, term=term, console=console)
        captured = capsys.readouterr()

    # Menu title is displayed
    assert TITLE_MARKER in captured.out

    # New Game is the first item and is highlighted
    assert "➤ " + NEW_GAME_MENU_ITEM in captured.out

    # Exit is the second item
    assert EXIT_MENU_ITEM in captured.out


@pytest.mark.functional
def test_menu_navigation(fake_user_data_folder: Path, capsys: CaptureFixture[str]):
    """Test that the menu can be navigated using arrow keys."""
    bus = bootstrap(uow=JsonUnitOfWork(Path(fake_user_data_folder)))
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
        run_cli(bus, term=term)
        captured = capsys.readouterr()

    loops = captured.out.split("↑ ↓ to navigate | Enter to select")

    # Check output after User presses down
    assert "➤ " + EXIT_MENU_ITEM in loops[1]
    assert "➤ " + NEW_GAME_MENU_ITEM not in loops[1]

    # Check output after User presses up
    assert "➤ " + NEW_GAME_MENU_ITEM in loops[2]
    assert "➤ " + EXIT_MENU_ITEM not in loops[2]

    # Check output after User presses down again
    assert "➤ " + EXIT_MENU_ITEM in loops[3]
    assert "➤ " + NEW_GAME_MENU_ITEM not in loops[3]

    # Check output after User presses enter
    assert EXIT_MESSAGE in loops[4]


@pytest.mark.functional
def test_starting_a_new_game(fake_user_data_folder: Path):
    """Test that selecting 'New Game' opens a game screen with a fresh game."""
    term = Terminal()
    console = Console(record=True)
    bus = bootstrap(
        uow=JsonUnitOfWork(Path(fake_user_data_folder)), rng=Random(42)
    )  # Using a fixed seed to make the game state predictable

    side_effects: list[MagicMock | Keystroke] = []

    # The user is in the main menu and selects 'New Game'
    side_effects.append(fake_key(KEY_ENTER, "KEY_ENTER"))
    # The user should now be viewing the game screen with a fresh game
    # (see assertions: 1)

    # The user moves up
    side_effects.append(fake_key(KEY_UP, "KEY_UP"))
    # The user should now be viewing the an updated game screen with the move applied
    # (see assertions: 2)

    # The user moves down
    side_effects.append(fake_key(KEY_DOWN, "KEY_DOWN"))
    # The user should now be viewing the an updated game screen with the move applied
    # (see assertions: 3)

    # The user moves left
    side_effects.append(fake_key(KEY_LEFT, "KEY_LEFT"))
    # The user should now be viewing the an updated game screen with the move applied
    # (see assertions: 4)

    # The user moves right
    side_effects.append(fake_key(KEY_RIGHT, "KEY_RIGHT"))
    # The user should now be viewing the an updated game screen with the move applied
    # (see assertions: 5)

    # The user exits the game
    side_effects.append(Keystroke("q"))
    #  A goodbye message should be displayed
    # (see assertions: 6)

    with patch.object(term, "inkey", side_effect=side_effects):
        run_cli(bus=bus, term=term, console=console, test_mode=True)
        raw_output = console.export_text()
    loops = split_console_output_loops(raw_output, LOOP_TERMINATION_DELIMITER)

    expected_number_of_loops = 6
    assert len(loops) == expected_number_of_loops

    # Assertions for the first loop (New Game)
    game_screen = ConsoleGameScreenParser(loops[0])
    assert game_screen.score == 0
    assert game_screen.high_score == 0
    assert game_screen.grid == (
        (0, 0, 0, 2),
        (0, 2, 0, 0),
        (0, 0, 0, 0),
        (0, 0, 0, 0),
    )  # Game starts with 2 spawned tiles

    # Assertions for the second loop (after moving up)
    game_screen = ConsoleGameScreenParser(loops[1])
    assert game_screen.score == 0
    assert game_screen.high_score == 0
    assert game_screen.grid == (
        (0, 2, 0, 2),
        (2, 0, 0, 0),
        (0, 0, 0, 0),
        (0, 0, 0, 0),
    )  # The board has shifted up and spawned a new tile

    # Assertions for the third loop (after moving down)
    game_screen = ConsoleGameScreenParser(loops[2])
    assert game_screen.score == 0
    assert game_screen.high_score == 0
    assert game_screen.grid == (
        (0, 0, 0, 0),
        (0, 0, 0, 0),
        (0, 0, 2, 0),
        (2, 2, 0, 2),
    )  # The board has shifted down and spawned a new tile

    # Assertions for the fourth loop (after moving left)
    game_screen = ConsoleGameScreenParser(loops[3])
    assert game_screen.score == 4  # Score should be 4 after merging two 2s
    assert game_screen.high_score == 0
    assert game_screen.grid == (
        (0, 0, 0, 0),
        (0, 0, 0, 0),
        (2, 2, 0, 0),
        (4, 2, 0, 0),
    )  # The board has shifted left (merging the 2s) and spawned a new tile

    # Assertions for the fifth loop (after moving right)
    game_screen = ConsoleGameScreenParser(loops[4])
    assert game_screen.score == 8  # Score should increase by 4 after merging two 2s
    assert game_screen.high_score == 0
    assert game_screen.grid == (
        (0, 0, 0, 0),
        (0, 0, 2, 0),
        (0, 0, 0, 4),
        (0, 0, 4, 2),
    )  # The board has shifted right (merging the 2s) and spawned a new tile

    # A goodbye message should be displayed after the user exits
    assert (
        EXIT_MESSAGE in loops[-2]
    )  # The last loop should contain the exit message (-2 to skip the empty line at the end)


# Add test for other key presses
# Add test for invalid moves
# Add test for undo functionality

# test_resuming_game

# test_starting_another_game

# test_finishing_game

# test_starting_another_game_after_finishing

# test_viewing_statistics
# test_resetting_statistics
