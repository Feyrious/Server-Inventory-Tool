#!/usr/bin/env python3

import argparse

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
        choices=["dev", "test", "prod"],
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
    process_data(
        list_all=args.list_all,
        list_env=args.list_env,
        check=args.check,
        check_all=args.check_all,
        export=args.export,
        verbose=args.verbose
    )

def process_data(list_all: bool, list_env: str | None, check: str | None, check_all: bool, export: bool, verbose: bool):
    if verbose:
        # Set Logging to Verbose
        print("Verbose Mode On")

    if list_all:
        # List all registered servers
        print("Server Inventory Tool CLI: List All Servers")
    elif list_env:
        # List all registered servers in environment
        print(f"Server Inventory Tool CLI: List by Environment - {list_env}")
    elif check:
        # Check server status
        print("Server Inventory Tool CLI: Check Server Status")
    elif check_all:
        # Check status for all servers
        print("Server Inventory Tool CLI: Check All Servers")
    elif export:
        # Export report
        print("Server Inventory Tool CLI: Generate server status report")
    else:
        # Present tool menu
        print("Server Inventory Tool Menu")


# Script entry point
if __name__ == "__main__":
    main()