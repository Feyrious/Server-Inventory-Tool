"""Ending the program with the right exit code (G16).

Every way the program can end has its own exit code in ExitCode, so a script
or pipeline can tell what happened without reading the text output.
"""

import sys
from enum import IntEnum
from typing import NoReturn

from server_inventory.verbose import log_verbose


class ExitCode(IntEnum):
    """All exit codes the program can end with (documented in README.md)."""

    OK = 0
    CHECK_FAILED = 1          # a checked server is down, or does not exist (G16)
    INVALID_ARGUMENTS = 2     # unknown or conflicting flags (set by argparse)
    DATA_FILE_INVALID = 3     # the data file is not valid JSON or not a list of servers
    DATA_FILE_UNREADABLE = 4  # the data file exists but cannot be read, e.g. no permission
    DATA_FILE_NOT_SAVED = 5   # the data file cannot be written
    REPORT_NOT_SAVED = 6      # the CSV report cannot be written
    PING_NOT_AVAILABLE = 7    # the ping command is not installed
    INTERRUPTED = 130         # stopped with Ctrl+C (Unix convention: 128 + signal 2)


# region Public functions
def exit_program(code: ExitCode, error_message: str = "") -> NoReturn:
    """Print the error message (if any) and end the program with this exit code."""
    if error_message:
        print(error_message, file=sys.stderr)

    _print_system_info(code)
    sys.exit(code)
# endregion


# region Private functions
def _print_system_info(code: ExitCode) -> None:
    log_verbose(f"Process finished with exit code {code.value} ({code.name})")
# endregion
