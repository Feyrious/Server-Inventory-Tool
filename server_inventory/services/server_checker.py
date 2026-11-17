"""Network checks against servers using external commands (ping).

Responsibility: run checks and update a server's status. The check logic
is written once here and reused by both the menu and the CLI (G18).
"""

import subprocess
from collections.abc import Callable
from datetime import datetime

from server_inventory.errors import PingNotAvailableError
from server_inventory.verbose import log_verbose

# Linux ping flags: -c = number of packets, -W = seconds to wait for a reply.
# Without a timeout an unreachable address can hang for a long time.
_PING_PACKET_COUNT = "1"
_PING_TIMEOUT_SECONDS = "2"
_LAST_CHECKED_FORMAT = "%Y-%m-%d %H:%M"

# A function that is called with (server, is_up) after each server is checked,
# so a caller like the menu can show progress without this class printing.
ServerCheckedCallback = Callable[[dict, bool], None]


class ServerChecker:
    """Checks whether servers respond and updates their status."""

    # region Public methods
    def check_server(self, server: dict) -> bool:
        """Ping one server, update its status and last_checked, and return True if it is up (G10).

        The server dict is changed in place; the caller saves the list afterwards.
        """
        is_up = self._ping(server["address"])

        server["status"] = "up" if is_up else "down"
        server["last_checked"] = datetime.now().strftime(_LAST_CHECKED_FORMAT)

        return is_up

    def check_all(
        self,
        servers: list[dict],
        on_server_checked: ServerCheckedCallback | None = None,
    ) -> bool:
        """Check every server and return True only if all of them are up (G16).

        If on_server_checked is given, it is called after each server is checked.
        """
        all_servers_up = True

        # A plain loop instead of all(...), because all() stops at the first
        # server that is down and would leave the rest unchecked.
        for server in servers:
            is_up = self.check_server(server)

            if not is_up:
                all_servers_up = False

            if on_server_checked is not None:
                on_server_checked(server, is_up)

        return all_servers_up
    # endregion

    # region Private methods
    def _build_ping_command(self, address: str) -> list[str]:
        """Return the ping command as a list, so the address is never parsed by a shell."""
        return ["ping", "-c", _PING_PACKET_COUNT, "-W", _PING_TIMEOUT_SECONDS, address]

    def _ping(self, address: str) -> bool:
        """Return True if the address answers ping, judged by the exit code (G9).

        Raises PingNotAvailableError if the ping command is not installed.
        """
        command = self._build_ping_command(address)
        log_verbose(f"Running command: {' '.join(command)}")

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            raise PingNotAvailableError(
                "The 'ping' command was not found. "
                "Install it (e.g. the iputils-ping package) to check servers."
            ) from None

        log_verbose(f"ping exited with code {result.returncode} for {address}")
        return result.returncode == 0
    # endregion
