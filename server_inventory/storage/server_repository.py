"""Loading and saving the server list as JSON.

Responsibility: the only place that reads or writes the data file. No input()
or print() here, so both the text menu and the CLI can reuse it.
"""

import json
from pathlib import Path

from server_inventory.errors import (
    DataFileInvalidError,
    DataFileNotSavedError,
    DataFileUnreadableError,
)


class ServerRepository:
    """Reads and writes the list of server dictionaries to a JSON file."""

    def __init__(self, data_file: Path):
        self.data_file = data_file

    # region Public methods
    def load(self) -> list[dict]:
        """Return all servers from the data file, or [] if the file is missing (G5, G7).

        Raises DataFileInvalidError or DataFileUnreadableError if the file can't be used.
        """
        if not self.data_file.exists():
            return []

        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                servers = json.load(file)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise DataFileInvalidError(
                f"The data file {self.data_file} is not valid JSON."
            ) from error
        except OSError as error:
            raise DataFileUnreadableError(
                f"Could not read the data file {self.data_file}: {error.strerror}."
            ) from error

        if not isinstance(servers, list):
            raise DataFileInvalidError(
                f"The data file {self.data_file} must contain a list of servers."
            )

        return servers

    def save(self, servers: list[dict]) -> None:
        """Write all servers to the data file, replacing its previous content (G5).

        Raises DataFileNotSavedError if the file can't be written.
        """
        try:
            # The data file may point to a folder that doesn't exist yet
            self.data_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.data_file, "w", encoding="utf-8") as file:
                json.dump(servers, file, indent=2, ensure_ascii=False)
                file.write("\n")
        except OSError as error:
            raise DataFileNotSavedError(
                f"Could not save the data file {self.data_file}: {error.strerror}."
            ) from error
    # endregion
