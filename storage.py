"""Reading and writing server data (JSON) and exporting reports (CSV).

Responsibility: everything that touches files on disk. No input() or print()
here, so both the text menu and the CLI can reuse these functions.
"""

# TODO: DEFAULT_DATA_FILE constant ("servers.json")
# TODO: get_data_file_path() -> Path        reads INVENTORY_DATA_FILE, falls back to default (G6)
# TODO: load_servers(data_file) -> list      empty list if the file is missing (G5, G7)
# TODO: save_servers(servers, data_file)     called after every change (G5)
# TODO: export_to_csv(servers) -> Path       reports/inventory_YYYY-MM-DD_HHMM.csv, header row (G8)
