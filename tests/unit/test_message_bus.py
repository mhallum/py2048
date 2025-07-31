"""Test suite for edge cases in the message bus."""

from dataclasses import dataclass
import pytest
from py2048.bootstrap import bootstrap
from py2048.core import commands, events
from py2048.service_layer import unit_of_work
from py2048.service_layer.messagebus import (
    MISSING_HANDLER_DESCRIPTION,
    UNKNOWN_MESSAGE_TYPE_DESCRIPTION,
    UNEXPECTED_ERROR_DESCRIPTION,
    UNEXPECTED_ERROR_WHILE_COLLECTING_EVENTS_DESCRIPTION,
    HANDLING_EVENT_DESCRIPTION,
    HANDLING_COMMAND_DESCRIPTION,
)

# pylint: disable=too-few-public-methods


@dataclass
class FakeCommand(commands.Command):
    """A fake command for testing."""


def dummy_command_handler(command: FakeCommand):  # pylint: disable=unused-argument
    """A dummy handler that does nothing."""


def failing_command_handler(command: FakeCommand):
    """A handler that raises an exception."""
    raise Exception("Simulated failure")  # pylint: disable=broad-exception-raised


@dataclass
class FakeEvent(events.Event):
    """A fake event for testing."""


def dummy_event_handler(event: FakeEvent):  # pylint: disable=unused-argument
    """A dummy event handler that does nothing."""


def failing_event_handler(event: FakeEvent):
    """An event handler that raises an exception."""
    raise Exception("Simulated failure in event handler")  # pylint: disable=broad-exception-raised


class FaultyUnitOfWork(unit_of_work.AbstractUnitOfWork):
    """A faulty unit of work that raises an error when collecting events."""

    def collect_new_events(self):
        """Simulate an error when collecting events."""
        raise Exception("Simulated failure in collecting events")  # pylint: disable=broad-exception-raised


# ============================================================================
#     Tests
# ============================================================================


class TestMessageBusEdgeCases:
    """Test suite for edge cases in the message bus."""

    @staticmethod
    def test_bus_raises_error_on_invalid_message_type():
        """Test that an invalid message type raises an error."""
        bus = bootstrap()

        expected_error_message = UNKNOWN_MESSAGE_TYPE_DESCRIPTION.format(
            type_name="str"
        )

        with pytest.raises(TypeError, match=expected_error_message):
            bus.handle("InvalidMessage")  # type: ignore[arg-type]


class TestCommandHandlingEdgeCases:
    """Test suite for edge cases in command handling."""

    @staticmethod
    def test_bus_logs_and_raises_error_on_missing_handler(
        caplog: pytest.LogCaptureFixture,
    ):
        """Verify that the message bus logs an error and raises a ValueError
        when attempting to handle a command with no registered handler.
        """

        bus = bootstrap()

        command = FakeCommand()
        expected_content = MISSING_HANDLER_DESCRIPTION.format(
            kind="command", message=command
        )

        with caplog.at_level("ERROR"):
            with pytest.raises(ValueError, match=expected_content):
                bus.handle(command)
        assert any(expected_content in record.message for record in caplog.records)

    @staticmethod
    def test_bus_logs_error_and_continues_on_unexpected_error(
        caplog: pytest.LogCaptureFixture,
    ):
        """Test that an unexpected error while handling a command is logged and continues."""
        bus = bootstrap(command_handlers={FakeCommand: failing_command_handler})

        command = FakeCommand()

        expected_content = UNEXPECTED_ERROR_DESCRIPTION.format(
            kind="command", message=command
        )

        with caplog.at_level("ERROR"):
            with pytest.raises(Exception, match="Simulated failure"):
                bus.handle(command)

        # Check that the expected error message is logged
        assert any(expected_content in record.message for record in caplog.records), (
            f"Expected log message not found: {expected_content}"
        )

        # Check that at least one ERROR log has traceback info
        expected_level = "ERROR"
        assert any(
            record.exc_info is not None
            for record in caplog.records
            if record.levelname == expected_level
        ), "Expected a traceback to be logged for an exception"

    @staticmethod
    def test_bus_logs_and_raises_error_on_unexpected_error_while_collecting_events(
        caplog: pytest.LogCaptureFixture,
    ):
        """Test that the message bus logs an error and raises an exception when
        an unexpected error occurs during event collection.
        """
        bus = bootstrap(
            uow=FaultyUnitOfWork(),
            command_handlers={FakeCommand: dummy_command_handler},
        )
        command = FakeCommand()

        expected_content = UNEXPECTED_ERROR_WHILE_COLLECTING_EVENTS_DESCRIPTION.format(
            kind="command", message=command
        )

        with caplog.at_level("ERROR"):
            with pytest.raises(
                Exception, match="Simulated failure in collecting events"
            ):
                bus.handle(command)

        # Check that the expected error message is logged
        assert any(expected_content in record.message for record in caplog.records), (
            f"Expected log message not found: {expected_content}"
        )

        # Check that at least one ERROR log has traceback info
        expected_level = "ERROR"
        assert any(
            record.exc_info is not None
            for record in caplog.records
            if record.levelname == expected_level
        ), "Expected a traceback to be logged for an exception"


