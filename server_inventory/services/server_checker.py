"""Network checks against servers using external commands (ping).

Responsibility: run checks and update a server's status. The check logic
is written once here and reused by both the menu and the CLI (G18).
"""

# TODO: class ServerChecker
#       ping(address) -> bool                  subprocess.run() with the command as a list, exit code decides (G9)
#       check_server(server: dict)             sets status "up"/"down" and last_checked "YYYY-MM-DD HH:MM" (G10)
#       check_all(servers: list[dict]) -> bool True if every server is up (used for exit codes, G16)
