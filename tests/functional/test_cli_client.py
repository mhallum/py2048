"""Test cases for the CLI client of the py2048 game."""

# pylint: disable=magic-value-comparison, no-self-use, too-few-public-methods

from click.testing import CliRunner
from py2048.run import main


class TestCli:
    """Test cases for the CLI client of the py2048 game."""

    def test_py2048_has_help_option(self):
        """Test that invoking the '--help' option shows the help message."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Usage: " in result.output

    def test_py2048_has_short_help_option(self):
        """Test that invoking the '-h' option shows the help message."""
        runner = CliRunner()
        result = runner.invoke(main, ["-h"])
        assert result.exit_code == 0
        assert "Usage: " in result.output

    def test_py2048_has_version_option(self):
        """Test that invoking the '--version' option shows the version."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "Py2048" in result.output
        assert "version" in result.output

    def test_py2048_has_short_version_option(self):
        """Test that invoking the '-v' option shows the version."""
        runner = CliRunner()
        result = runner.invoke(main, ["-v"])
        assert result.exit_code == 0
        assert "Py2048" in result.output
        assert "version" in result.output
