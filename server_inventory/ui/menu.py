"""Interactive text menu.

Responsibility: talking to the user (input/print) and calling the services.
Contains no business rules itself.
"""

from server_inventory.errors import PingNotAvailableError
from server_inventory.services.inventory_service import (
    VALID_ENVIRONMENTS,
    InventoryService,
    is_valid_environment,
)
from server_inventory.storage.report_exporter import ReportExporter
from server_inventory.ui.display import print_server_table
from server_inventory.verbose import log_verbose

_QUIT_CHOICE = "0"
_PROD_ENVIRONMENT = "prod"
_CONFIRM_ANSWER = "yes"


class Menu:
    """Text menu that runs in a loop until the user chooses to quit (G11)."""

    def __init__(self, inventory: InventoryService, exporter: ReportExporter):
        self.inventory = inventory
        self.exporter = exporter

        # Menu choice -> (text shown in the menu, method that handles it)
        self._menu_items = {
            "1": ("Show all servers", self._show_all_servers),
            "2": ("Show servers in an environment", self._show_servers_in_environment),
            "3": ("Add a server", self._add_server),
            "4": ("Remove a server", self._remove_server),
            "5": ("Check a server", self._check_server),
            "6": ("Check all servers", self._check_all_servers),
            "7": ("Export report as CSV", self._export_report),
        }

    # region Public methods
    def run(self) -> None:
        """Show the menu and handle choices until the user quits (G11, G12)."""
        while True:
            self._print_menu()
            choice = input("Choose an option: ").strip()
            log_verbose(f"Menu choice: '{choice}'")

            if choice == _QUIT_CHOICE:
                print("Goodbye!")
                return

            menu_item = self._menu_items.get(choice)

            if menu_item is None:
                print(f"'{choice}' is not a valid choice, please try again.")
                continue

            _, handle_choice = menu_item
            handle_choice()
    # endregion

    # region Private methods
    def _print_menu(self) -> None:
        print()
        print("=== Server Inventory Tool ===")

        for choice, (text, _) in self._menu_items.items():
            print(f"{choice}. {text}")

        print(f"{_QUIT_CHOICE}. Quit")

    def _show_all_servers(self) -> None:
        print_server_table(self.inventory.get_all_servers())

    def _show_servers_in_environment(self) -> None:
        env = self._ask_for_environment()
        print_server_table(self.inventory.filter_by_environment(env))

    def _add_server(self) -> None:
        name = input("Name: ").strip()
        address = input("Address: ").strip()
        env = self._ask_for_environment()
        role = input("Role: ").strip()

        try:
            self.inventory.add_server(name, address, env, role)
            print(f"Server '{name}' was added.")
        except ValueError as error:
            print(error)

    def _remove_server(self) -> None:
        name = input("Name of the server to remove: ").strip()
        server = self.inventory.find_by_name(name)

        if server is None:
            print(f"No server named '{name}' exists.")
            return

        # Removing a production server needs an extra confirmation (G13)
        if server["env"] == _PROD_ENVIRONMENT and not self._confirm(
            f"'{name}' is a production server. Type '{_CONFIRM_ANSWER}' to remove it: "
        ):
            print("Nothing was removed.")
            return

        self.inventory.remove_server(name)
        print(f"Server '{name}' was removed.")

    def _check_server(self) -> None:
        name = input("Name of the server to check: ").strip()
        print(f"Checking {name}...")

        try:
            is_up = self.inventory.check_server(name)
        except (ValueError, PingNotAvailableError) as error:
            print(error)
            return

        print(f"{name} is {'up' if is_up else 'down'}.")

    def _check_all_servers(self) -> None:
        print("Checking all servers, this can take a few seconds...")

        try:
            self.inventory.check_all_servers(on_server_checked=self._print_check_result)
        except PingNotAvailableError as error:
            print(error)
            return

        print()
        print_server_table(self.inventory.get_all_servers())

    def _print_check_result(self, server: dict, is_up: bool) -> None:
        """Print one line as soon as a server has been checked, so the user sees progress."""
        print(f"  {server['name']:<10} {'up' if is_up else 'down'}")

    def _export_report(self) -> None:
        report_file = self.exporter.export_csv(self.inventory.get_all_servers())
        print(f"Report saved to {report_file}")

    def _ask_for_environment(self) -> str:
        """Ask until the user enters a valid environment (G3)."""
        valid_choices = ", ".join(VALID_ENVIRONMENTS)

        while True:
            env = input(f"Environment ({valid_choices}): ").strip()

            if is_valid_environment(env):
                return env

            print(f"'{env}' is not a valid environment, please try again.")

    def _confirm(self, question: str) -> bool:
        return input(question).strip().lower() == _CONFIRM_ANSWER
    # endregion
