"""Module for handling notifications in the application."""

import abc
import time

from py2048.interfaces.cli.display import DisplayIO  # For type hinting

# pylint: disable=too-few-public-methods


class AbstractNotifications(abc.ABC):
    """Abstract base class for notifications."""

    @abc.abstractmethod
    def send(self, message: str) -> None:
        """Send a notification message."""
        raise NotImplementedError


class ConsoleNotifications(AbstractNotifications):
    """Concrete implementation of notifications using the console."""

    def __init__(self, display: DisplayIO):
        self.display = display

    def send(self, message: str) -> None:
        """Send a notification message to the console."""
        self.display.console.print(message, justify="center")
        time.sleep(1)  # Simulate a delay for the notification to be visible
        self.display.term.inkey()
