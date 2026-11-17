"""Network checks against servers using external commands (ping).

Responsibility: run checks and update a server's status. The check logic
is written once here and reused by both the menu and the CLI (G18).
"""

import subprocess
from datetime import datetime

# Linux ping flags: -c = number of packets, -W = seconds to wait for a reply.
# Without a timeout an unreachable address can hang for a long time.
_PING_PACKET_COUNT = "1"
_PING_TIMEOUT_SECONDS = "2"
_LAST_CHECKED_FORMAT = "%Y-%m-%d %H:%M"


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

    def check_all(self, servers: list[dict]) -> bool:
        """Check every server and return True only if all of them are up (G16)."""
        all_servers_up = True

        # A plain loop instead of all(...), because all() stops at the first
        # server that is down and would leave the rest unchecked.
        for server in servers:
            if not self.check_server(server):
                all_servers_up = False

        return all_servers_up
    # endregion

    # region Private methods
    def _build_ping_command(self, address: str) -> list[str]:
        """Return the ping command as a list, so the address is never parsed by a shell."""
        return ["ping", "-c", _PING_PACKET_COUNT, "-W", _PING_TIMEOUT_SECONDS, address]

    def _ping(self, address: str) -> bool:
        """Return True if the address answers ping, judged by the exit code (G9)."""
        result = subprocess.run(
            self._build_ping_command(address),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    # endregion
