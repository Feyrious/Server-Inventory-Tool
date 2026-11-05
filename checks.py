"""Network checks against servers using external commands (ping).

Responsibility: run checks and update a server's status. The check logic
is written once here and reused by both the menu and the CLI (G18).
"""

# TODO: ping_address(address) -> bool        subprocess.run() with the command as a list, exit code decides (G9)
# TODO: check_server(server)                 sets status to "up"/"down" and last_checked "YYYY-MM-DD HH:MM" (G10)
# TODO: check_all_servers(servers) -> bool   True if every server is up (used for exit codes, G16)
