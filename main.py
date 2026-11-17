#!/usr/bin/env python3

import argparse

from server_inventory import config
from server_inventory.errors import InventoryError
from server_inventory.exit_status import ExitCode, exit_program
from server_inventory.services.inventory_service import VALID_ENVIRONMENTS, InventoryService
from server_inventory.services.server_checker import ServerChecker
from server_inventory.storage.report_exporter import ReportExporter
from server_inventory.storage.server_repository import ServerRepository
from server_inventory.ui.display import print_server_table
from server_inventory.ui.menu import Menu
from server_inventory.verbose import log_verbose


def main():
    # Setting up CLI parameter arguments
    parser = argparse.ArgumentParser(
        description="A simple CLI tool to check, monitor and generate server status reports."
    )

    actions = parser.add_mutually_exclusive_group()

    # Flag to list servers, optionally filtered with --env
    actions.add_argument(
        "-l", "--list",
        action="store_true",
        help="List all servers, or only those in --env"
    )

    # Flag for checking status on specific server
    actions.add_argument(
        "-c", "--check",
        metavar="NAME",
        help="Check specific server status"
    )

    # Flag for checking status on all servers
    actions.add_argument(
        "-a", "--check-all",
        action="store_true",
        help="Check all servers statuses"
    )

    # Flag for exporting a server status report
    actions.add_argument(
        "-x", "--export",
        action="store_true",
        help="Generate server status report"
    )

    # Filter for --list. It combines with --list, so it is outside the
    # mutually exclusive group, like --verbose (G15: --list --env prod)
    parser.add_argument(
        "-e", "--env",
        choices=VALID_ENVIRONMENTS,
        help="Only list servers in this environment (use with --list)"
    )

    # Flag for setting logging to verbose
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose mode"
    )

    args = parser.parse_args()

    if args.env and not args.list:
        parser.error("--env can only be used together with --list")

    # Route the parsed values to the application. Every error the program
    # knows about ends here with its own exit code instead of a traceback.
    try:
        is_success = process_data(
            list_servers=args.list,
            env=args.env,
            check=args.check,
            check_all=args.check_all,
            export=args.export,
            verbose=args.verbose
        )
    except InventoryError as error:
        exit_program(error.exit_code, str(error))
    except KeyboardInterrupt:
        print()
        exit_program(ExitCode.INTERRUPTED, "Interrupted by the user.")
    except EOFError:
        # End of input (Ctrl+D) at a menu prompt counts as quitting
        print()
        exit_program(ExitCode.OK)

    # The exit code is the result for scripts and pipelines (G16)
    exit_program(ExitCode.OK if is_success else ExitCode.CHECK_FAILED)


def process_data(
    list_servers: bool,
    env: str | None,
    check: str | None,
    check_all: bool,
    export: bool,
    verbose: bool,
) -> bool:
    """Run the chosen action and return False if a check failed or the server does not exist."""
    if verbose:
        config.IS_VERBOSE = True
        log_verbose("Verbose mode is on")

    inventory, exporter = create_services()

    if list_servers:
        log_verbose(f"Action: list servers (environment filter: {env or 'none'})")
        servers = inventory.filter_by_environment(env) if env else inventory.get_all_servers()
        print_server_table(servers)
    elif check:
        log_verbose(f"Action: check server '{check}'")
        return check_one_server(inventory, check)
    elif check_all:
        log_verbose("Action: check all servers")
        all_servers_up = inventory.check_all_servers()
        print_server_table(inventory.get_all_servers())
        return all_servers_up
    elif export:
        log_verbose("Action: export CSV report")
        report_file = exporter.export_csv(inventory.get_all_servers())
        print(f"Report saved to {report_file}")
    else:
        log_verbose("No action given, starting the text menu")
        Menu(inventory, exporter).run()

    return True


def check_one_server(inventory: InventoryService, name: str) -> bool:
    """Check one server, print its row and return True if it is up."""
    try:
        is_up = inventory.check_server(name)
    except ValueError as error:
        print(error)
        return False

    print_server_table([inventory.find_by_name(name)])
    return is_up


def create_services() -> tuple[InventoryService, ReportExporter]:
    """Create the services and connect them (manual dependency injection)."""
    data_file = config.get_data_file_path()
    log_verbose(f"Data file: {data_file} (set {config.DATA_FILE_ENV_VARIABLE} to change it)")
    log_verbose(f"Reports folder: {config.REPORTS_DIRECTORY}")

    repository = ServerRepository(data_file)
    inventory = InventoryService(repository, ServerChecker())
    return inventory, ReportExporter(config.REPORTS_DIRECTORY)


# Script entry point
if __name__ == "__main__":
    main()
