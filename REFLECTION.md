# Reflection

> **Draft notes.** Bullet points collected during development, to be rewritten
> into prose at the end. VG2 asks for at least four choices, each covering:
> *what I chose, the alternatives, why, the consequences (pros and cons), and
> what I would do differently if the conditions changed.* At least two must
> come from the assignment's list (marked **[VG2 list]**). VG3 (scaling) has
> its own section at the bottom.

## Choices from the assignment's list

### List of dicts instead of a dict keyed by server name **[VG2 list]**
- Chose: `InventoryService.servers` is a `list[dict]`, loaded straight from the JSON array (G1).
- Alternative: `dict[str, dict]` with the server name as key.
- Pros: matches the JSON format 1:1, keeps insertion order, simple to loop over and filter (`filter_by_environment` is one list comprehension).
- Cons: `find_by_name()` loops through every server (O(n)). Duplicate names must be checked by hand in `add_server()`; with a dict they would be impossible by design.
- `remove_server()` and `check_server()` share `_get_existing_server()`, so the lookup cost is in one place and easy to swap later.
- Would change: with thousands of servers, or frequent lookups by name, keep a dict index by name (or move to a database).

### Saving after every change instead of only on exit **[VG2 list]**
- Chose: every change goes through `InventoryService`, which calls `_save()` right away (`add_server`, `remove_server`, `check_server`, `check_all_servers`) (G5).
- Alternative: keep changes in memory and save once when the program exits.
- Pros: nothing is lost if the program crashes or the user presses Ctrl+C; the file always matches what the user just saw.
- Cons: the whole file is rewritten on every change. Fine for a few servers, wasteful for many.
- `check_all_servers()` saves once after all checks, not once per server: a deliberate middle ground.
- Design lesson (PR #8): at first `save()` was public and callers had to remember to call it after a check. That made "always saved" a convention instead of a guarantee. Moving the check into `InventoryService` and making `_save()` private fixed it.

### How the program is split into packages, classes and functions **[VG2 list]**
- Chose: `server_inventory/` package with `storage/` (files), `services/` (rules and checks) and `ui/` (menu, display); `main.py` only parses arguments and wires things together.
- Started as flat modules with plain functions (as in the course), then switched to classes because of my C# background (PR #4).
- Classes for services (`ServerRepository`, `ReportExporter`, `InventoryService`, `ServerChecker`), but the servers themselves stay plain dicts because G1 requires it. A `Server` class (what I'd write in C#) would break G1.
- Plain functions where there is no state: `config.get_data_file_path()`, `is_valid_environment()`, `display.print_server_table()`. Classes only where they hold state or dependencies.
- Dependencies are passed in through constructors (`InventoryService(repository, checker)`), i.e. manual dependency injection. That made testing easy: a fake ping could be swapped in without real network access.
- Rule: only the menu and `main.py` may use `input()`, `print()` or `sys.exit()`. Services raise `ValueError` instead, so the menu and the CLI share all logic (G18).
- Consequence: easy to add a new interface (e.g. a web API) on top of the same services; more files and indirection than a small script strictly needs.

### Data file from an environment variable instead of a hard-coded name **[VG2 list]**
- Chose: `config.get_data_file_path()` reads `INVENTORY_DATA_FILE`, default `servers.json` (G6).
- Pros: the same code can use test data, a different file per environment, or a file set by a pipeline, without code changes.
- An empty variable (`INVENTORY_DATA_FILE=`) falls back to the default instead of trying to open `""`.
- The default is anchored to the project folder with `Path(__file__)`, so the tool works when started from another folder. The env var path is used as given (relative to where the command runs), which is what CLI users expect.
- Would change: if there were more settings, add a config file with the order *env var > config file > default* (the "Konfigurationsfil" VG extra).

### Using `subprocess` and the system `ping` instead of a Python implementation **[VG2 list]**
- Chose: `ServerChecker._ping()` runs `ping -c 1 -W 2 <address>` and only looks at the exit code (G9).
- Alternative: write ICMP in Python with raw sockets, or use a library.
- Pros: `ping` is already installed, well tested, and has the network permissions it needs. Raw sockets in Python need root.
- Discovered in practice: my development sandbox could not run ping at all ("Operation not permitted"), while my own terminal could. Checks depend on the environment the tool runs in.
- Cons: the flags are Linux-specific (`-W` means milliseconds on macOS, and Windows uses different flags). Some networks block ping, so "down" can mean "blocked" rather than "offline".
- `-W 2` timeout: without it, unreachable addresses like `192.0.2.10` hang for a long time.

### Sending the command to `subprocess.run()` as a list **[VG2 list]**
- Chose: `_build_ping_command()` returns `["ping", "-c", "1", "-W", "2", address]`.
- Alternative: one string with `shell=True`.
- Why: with a list no shell is involved, so an address like `example.com; rm -rf ~` is just an invalid hostname, not a second command (command injection, same class of bug as SQL injection).

### Offering both a text menu and a CLI **[VG2 list]**
- CLI for scripts and pipelines: the exit code is the result (G16). The menu is for people.
- Both use the same services, so behaviour can't drift between them.
- argparse mutually exclusive group: conflicting flags (`-l -a`) give an error and exit code 2 instead of being silently ignored by an `if/elif` chain. The library enforces the rule instead of my own code.
- `--list-env` is a separate flag instead of the spec's `--list --env prod`: a deliberate deviation, clearer to use, documented in the README.
- C# habit that went wrong: `type=bool` in argparse. `bool("False")` is `True`; flags should use `action="store_true"`.
- `process_data()` in `main.py` returns `True`/`False` and only `main()` calls `status_ok()` / `status_failed()`. The logic reports a result; one place decides how the process ends (G16).
- `VALID_ENVIRONMENTS` is now the single source for the CLI `choices`, the menu prompt and the service rule, so the three can't disagree.
- The CLI `--check-all` prints only the final table, while the menu shows each server live. Same service method, the caller decides how much to show.

## Other choices

### English names instead of the spec's Swedish names
- Approved by the teacher. Keys, flags, file names and code are in English because that's the industry standard and the repo is also a portfolio project.
- Cost: a mapping table in the README so the teacher can match each requirement.

### Errors as exceptions (`ValueError`) instead of return values
- `add_server()` can fail for two reasons (duplicate name, invalid environment); the exception message says which.
- Callers decide how to show it: the menu prints the message, the CLI turns it into exit code 1.
- Alternative: return `True`/`False` or `None`, which loses the reason.

### `exists()` (look before you leap) vs `try/except FileNotFoundError` (easier to ask forgiveness)
- `ServerRepository.load()` uses `exists()` because G7 asks for it.
- The more Pythonic alternative is `try/except`; it also avoids a race where the file disappears between the check and the open.
- Broken JSON (`json.JSONDecodeError`) is caught in `main.create_services()` and exits with code 1 through `exit_status.error_read_file()`. The repository itself doesn't decide how to report it.

### `check_all()` uses a loop, not `all(...)`
- `all()` stops at the first `False`, so servers after the first down server would never be checked and keep stale status.
- Small example of a "clever" one-liner being wrong; a comment in the code explains why.

### Removing `new_line()` / `os.linesep` (PR #10)
- C# habit: `Environment.NewLine`. In Python, text mode already translates `"\n"` to the OS line ending.
- Writing `os.linesep` (`"\r\n"` on Windows) in text mode gives `"\r\r\n"`. The bug would only show on Windows, never on my Linux machine.
- Same reason `ReportExporter` passes `newline=""` when writing CSV.

### Privacy by convention and `# region` blocks
- Python can't enforce `private`; a leading `_` is the convention (`_save`, `_ping`, `_build_report_filename`, `_print_system_info`).
- Rule I followed: public only if code outside the class needs it; move it later if that changes (PR #7, PR #9).
- `# region` / `# endregion` comments (folded by PyCharm) group public and private members, like `#region` in C#.

### Storage details
- `json.dump(..., indent=2)` plus a final newline: `servers.json` is committed to git (the spec lists it), so status changes show as small, readable diffs.
- Con: every check changes a tracked file, so `git status` is "dirty" after using the tool.
- Report filename `inventory_YYYY-MM-DD_HHMM.csv`: no `:` because it is invalid on Windows. Two exports in the same minute overwrite each other.
- `csv.DictWriter(extrasaction="ignore")`: extra keys (e.g. a future history list) don't break the export.
- `reports/report.example.csv` is committed as an example. `.gitignore` uses `reports/*` plus `!reports/report.example.csv`; a plain `reports/` can't have exceptions because git skips ignored folders entirely.
- Example data in `servers.json` uses loopback addresses (always up) and the reserved documentation ranges 192.0.2.x, 198.51.100.x and 203.0.113.x (always down), so a real check gives predictable results. `web02` (197.0.0.5) is a real public address and could change.

### Global state: `config.IS_VERBOSE`
- A module-level variable set once from `main.py` and read by `exit_status`. Simple, but it is hidden global state.
- Alternative: pass `verbose` as a parameter or into constructors. More explicit, more plumbing.
- Consequence: `exit_status` only prints when verbose is on, so without `-v` a broken data file exits with code 1 but shows nothing. Fine for pipelines (they read the exit code), confusing for a person. Would change: always print errors to stderr, and use verbose only for extra detail.

### Process: git flow and one PR per feature
- `main` / `develop` / `feature/*` branches, every change merged through a PR with a description and test table.
- One file per commit, so the history shows the project being built step by step.
- Merging `develop` straight into `main` early on was a mistake; fixed by switching to PRs.

### Testing approach
- Manual tests on a copy of `servers.json`, never on the real file. Fakes for `ping` (`true`/`false` commands) to test the logic without the network.
- No automated tests yet. With more time: `pytest` with temporary files (`tmp_path`) and a fake checker.

### Text UI (`ui/menu.py`, `ui/display.py`)
- Menu choices live in one dict: choice -> (text, handler method). Adding a choice is one line, and the printed menu and the handling can't drift apart. Alternative: a long `if/elif` chain (what `main.py` uses for the CLI, where argparse already limits the options).
- Table columns are defined once in `display._COLUMNS` (key, title, width), so header and rows always line up (G14).
- Fixed column widths vs auto-sizing: a 19-character role (`integration-testing`) overflowed its column during testing. I widened name/role to 15 and shortened the role to `inter-testing`. Auto-sizing each column to its longest value would never overflow but is more code; fixed widths match the assignment's `:<15` hint.
- Progress while checking all servers: the menu was silent until every check finished (up to 2 s per unreachable server). Options: (A) loop in the menu (duplicates logic, saves once per server), (B) an optional callback `on_server_checked(server, is_up)` passed through `InventoryService` to `ServerChecker`, (C) a generator that yields results (saving becomes awkward if the caller stops early). Chose B: services still never print, the loop and the single save stay in one place. Like passing an `Action<T1, T2>` in C#.
- `main.create_services()` is the composition root: the only place where objects are created and connected (manual dependency injection, like a DI container in `Program.cs`).
- `Checking nope...` prints before "No server named 'nope' exists." because `check_server()` does lookup and check in one call. Small UX cost of keeping the menu free of rules.
- Not handled yet (the "Säkrare inmatning" VG extra): empty names/addresses are accepted, names with spaces are allowed, and Ctrl+C at a prompt ends the program with a traceback (`KeyboardInterrupt`).

## VG3: a larger environment (1 000 servers, nightly pipeline)
- **Check time:** checks run one at a time with a 2 s timeout. 1 000 servers, many down → up to ~33 minutes. Fix: run checks in parallel (`concurrent.futures.ThreadPoolExecutor`) or with `asyncio`.
- **Lookups:** `find_by_name()` is O(n); a dict index by name would make lookups instant.
- **Storage:** rewriting a whole JSON file on every change does not scale and is unsafe if two runs write at once. Move to SQLite or a real database, or at least use file locking.
- **Saving:** `check_all_servers()` already saves once per run instead of once per server. Keep that.
- **Pipeline:** exit codes already work (G16). Add machine-readable output (JSON) and logging (`logging` module) instead of `print`.
- **Reliability:** ping is often blocked; add TCP or HTTP checks (the HTTP VG extra), and retries.
- **Reports:** add seconds to the filename, or a run id, to avoid overwrites; clean up old reports.
- **Config:** a config file and env vars for timeouts and paths instead of constants in code.
