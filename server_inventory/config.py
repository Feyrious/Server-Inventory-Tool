"""Runtime settings: verbose mode and where data and reports are stored."""

import os
from pathlib import Path

IS_VERBOSE = False

# The project root folder (the one containing main.py). Default paths are
# anchored here so the tool finds its files no matter where it is run from.
PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent

DATA_FILE_ENV_VARIABLE = "INVENTORY_DATA_FILE"
DEFAULT_DATA_FILE = PROJECT_DIRECTORY / "servers.json"
REPORTS_DIRECTORY = PROJECT_DIRECTORY / "reports"


def get_data_file_path() -> Path:
    """Return the data file from INVENTORY_DATA_FILE, or the default if it is not set (G6)."""
    data_file_from_env = os.environ.get(DATA_FILE_ENV_VARIABLE)

    if data_file_from_env:
        return Path(data_file_from_env)

    return DEFAULT_DATA_FILE


def new_line():
    return os.linesep
