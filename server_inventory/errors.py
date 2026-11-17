"""Exceptions for problems the user or the environment can cause.

Responsibility: one place for the program's own error types. Each error
knows which exit code it ends the program with, so main.py can handle all
of them with a single except block instead of a traceback.
"""

from server_inventory.exit_status import ExitCode


class InventoryError(Exception):
    """Base class for the program's own errors."""

    exit_code = ExitCode.CHECK_FAILED


class DataFileInvalidError(InventoryError):
    """The data file is not valid JSON, or does not contain a list of servers."""

    exit_code = ExitCode.DATA_FILE_INVALID


class DataFileUnreadableError(InventoryError):
    """The data file exists but cannot be read, e.g. because of permissions."""

    exit_code = ExitCode.DATA_FILE_UNREADABLE


class DataFileNotSavedError(InventoryError):
    """The data file cannot be written."""

    exit_code = ExitCode.DATA_FILE_NOT_SAVED


class ReportNotSavedError(InventoryError):
    """The CSV report cannot be written."""

    exit_code = ExitCode.REPORT_NOT_SAVED


class PingNotAvailableError(InventoryError):
    """The ping command is not installed on this machine."""

    exit_code = ExitCode.PING_NOT_AVAILABLE
