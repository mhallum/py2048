"""Test cases for the CLI client of the py2048 game."""

from click.testing import CliRunner
from py2048.front_end.cli import py2048


class TestCli:
    """Test cases for the CLI client of the py2048 game."""

    def test_py2048_has_help_option(self):
        """Test that typing 'py2048 --help' shows the help message."""
        runner = CliRunner()
        result = runner.invoke(py2048, ["--help"])
        assert result.exit_code == 0
        assert "Usage: py2048" in result.output

    def test_py2048_has_short_help_option(self):
        """Test that typing 'py2048 -h' shows the help message."""
        runner = CliRunner()
        result = runner.invoke(py2048, ["-h"])
        assert result.exit_code == 0
        assert "Usage: py2048" in result.output

    def test_py2048_has_version_option(self):
        """Test that typing 'py2048 --version' shows the version."""
        runner = CliRunner()
        result = runner.invoke(py2048, ["--version"])
        assert result.exit_code == 0
        assert "Py2048" in result.output
        assert "version" in result.output

    def test_py2048_has_short_version_option(self):
        """Test that typing 'py2048 -v' shows the version."""
        runner = CliRunner()
        result = runner.invoke(py2048, ["-v"])
        assert result.exit_code == 0
        assert "Py2048" in result.output
        assert "version" in result.output
