"""Formatting servers for the terminal.

Responsibility: turning data into readable output. Shared by the menu and
the CLI so the table looks the same in both modes.
"""

# One entry per column: (key in the server dict, column title, column width).
# Widths are defined once here, so the header and the rows always line up.
_COLUMNS = [
    ("name", "Name", 10),
    ("address", "Address", 16),
    ("env", "Env", 6),
    ("role", "Role", 13),
    ("status", "Status", 10),
    ("last_checked", "Last checked", 16),
]
_EMPTY_VALUE = "-"


# region Public functions
def print_server_table(servers: list[dict]) -> None:
    """Print the servers as a table with aligned columns (G14)."""
    if not servers:
        print("No servers to show.")
        return

    header = _format_header()
    print(header)
    print("-" * len(header))

    for server in servers:
        print(_format_server_row(server))
# endregion


# region Private functions
def _format_header() -> str:
    return "".join(f"{title:<{width}}" for _, title, width in _COLUMNS)


def _format_server_row(server: dict) -> str:
    # "or" swaps empty values, like a server that was never checked, for "-"
    return "".join(f"{server.get(key) or _EMPTY_VALUE:<{width}}" for key, _, width in _COLUMNS)
# endregion