class TestEventHandlingEdgeCases:
    """Test suite for edge cases in event handling."""

    @staticmethod
    def test_bus_logs_debug_message_and_continues_on_missing_handler(
        caplog: pytest.LogCaptureFixture,
    ):
        """Test that the bus logs a debug message and continues on missing handler."""
        bus = bootstrap(event_handlers={FakeEvent: []})

        event = FakeEvent()

        expected_content = MISSING_HANDLER_DESCRIPTION.format(
            kind="event", message=event
        )
        with caplog.at_level("DEBUG"):
            bus.handle(event)
        assert any(expected_content in record.message for record in caplog.records)

    @staticmethod
    def test_bus_logs_error_and_continues_on_unexpected_error(
        caplog: pytest.LogCaptureFixture,
    ):
        """Test that an unexpected error while handling an event is logged and continues."""

        bus = bootstrap(event_handlers={FakeEvent: [failing_command_handler]})
        event = FakeEvent()

        expected_content = UNEXPECTED_ERROR_DESCRIPTION.format(
            kind="event", message=event
        )

        with caplog.at_level("ERROR"):
            bus.handle(event)

        # Check that the expected error message is logged
        assert any(expected_content in record.message for record in caplog.records), (
            f"Expected log message not found: {expected_content}"
        )

        # Check that at least one ERROR log has traceback info
        expected_level = "ERROR"
        assert any(
            record.exc_info is not None
            for record in caplog.records
            if record.levelname == expected_level
        ), "Expected a traceback to be logged for an exception"

    @staticmethod
    def test_bus_logs_error_and_continues_on_unexpected_error_while_collecting_events(
        caplog: pytest.LogCaptureFixture,
    ):
        """Test that the message bus logs an error and continues when
        an unexpected error occurs during event collection."""

        bus = bootstrap(
            uow=FaultyUnitOfWork(), event_handlers={FakeEvent: [dummy_event_handler]}
        )
        event = FakeEvent()

        expected_content = UNEXPECTED_ERROR_WHILE_COLLECTING_EVENTS_DESCRIPTION.format(
            kind="event", message=event
        )

        with caplog.at_level("ERROR"):
            bus.handle(event)

        # Check that the expected error message is logged
        assert any(expected_content in record.message for record in caplog.records), (
            f"Expected log message not found: {expected_content}"
        )

        # Check that at least one ERROR log has traceback info
        expected_level = "ERROR"
        assert any(
            record.exc_info is not None
            for record in caplog.records
            if record.levelname == expected_level
        ), "Expected a traceback to be logged for an exception"


class TestEventHandlingLogging:
    """Test suite for event handling logging."""

    @staticmethod
    def test_bus_logs_message_for_event_handling(caplog: pytest.LogCaptureFixture):
        """The bus logs a debug message when handling an event."""
        bus = bootstrap(event_handlers={FakeEvent: [dummy_event_handler]})
        event = FakeEvent()

        with caplog.at_level("DEBUG"):
            bus.handle(event)

        expected_log_message = HANDLING_EVENT_DESCRIPTION.format(
            event=event, handler=dummy_event_handler.__name__
        )
        assert any(
            expected_log_message in record.message for record in caplog.records
        ), f"Expected log message not found: {expected_log_message}"

    @staticmethod
    def test_bus_logs_message_for_command_handling(caplog: pytest.LogCaptureFixture):
        """Test that the bus logs a debug message when handling a command."""
        bus = bootstrap(command_handlers={FakeCommand: dummy_command_handler})
        command = FakeCommand()

        with caplog.at_level("DEBUG"):
            bus.handle(command)

        expected_log_message = HANDLING_COMMAND_DESCRIPTION.format(command=command)
        assert any(
            expected_log_message in record.message for record in caplog.records
        ), f"Expected log message not found: {expected_log_message}"
