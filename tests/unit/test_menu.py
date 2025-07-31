"""Unit tests for the Menu class in the py2048 application."""

from py2048.application.menu import Menu


def test_menu_can_move_up():
    """Test that the menu can move up."""
    menu = Menu("Test Menu", ["Item 1", "Item 2", "Item 3"])
    menu.index = 1
    menu.move_up()
    assert menu.index == 0


def test_menu_can_move_down():
    """Test that the menu can move down."""
    menu = Menu("Test Menu", ["Item 1", "Item 2", "Item 3"])
    menu.index = 0
    menu.move_down()
    assert menu.index == 1


def test_menu_can_select():
    """Test that the menu can return the select the current item."""
    menu = Menu("Test Menu", ["Item 1", "Item 2", "Item 3"])
    menu.index = 1
    assert menu.selected == "Item 2"  # pylint: disable=magic-value-comparison
    # pylint warning disabled because an enum is overkill for such a small and isolated test
