"""Loading and saving the server list as JSON.

Responsibility: the only place that reads or writes the data file. No input()
or print() here, so both the text menu and the CLI can reuse it.
"""

# TODO: class ServerRepository
#       __init__(data_file: Path)
#       load() -> list[dict]         empty list if the file is missing (G5, G7)
#       save(servers: list[dict])    called after every change (G5)
