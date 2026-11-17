"""Debug messages that are only shown in verbose mode (--verbose).

Responsibility: one place that decides whether a debug message is printed.
The messages go to stderr, so normal output like the server table can still
be redirected to a file without debug lines mixed in.
"""

import sys

from server_inventory import config


def log_verbose(message: str) -> None:
    """Print a debug message if verbose mode is on."""
    if config.IS_VERBOSE:
        print(f"[verbose] {message}", file=sys.stderr)
