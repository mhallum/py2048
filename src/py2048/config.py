"""Configuration for Py2048 application."""

from pathlib import Path

from appdirs import user_data_dir  # type: ignore

APP_NAME = "py2048"
APP_AUTHOR = "mhallum"
data_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))  # type: ignore


def get_user_data_folder() -> Path:
    """Get the user data folder for Py2048."""
    return Path(user_data_dir(APP_NAME, APP_AUTHOR))  # type: ignore
