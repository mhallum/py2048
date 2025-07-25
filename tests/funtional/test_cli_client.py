"""Test cases for the CLI client of the py2048 game."""

from click.testing import CliRunner
from py2048.front_end.cli import py2048


class TestCli:
    """Test cases for the CLI client of the py2048 game."""

    def test_py2048_has_help_command(self):
        """Test that typing 'py2048 --help' shows the help message."""
        runner = CliRunner()
        result = runner.invoke(py2048, ["--help"])
        assert result.exit_code == 0
        assert "Usage: py2048" in result.output
