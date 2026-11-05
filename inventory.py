"""Business rules for the server list: find, add, remove and filter servers.

Responsibility: pure logic on the list of server dictionaries. No input(),
print() or file access, so the rules live in one place and are easy to test.
"""

# TODO: VALID_ENVIRONMENTS and VALID_STATUSES constants (G2)
# TODO: find_server_by_name(servers, name) -> dict | None
# TODO: is_valid_environment(env) -> bool                 (G3)
# TODO: add_server(servers, name, address, env, role)     status always "unknown", no duplicate names (G2, G4)
# TODO: remove_server(servers, name)
# TODO: filter_by_environment(servers, env) -> list
