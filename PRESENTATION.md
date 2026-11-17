# Presentation
## How AI was used in this project

*So for this assignment, with about 6 years of previous C# .NET development, 
I chose to use an AI coding assistant since my focus would not be on learning 
how to code, but instead learning how to use Python and its idioms and libraries.*
  
*So with this in mind I set out to set up specific roles for me and the coding 
agent for this project, where I would take responsibility for the architectural 
decisions, doing code reviews and questioning any choices made in implementing the code. 
While the coding agent would focus on implementing the code, keeping track of the 
requirements and also educate me in how Python works compared to how it's done in .NET.*  
  
***My role as a Tech Lead***
* Owning the architectural and design decisions
* Using English terminology as it's the default in IT
* Performing code reviews and questioning the implementation of the code
* Keeping commits small, with larger changes split up so each commit only touches 
  one file, for easier reviewing and traceability
* Following OOP architecture
  * Created separate modules to separate logical responsibilities
  * Using classes for encapsulation and separation of concerns
* Structure methods into private/public regions
* Testing and merging of PRs into the code base
  
***The Coding Agent's Role***
* Structured the project based on directions from me
* Keeping track of the code requirements
* Implemented code based on the requirements and with directions from me
* Handled the initial testing of the implemented code
* Wrote PR messages to cover all the changes made
* Acted as a tutor and described how the code worked and how it differs from .NET

## 1. Three parts of the code and how their syntax works

