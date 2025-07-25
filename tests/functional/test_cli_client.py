"""Test cases for the CLI client of the py2048 game."""

# pylint: disable=magic-value-comparison, no-self-use, too-few-public-methods

from click.testing import CliRunner
import pytest
from py2048.run import main


class TestUnifiedEntryPoint:
    """Test cases for the unified entry point of the Py2048 game."""

    @pytest.mark.parametrize("flag", ["--help", "-h"])
    def test_help_option(self, flag: str):
        """Test that invoking the '-h or --help' option shows the help message."""
        runner = CliRunner()
        result = runner.invoke(main, [flag])
        assert result.exit_code == 0
        assert "Usage: " in result.output

    @pytest.mark.parametrize("flag", ["--version", "-v"])
    def test_version_option(self, flag: str):
        """Test that invoking the '-v or --version' option shows the version."""
        runner = CliRunner()
        result = runner.invoke(main, [flag])
        assert result.exit_code == 0
        assert "Py2048" in result.output
        assert "version" in result.output

    def test_mode_selection_default(self):
        """Test that the default mode is CLI when no mode is specified."""
        runner = CliRunner()
        result = runner.invoke(main)
        assert result.exit_code == 0
        assert (
            "Launching Py2048 in CLI mode" in result.output
        )  # Placeholder for actual CLI mode message
