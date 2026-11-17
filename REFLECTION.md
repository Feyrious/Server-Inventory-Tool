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
- `.env.example` lists every variable the tool reads, with its default. Python doesn't load `.env` files by itself (that needs a library like `python-dotenv`); I kept to the standard library and documented `set -a; source .env` instead. The real `.env` is in `.gitignore`, so local settings (and any future secrets) never reach git.
- Writing the example showed a subtle difference: the code's default is anchored to the project folder, but `INVENTORY_DATA_FILE=servers.json` is relative to where you run the command. Same value, different meaning; documented in the file.

### Using `subprocess` and the system `ping` instead of a Python implementation **[VG2 list]**
- Chose: `ServerChecker._ping()` runs `ping -c 1 -W 2 <address>` and only looks at the exit code (G9).
- Alternative: write ICMP in Python with raw sockets, or use a library.
- Pros: `ping` is already installed, well tested, and has the network permissions it needs. Raw sockets in Python need root.
- Discovered in practice: my development sandbox could not run ping at all ("Operation not permitted"), while my own terminal could. Checks depend on the environment the tool runs in.
- Cons: the flags are Linux-specific (`-W` means milliseconds on macOS, and Windows uses different flags). Some networks block ping, so "down" can mean "blocked" rather than "offline".
- `-W 2` timeout: without it, unreachable addresses like `192.0.2.10` hang for a long time.
- Relying on an external command means it may not exist: slim Docker images don't include `ping`. Found in the code review; `_ping()` now catches `FileNotFoundError` and raises `PingNotAvailableError` (exit code 7) instead of crashing with a traceback.
- Writing the README's installation section made the portability problem concrete: on macOS the 2 s timeout becomes 2 ms, and on Windows `ping -c` doesn't exist, so every check shows `down`. I documented Linux as supported, Windows through WSL (as the assignment suggests) and macOS with a limitation. Would change: choose the flags with `platform.system()` (`-c`/`-W` on Linux, `-c`/`-t` on macOS, `-n`/`-w` on Windows) in `_build_ping_command()`.

### Sending the command to `subprocess.run()` as a list **[VG2 list]**
- Chose: `_build_ping_command()` returns `["ping", "-c", "1", "-W", "2", address]`.
- Alternative: one string with `shell=True`.
- Why: with a list no shell is involved, so an address like `example.com; rm -rf ~` is just an invalid hostname, not a second command (command injection, same class of bug as SQL injection).

### Offering both a text menu and a CLI **[VG2 list]**
- CLI for scripts and pipelines: the exit code is the result (G16). The menu is for people.
- Both use the same services, so behaviour can't drift between them.
- argparse mutually exclusive group: conflicting flags (`-l -a`) give an error and exit code 2 instead of being silently ignored by an `if/elif` chain. The library enforces the rule instead of my own code.
- First version: `--list-all` and `--list-env prod` as two separate actions. The review against G15 showed the spec's `--lista --miljo prod` then had no 1-to-1 translation (`--list-all --list-env prod` was rejected by the exclusive group). Changed to `-l/--list` plus an optional `-e/--env` filter outside the group, like `--verbose`. Lesson: English names were approved, different behaviour was not.
- C# habit that went wrong: `type=bool` in argparse. `bool("False")` is `True`; flags should use `action="store_true"`.
- `process_data()` in `main.py` returns `True`/`False` and only `main()` calls `exit_program()`. The logic reports a result; one place decides how the process ends (G16).
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

