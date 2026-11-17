#!/usr/bin/env python3

import argparse
import json

from server_inventory import config, exit_status
from server_inventory.services.inventory_service import VALID_ENVIRONMENTS, InventoryService
from server_inventory.services.server_checker import ServerChecker
from server_inventory.storage.report_exporter import ReportExporter
from server_inventory.storage.server_repository import ServerRepository
from server_inventory.ui.display import print_server_table
from server_inventory.ui.menu import Menu


def main():
    # Setting up CLI parameter arguments
    parser = argparse.ArgumentParser(
        description="A simple CLI tool to check, monitor and generate server status reports."
    )

    actions = parser.add_mutually_exclusive_group()

    # Flag to list all servers in this tool
    actions.add_argument(
        "-l", "--list-all",
        action="store_true",
        help="List all servers"
    )

    # Flag to list all servers with a specific environment
    actions.add_argument(
        "-e", "--list-env",
        choices=VALID_ENVIRONMENTS,
        help="List all servers in provided environment"
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

    # Flag for setting logging to verbose
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose mode"
    )

    args = parser.parse_args()

    # Route the parsed values to the application
    is_success = process_data(
        list_all=args.list_all,
        list_env=args.list_env,
        check=args.check,
        check_all=args.check_all,
        export=args.export,
        verbose=args.verbose
    )

    # The exit code is the result for scripts and pipelines (G16)
    if is_success:
        exit_status.status_ok()
    else:
        exit_status.status_failed()


def process_data(list_all: bool, list_env: str | None, check: str | None, check_all: bool, export: bool, verbose: bool) -> bool:
    """Run the chosen action and return False if a check failed or the server does not exist."""
    if verbose:
        config.IS_VERBOSE = True

    inventory, exporter = create_services()

    if list_all:
        print_server_table(inventory.get_all_servers())
    elif list_env:
        print_server_table(inventory.filter_by_environment(list_env))
    elif check:
        return check_one_server(inventory, check)
    elif check_all:
        all_servers_up = inventory.check_all_servers()
        print_server_table(inventory.get_all_servers())
        return all_servers_up
    elif export:
        report_file = exporter.export_csv(inventory.get_all_servers())
        print(f"Report saved to {report_file}")
    else:
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

    try:
        inventory = InventoryService(ServerRepository(data_file), ServerChecker())
        return inventory, ReportExporter(config.REPORTS_DIRECTORY)
    except json.JSONDecodeError:
        exit_status.error_read_file(str(data_file))


# Script entry point
if __name__ == "__main__":
    main()
