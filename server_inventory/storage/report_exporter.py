"""Exporting the server list as a CSV report.

Responsibility: writing report files to the reports folder.
"""

import csv
from datetime import datetime
from pathlib import Path

from server_inventory.errors import ReportNotSavedError

REPORT_COLUMNS = ["name", "address", "env", "role", "status", "last_checked"]
_FILENAME_TIMESTAMP_FORMAT = "%Y-%m-%d_%H%M"


class ReportExporter:
    """Writes server reports to files in a reports folder."""

    def __init__(self, reports_directory: Path):
        self.reports_directory = reports_directory

    # region Public methods
    def export_csv(self, servers: list[dict]) -> Path:
        """Write all servers to a timestamped CSV file and return its path (G8).

        Raises ReportNotSavedError if the report can't be written.
        """
        report_file = self.reports_directory / self._build_report_filename()

        try:
            self.reports_directory.mkdir(parents=True, exist_ok=True)

            # newline="" stops Windows from adding an empty line between rows
            with open(report_file, "w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=REPORT_COLUMNS, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(servers)
        except OSError as error:
            raise ReportNotSavedError(
                f"Could not save the report {report_file}: {error.strerror}."
            ) from error

        return report_file
    # endregion

    # region Private methods
    def _build_report_filename(self) -> str:
        """Return a filename like inventory_2026-11-17_1337.csv."""
        timestamp = datetime.now().strftime(_FILENAME_TIMESTAMP_FORMAT)
        return f"inventory_{timestamp}.csv"
    # endregion