### Ping Command Builder
*Code Link: [`ServerChecker._build_ping_command()`](server_inventory/services/server_checker.py#L67)*

Just like SQL injections, it is possible to also get shell injections if you 
are not careful, so due to that a method was added to build the ping command
from the settings and the address argument provided.

The method returns a list of strings (`-> list[str]`) instead of one command string,
like `["ping", "-c", "1", "-W", "2", address]`. That list is then passed straight to
`subprocess.run()` in `_ping()` without `shell=True`, so no shell ever reads the
command. Each item in the list becomes exactly one argument to `ping`.

In this case trying to inject anything into the shell, like `127.0.0.1; rm -rf /`,
will only result in a strange host name that ping can't find, since the whole 
address ends up as one single argument.

### Having the menu items in a dictionary
*Code Link: [`Menu.__init__()` → `self._menu_items`](server_inventory/ui/menu.py#L30)*

To simplify the code and link a menu option to an actual action, the implementation is
a dictionary with a key (menu number) and a tuple, that itself has the menu text string 
and a method reference in it (like an `Action` in C#). Example: `{"1": ("Show all servers", self._show_all_servers)}`.
Note that the method is written without `()`, so it is stored and not called.
  
Later when picking a menu item in [`Menu.run()`](server_inventory/ui/menu.py#L41), it checks the choice against the
keys with `self._menu_items.get(choice)`, which returns `None` instead of raising an error
if it's not a valid choice. Then it unpacks the tuple (discarding the first value: `_, handle_choice = menu_item`) and then
runs the method that it unpacked with `handle_choice()`.

The same dictionary is also used by `_print_menu()` to print the menu, so adding a new
option only needs one new line in the dictionary.

### Check all servers with a callback
*Code Link: [`ServerChecker.check_all()`](server_inventory/services/server_checker.py#L41)*

For a short list of servers this is mostly not an issue, but the more servers that are added
the longer a check will take, and with up to a thousand servers each taking up to a second
or two to respond that might add up to half an hour of run time.  

To combat this and make sure that the user knows that the script is still running, an
implementation of a callback was added for each server check. This allows the caller to
pass in a method to (in this case) print a message for each server being tested and show
the result of the check straight away in the terminal.

The syntax for this is:
- `on_server_checked: ServerCheckedCallback | None = None` - an optional parameter, where
  `ServerCheckedCallback` is a type hint for a function that takes a server dict and a bool.
- `for server in servers:` - a loop that checks every server. A plain loop is used instead of
  `all()`, since `all()` stops at the first server that is down and leaves the rest unchecked.
- `if on_server_checked is not None:` - a condition so the callback is only called if one was
  passed in, and then it's called like any other function: `on_server_checked(server, is_up)`.
- `return all_servers_up` - returns `True` only if every server is up.

The callback can be ignored if not in use, for example when used in a pipeline since 
it's just the exit code that matters in that case. That is why
[`process_data()`](main.py#L122) in `main.py` calls `check_all_servers()` without one, 
while the menu passes in `_print_check_result`.

## 2. Why use a list of dictionaries to represent the servers

Using a list to hold all the servers keeps them in order, makes it easy to loop over 
or filter them, and maps directly to a JSON array. The list is created when loading 
the data file in [`ServerRepository.load()`](server_inventory/storage/server_repository.py#L25)
and is then held by the `InventoryService`.

Using a dictionary (key:value) for each server allows for a 1:1 mapping straight to JSON 
for storage, as well as making it easy to iterate over all values. Another added 
bonus is that it's easier to map a dictionary over to a CSV file, using the key as 
the header for a column and its values each as a separate row with `DictWriter`.

The structure and data types in use are as follows, where a new server dict is built in
[`InventoryService.add_server()`](server_inventory/services/inventory_service.py#L44):

`name: str` - The name of the server  
`address: str` - Network address to the server  
`env: str` - What environment it's running in (dev, test or prod)  
`role: str` - What it's used for/description  
`status: str` - Needs a valid status of up, down or unknown  
`last_checked: str` - JSON does not have a date type (formatted YYYY-MM-DD HH:MM)

Normally as a C# developer I would opt for a class to represent the server, and then
have that class live inside a list of that object. This would allow me to add methods
to this class to for example add validation, keeping the code a bit more clean and 
giving real type safety, which a dict doesn't have. But since the assignment (G1) 
requires each server to be a dictionary, the classes in this project are only used 
for the services and the storage, while the servers themselves stay as dicts.

## 3. Why use JSON for the data but CSV for the report

Using JSON as the storage format is mostly due to the broad adoption of using JSON
for sending/receiving data. This is due to the small metadata footprint it has if
we compare it to something like XML but still keeps it in a structured way compared
to a plain text file, or in our case, a CSV file. The CSV does not keep the data 
structure and also does not keep the data type, but is mainly used to represent data
in an easy, readable way for people to look at the data.

Since the program reads the data file back every time it starts, the structure has to
survive the round trip. In [`ServerRepository.load()`](server_inventory/storage/server_repository.py#L25)
and [`save()`](server_inventory/storage/server_repository.py#L54), `json.load()` gives back the 
exact same list of dicts that `json.dump()` wrote. The report on the other hand is only
written by [`ReportExporter.export_csv()`](server_inventory/storage/report_exporter.py#L24)
and never read back by the program, so losing the structure is fine there.

So the summary is that JSON is better for storing the data, while the CSV format is
better as an output format for humans to read when needed.

## 4. How the program is split into modules and functions

Here is the basic run-down of the program structure used:
- Entry point and main modules
  - `main.py` - This is the entry point of the program. It reads the CLI arguments with
    argparse, builds and connects the services in `create_services()` and routes 
    each request to the right action in `process_data()`.
  - `services/` - Handles the server inventory and checking the server status.
    - `inventory_service.py` - The rules: find, filter, add and remove servers, 
      and saving after every change.
    - `server_checker.py` - Pings a server and updates its status.
  - `storage/` - Takes care of loading, storing and generating files on the system.
    - `server_repository.py` - Reads and writes the JSON data file.
    - `report_exporter.py` - Writes the CSV report.
  - `ui/` - Presents the interface and displays information to the user.
    - `menu.py` - The interactive text menu.
    - `display.py` - Prints the server table.
- Support modules: 
  - `config.py` - Program settings 
  - `errors.py` - The program's own exceptions, each one knowing its exit code
  - `exit_status.py` - Exit codes used by the program
  - `verbose.py` - Prints debug messages to stderr, but only when `--verbose` is on

The main rule is that the services never use `print()` or `input()`, and never decide 
the exit code. That is left to the menu and `main.py`, so both can share the same logic.

## 5. Standard library modules and what they are used for

| Imported Module | Where it's used | What it's used for |
|---|---|---|
| `json` | `storage/server_repository.py` | Read and write the data file |
| `csv` | `storage/report_exporter.py` | Write the report with `DictWriter` (header row) |
| `pathlib` (`Path`) | `config.py`, `server_repository.py`, `report_exporter.py` | Paths, `exists()`, `mkdir(parents=True, exist_ok=True)`, joining with `/` |
| `os` | `config.py` | `os.environ.get()` reads `INVENTORY_DATA_FILE` |
| `datetime` | `server_checker.py`, `report_exporter.py` | Timestamp for `last_checked` and the report filename |
| `subprocess` | `server_checker.py` | `subprocess.run()` runs `ping` with the command as a list |
| `argparse` | `main.py` | Flags, `--help`, mutually exclusive actions, `choices` |
| `sys` | `exit_status.py`, `verbose.py` | `sys.exit()` for exit codes, `sys.stderr` for errors and verbose output |
| `enum` (`IntEnum`) | `exit_status.py` | Named exit codes that are real integers |
| `typing` (`NoReturn`), `collections.abc` (`Callable`) | `exit_status.py`, `server_checker.py` | Type hints only |

## 6. Three examples of good practice and why they are good

A few best practices have already been mentioned above, but here are a few more  
that focus more on coding best practices.

- **Logic written once** - The `InventoryService` is used by both the menu
  in `ui/menu.py` and the CLI in `main.py`, which reduces the risk of errors and any 
  changes get applied to both. In this way there is no risk that one part of the code 
  handles data in a different way and in the worst case loses or corrupts the data it handles.
- **Descriptive names and type hints** - Making sure to have good and clear names  
  for all methods and variables. This also includes adding the expected parameter and
  return types to methods, like `find_by_name(self, name: str) -> dict | None` in
  `InventoryService`. Python doesn't enforce type hints, but they document what is 
  expected and let PyCharm warn about mistakes, keeping the code clear.
- **Version control** - I'm using Git with Git Flow as the foundation, enforcing  
  a PR for each new feature that gets merged into a development branch. Each PR has  
  smaller commits added to it for better history and then releases are pushed to `main`.

## 7. Sources and tools used, and for what

- **Course material**: 
  - The *Service Status Tool* course project I made and the presentations are used  
    for general structure when setting up a Python project and as example code.
- **Python documentation** 
  - Using the official documentation to find information about commonly  
    used modules, how they work and how to use them.
- **`ASSIGNMENT.md`**
  - Used as the base requirements and as a checklist when doing reviews.
- **Claude Code (AI assistant)**
  - See *How AI was used in this project* above.
- **PyCharm**
  - Code editor of choice to edit and review the code.
- **Git and GitHub**
  - Used for version control, doing code reviews and checking pull requests.

## Assignment notes

This project is a course assignment ("Inlämningsuppgift: Server Inventory
Tool", *Programmering med Python*). The full assignment is in
[`ASSIGNMENT.md`](ASSIGNMENT.md).

### Swedish names in the assignment → names in this project

All code and documentation are in English (approved by the teacher). This
table maps the assignment's names to the ones used here:

| Assignment (Swedish) | This project | Requirement |
|---|---|---|
| `namn`, `adress`, `miljo`, `roll`, `status`, `senast_kontrollerad` | `name`, `address`, `env`, `role`, `status`, `last_checked` | G1 |
| `dev`, `test`, `prod` / `up`, `down`, `unknown` | unchanged | G2 |
| `servrar.json` | `servers.json` | G5, G7 |
| `INVENTORY_DATAFIL` | `INVENTORY_DATA_FILE` | G6 |
| `rapporter/inventering_2026-11-03_1337.csv` | `reports/inventory_2026-11-03_1337.csv` | G8 |
| `meny.py` | `server_inventory/ui/menu.py` | G11–G14 |
| `lagring.py` | `server_inventory/storage/server_repository.py` and `report_exporter.py` | G5–G8 |
| `kontroller.py` | `server_inventory/services/server_checker.py` | G9, G10 |
| `python main.py --lista` | `python3 main.py --list` | G15 |
| `python main.py --lista --miljo prod` | `python3 main.py --list --env prod` | G15 |
| `python main.py --kontrollera web01` | `python3 main.py --check web01` | G15 |
| `python main.py --kontrollera-alla` | `python3 main.py --check-all` | G15 |
| `python main.py --export` | `python3 main.py --export` | G15 |
| `REDOGORELSE.md` | `PRESENTATION.md` (this file) | G20 |
| `REFLEKTION.md` | [`REFLECTION.md`](REFLECTION.md) | VG2–VG4 |

Beyond the requirements, the service rules live in their own module
(`services/inventory_service.py`) so the menu and the command line share them.

### Extras (VG1)

| Extra | Where | How to use |
|---|---|---|
| `--verbose` | `server_inventory/verbose.py`, used throughout the code | Add `-v` to any command, see [Verbose mode](README.md#verbose-mode) |

Also beyond the assignment: an exit code for every error scenario (see
[Exit codes](README.md#exit-codes)) and live progress when checking all servers in the
menu.
