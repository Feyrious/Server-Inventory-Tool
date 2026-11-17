"""Business rules for the server list: find, add, remove, filter and check servers.

Responsibility: the rules for the list of server dictionaries. Every change
to the list goes through this class and is saved right away. No input() or
print(), so the menu and the CLI share the same rules.
"""

from server_inventory.services.server_checker import ServerChecker
from server_inventory.storage.server_repository import ServerRepository

VALID_ENVIRONMENTS = ["dev", "test", "prod"]
VALID_STATUSES = ["up", "down", "unknown"]


def is_valid_environment(env: str) -> bool:
    """Return True if env is one of the allowed environments (G2, G3)."""
    return env in VALID_ENVIRONMENTS


class InventoryService:
    """Holds the servers while the program runs and saves every change."""

    def __init__(self, repository: ServerRepository, checker: ServerChecker):
        self.repository = repository
        self.checker = checker
        self.servers = repository.load()

    # region Public methods
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
        self._save()
        return new_server

    def remove_server(self, name: str) -> dict:
        """Remove the server with this name and save (G5).

        Raises ValueError if no server has that name.
        """
        server = self._get_existing_server(name)
        self.servers.remove(server)
        self._save()
        return server

    def check_server(self, name: str) -> bool:
        """Check one server, save the new status and return True if it is up (G9, G10).

        Raises ValueError if no server has that name.
        """
        server = self._get_existing_server(name)
        is_up = self.checker.check_server(server)
        self._save()
        return is_up

    def check_all_servers(self) -> bool:
        """Check every server, save the new statuses and return True if all are up (G10, G16)."""
        all_servers_up = self.checker.check_all(self.servers)
        self._save()
        return all_servers_up
    # endregion

    # region Private methods
    def _get_existing_server(self, name: str) -> dict:
        """Return the server with this name, or raise ValueError if there is none."""
        server = self.find_by_name(name)

        if server is None:
            raise ValueError(f"No server named '{name}' exists.")

        return server

    def _save(self) -> None:
        self.repository.save(self.servers)
    # endregion
