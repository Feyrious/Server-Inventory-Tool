"""Exceptions for problems the user or the environment can cause.

Responsibility: one place for the program's own error types, so the menu
and main.py can catch them and show a clear message instead of a traceback.
"""


class PingNotAvailableError(Exception):
    """Raised when the ping command is not installed on this machine."""
