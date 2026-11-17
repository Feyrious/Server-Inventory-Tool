"""Business rules for the server list: find, add, remove and filter servers.

Responsibility: the rules for the list of server dictionaries. No input()
or print(), so the menu and the CLI share the same rules.
"""

from server_inventory.storage.server_repository import ServerRepository

VALID_ENVIRONMENTS = ["dev", "test", "prod"]
VALID_STATUSES = ["up", "down", "unknown"]


def is_valid_environment(env: str) -> bool:
    """Return True if env is one of the allowed environments (G2, G3)."""
    return env in VALID_ENVIRONMENTS


class InventoryService:
    """Holds the servers while the program runs and saves every change."""

    def __init__(self, repository: ServerRepository):
        self.repository = repository
        self.servers = repository.load()

    def get_all_servers(self) -> list[dict]:
        return self.servers

    def find_by_name(self, name: str) -> dict | None:
        """Return the server with this name, or None if there is none."""
        for server in self.servers:
            if server["name"] == name:
                return server

        return None

    def filter_by_environment(self, env: str) -> list[dict]:
        return [server for server in self.servers if server["env"] == env]

    def add_server(self, name: str, address: str, env: str, role: str) -> dict:
        """Add a new server with status "unknown" and save (G2, G4, G5).

        Raises ValueError if the name is taken or the environment is invalid.
        """
        if self.find_by_name(name) is not None:
            raise ValueError(f"A server named '{name}' already exists.")

        if not is_valid_environment(env):
            raise ValueError(f"'{env}' is not a valid environment.")

        new_server = {
            "name": name,
            "address": address,
            "env": env,
            "role": role,
            "status": "unknown",
            "last_checked": "",
        }
        self.servers.append(new_server)
        self.save()
        return new_server

    def remove_server(self, name: str) -> dict:
        """Remove the server with this name and save (G5).

        Raises ValueError if no server has that name.
        """
        server = self.find_by_name(name)

        if server is None:
            raise ValueError(f"No server named '{name}' exists.")

        self.servers.remove(server)
        self.save()
        return server

    def save(self) -> None:
        """Save the current server list, e.g. after a status check (G5, G10)."""
        self.repository.save(self.servers)
