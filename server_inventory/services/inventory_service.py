"""Business rules for the server list: find, add, remove and filter servers.

Responsibility: pure logic on the list of server dictionaries. No input(),
print() or file access, so the rules live in one place and are easy to test.
"""

# TODO: VALID_ENVIRONMENTS and VALID_STATUSES constants (G2)
# TODO: class InventoryService
#       __init__(repository: ServerRepository)   loads the servers once
#       find_by_name(name) -> dict | None
#       is_valid_environment(env) -> bool        (G3)
#       add_server(name, address, env, role)     status always "unknown", no duplicate names (G2, G4)
#       remove_server(name)                      saves after the change (G5)
#       filter_by_environment(env) -> list[dict]
