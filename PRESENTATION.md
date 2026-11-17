# Presentation (Redogörelse)

> **Draft notes.** The headings are the seven questions from G20. The bullet
> points under each one are facts and code references to write the answers
> from, in my own words. G20 asks for a few sentences per question that
> explain *how* and *why*, and every answer must point to concrete places in
> the code (file and function).

## How AI was used in this project

> *Draft. Rewrite in my own words.*

- Background: I have about 5–6 years of experience as a .NET (C#) developer.
  For me this course is about learning **Python as a language** (its idioms,
  standard library and conventions), not about learning to program. That is
  why I chose to use an AI coding assistant (Claude Code), and in what role.
- Allowed by the course as long as I understand the code and can explain and
  defend every part of it.
- The work was split like roles in a development team:
  - **Me: tech lead / architect and reviewer.**
    - Architectural decisions: packages and classes (`storage/`, `services/`,
      `ui/`) instead of flat modules, servers kept as dicts because of G1,
      English naming throughout, git flow with one PR per feature.
    - Design decisions in review, for example: making helper methods private
      when nothing outside the class needs them (`ServerChecker._ping`),
      questioning why `save()` was public, which led to `InventoryService`
      owning the checks (PR #8), choosing the callback design for live
      progress (option B of three), the `--list --env` flag shape, exit codes
      for every error scenario, and verbose messages as debug logging.
    - Coding conventions: public methods before private ones, `# region`
      blocks, one file / one logical change per commit.
    - Reviewed every change and every PR before merging, and tested in my own
      terminal (for example the real `ping` checks).
    - Wrote the first version of the CLI myself (`main.py` argparse setup,
      commit `a463498`) and fixed it after the AI's review (`type=bool`,
      mutually exclusive flags).
    - *Check and fill in:* how much of `envconfig.py` / `statuscode.py`
      (commit `8155fa4`, later `config.py` / `exit_status.py`) I wrote myself.
  - **AI: pair programmer / implementer.**
    - Proposed a structure and step-by-step plan from the assignment.
    - Wrote most of the implementation code under my direction, especially
      at the end when time was short, one file or logical change at a time.
    - Explained every piece of code it wrote (what, why and how it works,
      with comparisons to C#), so I could review and defend it.
    - Did code reviews against the assignment's requirements (G1–G18) and
      pointed out risks, such as the `--lista --miljo` mapping and crashes
      when `ping` is missing.
    - Tested changes on copies of the data and wrote PR descriptions.
    - Collected bullet points for this file and `REFLECTION.md`. The final
      text is written by me.
- What I learned from working this way: see the C# vs Python points in
  `REFLECTION.md` (`type=bool`, `os.linesep`, `all()`, privacy by convention).

## 1. Three constructs in the code and how their syntax works

Pick three different kinds. Candidates:

- **Condition (`if` / `elif` / `else`)**
  - `ui/menu.py` → `Menu._remove_server()`: `if server is None: ... return`,
    then `if server["env"] == _PROD_ENVIRONMENT and not self._confirm(...)`.
    Shows `is None`, `and` with short-circuit (the question is only asked for
    prod servers), and early `return` (guard clauses).
  - `main.py` → `process_data()`: `if / elif / else` chain that routes each
    flag to an action; `else` starts the menu.
  - `config.py` → `get_data_file_path()`: `if data_file_from_env:` — an empty
    string is falsy, so it falls back to the default.
- **Loop**
  - `services/inventory_service.py` → `InventoryService.find_by_name()`:
    `for server in self.servers:` with `return` inside the loop, `None` after.
  - `ui/menu.py` → `Menu.run()`: `while True:` with `continue` (invalid
    choice) and `return` (quit) — G11/G12.
  - `services/server_checker.py` → `ServerChecker.check_all()`: `for` loop
    chosen over `all(...)` because `all()` stops at the first `False`.
- **Function with parameters and `return`**
  - `services/inventory_service.py` → `is_valid_environment(env: str) -> bool`:
    one parameter, returns the result of `env in VALID_ENVIRONMENTS`.
  - `services/server_checker.py` → `ServerChecker.check_server(server: dict) -> bool`:
    changes the dict in place *and* returns whether the server is up.
  - Type hints (`-> bool`, `str | None`) are documentation, not enforced.
- Other options if wanted: list comprehension in
  `InventoryService.filter_by_environment()`, `try / except ValueError` in
  `Menu._add_server()`, f-string format spec `:<{width}` in
  `ui/display.py → _format_header()`.

## 2. Why a list of dictionaries, and which data types a server has

- All servers: a `list` in `InventoryService.servers`, loaded by
  `ServerRepository.load()` (G1).
- One server: a `dict` with six keys. Value types:
  - `name`, `address`, `env`, `role`: `str`
  - `status`: `str`, one of `VALID_STATUSES` (`up`, `down`, `unknown`)
  - `last_checked`: `str` formatted `YYYY-MM-DD HH:MM`, or `""` if never
    checked — a string, not a `datetime`, because JSON has no date type.
- Why a list of dicts fits:
  - Matches JSON 1:1 (array of objects), so `json.load` / `json.dump` need no
    conversion.
  - Easy to loop over, filter (list comprehension) and keep in order.
  - Dicts are flexible: `csv.DictWriter` writes them directly
    (`ReportExporter.export_csv()`).
- Trade-offs (more in `REFLECTION.md`): lookup by name is a loop (O(n)), and
  unique names have to be checked by hand in `add_server()`.
- Coming from C#: I'd normally write a `Server` class, but G1 requires dicts.

## 3. Why JSON for the data but CSV for the report

- JSON (`storage/server_repository.py`):
  - The program reads it back every time it starts → needs a format that
    keeps the structure (list of objects with named fields) exactly.
  - Round-trip: `json.load` gives back the same list of dicts that
    `json.dump` wrote.
  - Human-readable with `indent=2`, and gives small diffs in git.
- CSV (`storage/report_exporter.py`):
  - The report is for people: opens directly in Excel / LibreOffice / Google
    Sheets as a table.
  - Flat format (one row per server, one column per field) fits a report.
  - One-way: the program never reads reports back, so losing structure is fine.
- Summary: JSON = storage for the program, CSV = output for humans.

## 4. How the program is split into modules and functions

- `main.py` — entry point: argparse, `create_services()` builds and connects
  the objects, `process_data()` routes to an action, `exit_program()` sets the
  exit code (G15–G17).
- `server_inventory/storage/` — files: `ServerRepository` (JSON) and
  `ReportExporter` (CSV).
- `server_inventory/services/` — rules: `InventoryService` (find, filter, add,
  remove, check, save after every change) and `ServerChecker` (ping).
- `server_inventory/ui/` — the user: `Menu` and `print_server_table()`.
- Support modules: `config.py` (settings), `errors.py` (exceptions with exit
  codes), `exit_status.py` (exit codes), `verbose.py` (debug messages).
- Main rule: services never ask the user anything and don't decide the exit
  code, so the menu and the CLI share the same logic (G18).
- Classes where there is state or dependencies, plain functions where there
  isn't (`is_valid_environment()`, `print_server_table()`).
- Dependencies passed through constructors (`InventoryService(repository, checker)`).
- See the folder tree in `README.md` → *Project structure*.

## 5. Standard library modules and what they are used for

| Module | Where | Used for |
|---|---|---|
| `json` | `storage/server_repository.py` | Read and write the data file |
| `csv` | `storage/report_exporter.py` | Write the report with `DictWriter` (header row) |
| `pathlib` (`Path`) | `config.py`, `server_repository.py`, `report_exporter.py` | Paths, `exists()` (G7), `mkdir(parents=True, exist_ok=True)` (G8), joining with `/` |
| `os` | `config.py` | `os.environ.get()` reads `INVENTORY_DATA_FILE` (G6) |
| `datetime` | `server_checker.py`, `report_exporter.py` | Timestamp for `last_checked` (G10) and the report filename (G8) |
| `subprocess` | `server_checker.py` | `subprocess.run()` runs `ping` with the command as a list (G9) |
| `argparse` | `main.py` | Flags, `--help`, mutually exclusive actions, `choices` (G15) |
| `sys` | `exit_status.py`, `verbose.py` | `sys.exit()` for exit codes (G16), `sys.stderr` for errors and verbose output |
| `enum` (`IntEnum`) | `exit_status.py` | Named exit codes that are real integers |
| `typing` (`NoReturn`), `collections.abc` (`Callable`) | `exit_status.py`, `server_checker.py` | Type hints only |

## 6. Three examples of good practice and why they are good

Pick three. Candidates:

- **Logic written once (G18)** — `InventoryService` is used by both the menu
  and the CLI; `VALID_ENVIRONMENTS` feeds the service rule, the menu prompt
  and argparse `choices`; table column widths live in one list
  (`display._COLUMNS`).
- **Command as a list to `subprocess.run()`** — `ServerChecker._build_ping_command()`:
  no shell, so an address can't inject a second command.
- **Errors as exceptions with exit codes** — `errors.py` + `exit_status.ExitCode`:
  one `except InventoryError` in `main.py`, a clear message instead of a
  traceback, and a distinct exit code for scripts.
- **No secrets, environment-based config** — `INVENTORY_DATA_FILE`,
  `.env.example` committed, `.env` and `reports/*` in `.gitignore`.
- **Saving after every change** — `InventoryService._save()` is private and
  called by every method that changes the list, so saving can't be forgotten.
- **Descriptive names, docstrings and type hints** — e.g.
  `check_all_servers(on_server_checked=...) -> bool`.
- **Version control** — git flow, one PR per feature with a description and
  test table, small commits.

## 7. Sources and tools used, and for what

- **Course material**: the *Service Status Tool* course project and book —
  general structure (menu, argparse, JSON, subprocess).
- **Python documentation** (docs.python.org): `argparse` (mutually exclusive
  groups, `choices`), `subprocess.run`, `pathlib`, `csv.DictWriter`, `json`,
  `enum.IntEnum`.
- **`ASSIGNMENT.md`** — the requirements, used as a checklist in reviews.
- **Claude Code (AI assistant)** — see *How AI was used in this project* above.
- **PyCharm** — editor (`# region` folding, inspections).
- **Git and GitHub** — version control, pull requests, code review.
- Add anything else I used (forums, Stack Overflow, classmates, the teacher).
