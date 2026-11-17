"""Loading and saving the server list as JSON.

Responsibility: the only place that reads or writes the data file. No input()
or print() here, so both the text menu and the CLI can reuse it.
"""

import json
from pathlib import Path


class ServerRepository:
    """Reads and writes the list of server dictionaries to a JSON file."""

    def __init__(self, data_file: Path):
        self.data_file = data_file

    # region Public methods
    def load(self) -> list[dict]:
        """Return all servers from the data file, or an empty list if the file is missing (G5, G7)."""
        if not self.data_file.exists():
            return []

        with open(self.data_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def save(self, servers: list[dict]) -> None:
        """Write all servers to the data file, replacing its previous content (G5)."""
        with open(self.data_file, "w", encoding="utf-8") as file:
            json.dump(servers, file, indent=2, ensure_ascii=False)
            file.write("\n")
    # endregion
