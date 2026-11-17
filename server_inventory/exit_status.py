"""Ending the program with the right exit code (G16).

In verbose mode the exit code and any message are printed before exiting.
"""

import sys

from server_inventory import config


# region Public functions
def status_ok():
    _print_system_info(0)
    sys.exit(0)


def status_failed():
    """Exit with code 1, e.g. when a checked server is down or does not exist (G16)."""
    _print_system_info(1)
    sys.exit(1)


def error_read_file(file_name: str):
    _print_system_info(1, "Error reading file " + file_name)
    sys.exit(1)
# endregion


# region Private functions
def _print_system_info(code: int, message: str = ""):
    if config.IS_VERBOSE:
        if len(message) > 0:
            print(message)

        print(f"Process finished with exit code {code}")
# endregion