### Exit codes: one per error scenario (`exit_status.ExitCode`, `errors.py`)
- `ExitCode` is an `IntEnum`: named constants that are real integers, so `sys.exit(ExitCode.DATA_FILE_INVALID)` works and the code reads like documentation.
- G16 fixes code 1 for both "server down" and "server not found", so they share `CHECK_FAILED`; every other scenario got its own code (2–7). 2 matches argparse's own code for bad arguments, and 130 (128 + SIGINT) is the Unix convention for Ctrl+C, so pipelines recognise them.
- Each exception class carries its own exit code as a class attribute and inherits from `InventoryError`, so `main.py` handles all of them in one `except InventoryError` block. Adding a new error = one new class, no change in `main.py`.
- Alternative: catch each exception type in `main.py` and map it to a code there. Keeps exit codes out of `errors.py`, but the mapping grows with every new error.
- Storage classes translate low-level errors (`OSError`, `JSONDecodeError`) into these types with `raise ... from error`, which keeps the original error attached (like `InnerException` in C#).
- Con: `errors.py` now depends on `exit_status`, so the error types know about the CLI. Acceptable for a small tool; a library would keep them separate.

### `exists()` (look before you leap) vs `try/except FileNotFoundError` (easier to ask forgiveness)
- `ServerRepository.load()` uses `exists()` because G7 asks for it.
- The more Pythonic alternative is `try/except`; it also avoids a race where the file disappears between the check and the open.
- Broken JSON, a JSON object instead of a list, and unreadable files are turned into `DataFileInvalidError` / `DataFileUnreadableError` inside `ServerRepository.load()`, and end the program with exit code 3 or 4. A data file in a folder that doesn't exist is created on the first save (found in review; used to crash).

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
- First version: `exit_status` only printed when verbose was on, so without `-v` a broken data file exited silently. Changed: error messages always print to stderr; verbose is only for extra detail.
- Verbose messages go through one helper, `verbose.log_verbose()`, so the "only if verbose" check is written once (G18) instead of `if config.IS_VERBOSE: print(...)` everywhere.
- They are debug/status messages, so they appear in services and storage too, not only in the UI. Accepted as a deliberate exception to "services never print", the same way a logger would be used.
- stdout vs stderr: normal output (the table) goes to stdout and `[verbose]` lines to stderr, so `main.py -l -v > servers.txt` gives a clean file while debug lines still show in the terminal.
- Would change in a bigger tool: use Python's `logging` module with levels (DEBUG/INFO/ERROR) instead of a home-made helper.

### Process: git flow and one PR per feature
- `main` / `develop` / `feature/*` branches, every change merged through a PR with a description and test table.
- One file per commit, so the history shows the project being built step by step.
- Merging `develop` straight into `main` early on was a mistake; fixed by switching to PRs.
- The README is written as a user guide (install, menu, CLI, pipelines, exit codes) rather than as course documentation, with the assignment-specific parts (Swedish → English name table, VG extras) in a separate section at the end. One document serves both a user and the teacher.
- Every command in the README was run before merging, so the documented exit codes and verbose output match the real program.

### Testing approach
- Manual tests on a copy of `servers.json`, never on the real file. Fakes for `ping` (`true`/`false` commands) to test the logic without the network.
- No automated tests yet. With more time: `pytest` with temporary files (`tmp_path`) and a fake checker.
- The reviews that found real problems were the ones that tested *outside* the happy path: `ping` missing (PATH without ping), a data file in a folder that doesn't exist, read-only files, Ctrl+C sent as a signal. A first Ctrl+C test was misleading (a background job in a non-interactive shell ignores SIGINT), which is a reminder to check that a test really tests what it claims.

### Text UI (`ui/menu.py`, `ui/display.py`)
- Menu choices live in one dict: choice -> (text, handler method). Adding a choice is one line, and the printed menu and the handling can't drift apart. Alternative: a long `if/elif` chain (what `main.py` uses for the CLI, where argparse already limits the options).
- Table columns are defined once in `display._COLUMNS` (key, title, width), so header and rows always line up (G14).
- Fixed column widths vs auto-sizing: a 19-character role (`integration-testing`) overflowed its column during testing. I widened name/role to 15 and shortened the role to `inter-testing`. Auto-sizing each column to its longest value would never overflow but is more code; fixed widths match the assignment's `:<15` hint.
- Progress while checking all servers: the menu was silent until every check finished (up to 2 s per unreachable server). Options: (A) loop in the menu (duplicates logic, saves once per server), (B) an optional callback `on_server_checked(server, is_up)` passed through `InventoryService` to `ServerChecker`, (C) a generator that yields results (saving becomes awkward if the caller stops early). Chose B: services still never print, the loop and the single save stay in one place. Like passing an `Action<T1, T2>` in C#.
- `main.create_services()` is the composition root: the only place where objects are created and connected (manual dependency injection, like a DI container in `Program.cs`).
- `Checking nope...` prints before "No server named 'nope' exists." because `check_server()` does lookup and check in one call. Small UX cost of keeping the menu free of rules.
- Not handled yet (the "Säkrare inmatning" VG extra): empty names/addresses are accepted, and names with spaces are allowed. (Ctrl+C and Ctrl+D at a prompt are handled since the exit code work: exit code 130 and a clean quit.)

### Python 3.10 as the minimum version
- The code uses the `X | None` syntax in type hints (`find_by_name() -> dict | None`, `process_data(env: str | None, ...)`). Those hints are evaluated when the function is defined, so the program won't even start on Python 3.9 or older.
- Alternatives: `Optional[dict]` from `typing`, or `from __future__ import annotations` at the top of each file. Both work on older versions.
- Chose the modern syntax because it reads like C#'s `string?`, and Python 3.10 has been out since 2021. Documented as a requirement in the README.
- Would change: if the tool had to run on an older server (e.g. an old LTS distribution), use `Optional[...]` or the `__future__` import.

### Using an AI assistant as a pair programmer
- Chose: Claude Code as a pair programmer, with me in the tech lead / reviewer role (details in `PRESENTATION.md`). Reason: I already program professionally in C#, so the learning goal is Python as a language, not programming itself.
- Alternatives: write everything myself and only look things up; or use AI as a search engine for single questions.
- Pros: faster progress under a tight deadline; constant explanations with C# comparisons were a direct way to learn Python idioms; requirement-by-requirement reviews caught real problems (the `--lista --miljo` mapping, crash cases).
- Cons / risks: it's easy to accept code without understanding it. Mitigations I used: one file or one logical change per commit, an explanation of every piece of code, my own review before every merge, and questioning design choices (e.g. why `save()` was public, which led to a better design).
- Sometimes the AI was wrong or too fast: it once claimed a test had been run in a terminal when it hadn't (corrected in the PR), and early on it changed several files at once, which made it hard to follow. Setting rules (one file at a time, public before private) fixed that.
- Would change: as a beginner in programming, I would write more of the code myself first and use AI mainly for review.

### Linking to code lines in `PRESENTATION.md`
- Chose: relative links with line anchors (`server_checker.py#L41`), so each answer points straight at the code, as G20 asks.
- Alternatives: link only to the file and name the function (never breaks); or GitHub permalinks pinned to a commit (never drift, but show old code after a fix).
- Trade-off: relative line anchors drift when lines are added above them, so they have to be checked again after every code change. That's why they were added last, when the code was done.

## VG3: a larger environment (1 000 servers, nightly pipeline)
- **Check time:** checks run one at a time with a 2 s timeout. 1 000 servers, many down → up to ~33 minutes. Fix: run checks in parallel (`concurrent.futures.ThreadPoolExecutor`) or with `asyncio`.
- **Lookups:** `find_by_name()` is O(n); a dict index by name would make lookups instant.
- **Storage:** rewriting a whole JSON file on every change does not scale and is unsafe if two runs write at once. Move to SQLite or a real database, or at least use file locking.
- **Saving:** `check_all_servers()` already saves once per run instead of once per server. Keep that.
- **Pipeline:** exit codes already work (G16). Add machine-readable output (JSON) and logging (`logging` module) instead of `print`.
- **Reliability:** ping is often blocked; add TCP or HTTP checks (the HTTP VG extra), and retries.
- **Reports:** add seconds to the filename, or a run id, to avoid overwrites; clean up old reports.
- **Config:** a config file and env vars for timeouts and paths instead of constants in code.
- **Runner environment:** CI images are often minimal: they may lack `ping` (now exit code 7 instead of a crash) or have an old Python (needs 3.10+). A container image with both pinned would make nightly runs predictable.
- **Data file in git:** `servers.json` is committed, and every check changes it. A nightly job would either produce a commit every night or leave the repo dirty. Better: keep the live data file outside the repo (`INVENTORY_DATA_FILE=/srv/inventory/servers.json`) and only keep example data in git.
