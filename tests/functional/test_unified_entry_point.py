"""Functional tests for the Py2048 unified entry point.

These tests verify that the correct interface is launched based on the
--mode option, and that help/version flags display the correct information.
"""

# pylint: disable=magic-value-comparison

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from py2048.run import main


@pytest.mark.parametrize("flag", ["--help", "-h"])
def test_help_option(flag: str):
    """Test that the help option (-h or --help) shows usage instructions."""
    runner = CliRunner()
    result = runner.invoke(main, [flag])
    assert result.exit_code == 0
    assert "Usage: " in result.output


@pytest.mark.parametrize("flag", ["--version", "-v"])
def test_version_option(flag: str):
    """Test that the version option (-v or --version) shows version info."""
    runner = CliRunner()
    result = runner.invoke(main, [flag])
    assert result.exit_code == 0
    assert "Py2048" in result.output
    assert "version" in result.output


def test_terminal_mode_launches_the_tui_app():
    """Test that selecting terminal mode calls the TUI interface runner."""
    with patch("py2048.interfaces.tui.app.Py2048TUIApp.run") as mock_run_tui:
        runner = CliRunner()
        result = runner.invoke(main, ["--mode", "terminal"])
        assert result.exit_code == 0
        mock_run_tui.assert_called_once()


def test_gui_mode_triggers_run_gui():
    """Test that selecting GUI mode calls the GUI interface runner."""
    with patch("py2048.interfaces.gui.main.run_gui") as mock_run_gui:
        runner = CliRunner()
        result = runner.invoke(main, ["--mode", "gui"])
        assert result.exit_code == 0
        mock_run_gui.assert_called_once()


def test_gui_mode_triggers_run_web():
    """Test that selecting Web mode starts the Flask web interface."""
    with patch("py2048.interfaces.web.main.run_web") as mock_run_web:
        runner = CliRunner()
        result = runner.invoke(main, ["--mode", "web"])
        assert result.exit_code == 0
        mock_run_web.assert_called_once()
