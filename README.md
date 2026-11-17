# Server Inventory Tool

A small command-line tool for keeping track of servers: what they are, which
environment they run in, and whether they respond on the network.

Many teams need a simple overview of their servers without setting up a full
monitoring system. Server Inventory Tool keeps the list in a JSON file, checks
the servers with `ping`, and exports reports as CSV. It can be used
interactively through a text menu, or from scripts and CI/CD pipelines where
the exit code tells you whether all servers are up.

**Features**

- Keep an inventory of servers with name, address, environment (`dev`, `test`,
  `prod`), role and status
- Add and remove servers, with an extra confirmation for production servers
- Check one or all servers with `ping`, and save the result and time of the check
- List all servers, or only the servers in one environment, as an aligned table
- Export the inventory as a timestamped CSV report
- Two ways to use it: an interactive text menu and command-line flags
- Exit codes for every outcome, so scripts and pipelines can react to the result
- `--verbose` mode that shows what the tool is doing, including the exact
  commands it runs

The tool is written in Python and uses only the standard library.

## Requirements

| Requirement | Version / note |
|---|---|
| Python | **3.10 or newer** (the code uses the `X \| None` type syntax from 3.10) |
| `ping` | Installed on most systems. Used to check if servers respond. |
| Third-party packages | None. Only the Python standard library is used. |
| Operating system | Linux. Windows through WSL. macOS with limitations, see below. |

## Installation

There is nothing to build or install with `pip`. You only need Python, `ping`
and a copy of the project.

### Linux

1. Check that Python 3.10 or newer and `ping` are installed:

   ```bash
   python3 --version
   ping -c 1 127.0.0.1
   ```

   If something is missing, install it with your package manager:

   ```bash
   # Debian / Ubuntu
   sudo apt install python3 iputils-ping

   # Fedora
   sudo dnf install python3 iputils
   ```

2. Get the project:

   ```bash
   git clone https://github.com/Feyrious/Server-Inventory-Tool.git
   cd Server-Inventory-Tool
   ```

### Windows (through WSL)

The server checks use the Linux version of `ping`, whose flags differ from
the Windows `ping`. Run the tool in WSL (Windows Subsystem for Linux):

1. Open PowerShell as administrator and install WSL with Ubuntu:

   ```powershell
   wsl --install
   ```

2. Restart if asked, open **Ubuntu** from the Start menu, and follow the
   [Linux](#linux) steps inside it.

### macOS

Python can be installed from [python.org](https://www.python.org/downloads/)
or with Homebrew (`brew install python`). `ping` is already installed. Then
get the project as in step 2 of the [Linux](#linux) steps.

> **Limitation:** on macOS, `ping -W` means milliseconds instead of seconds,
> so the 2-second timeout the tool uses becomes 2 ms. Listing, adding,
> removing and exporting work normally, but checks of remote servers will
> usually show `down`. For reliable checks, run the tool on Linux or in a
> Linux container.

## Quick start

From the project folder:

```bash
python3 main.py                  # start the text menu
python3 main.py --list           # print all servers and exit
python3 main.py --check-all      # check every server, exit code 0 if all are up
```

The project comes with example servers in `servers.json`, so every command
works right away.

## Configuration

### Choosing the data file: `INVENTORY_DATA_FILE`

The servers are stored in a JSON file. Which file is used is decided by the
environment variable `INVENTORY_DATA_FILE`:

| `INVENTORY_DATA_FILE` | File used |
|---|---|
| Not set (or empty) | `servers.json` in the project folder, wherever you run the command from |
| Set to a path | That path. A relative path is resolved from the folder you run the command in. |

Set it for a single run:

```bash
INVENTORY_DATA_FILE=test-servers.json python3 main.py --list
```

Or for the whole terminal session:

```bash
export INVENTORY_DATA_FILE=/srv/inventory/servers.json
python3 main.py --list
```

If the file doesn't exist, the tool starts with an empty list and creates the
file (and its folder) the first time something is saved.

Run with `--verbose` to see which data file is used.

### Using a `.env` file

`.env.example` lists every environment variable the tool reads, with its
default value. Copy it and change what you need:

```bash
cp .env.example .env
```

Python does not read `.env` files by itself, so load it into your shell
before running the tool:

```bash
set -a; source .env; set +a
python3 main.py
```

`.env` is ignored by git, so your local settings are never committed.

### Data file format

The data file contains a JSON list with one object per server:

```json
[
  {
    "name": "web01",
    "address": "example.com",
    "env": "prod",
    "role": "web-server",
    "status": "up",
    "last_checked": "2026-11-17 15:19"
  }
]
```

| Field | Meaning |
|---|---|
| `name` | Unique name of the server |
| `address` | Hostname or IP address that is pinged |
| `env` | Environment: `dev`, `test` or `prod` |
| `role` | Free text, e.g. `web-server` or `database` |
| `status` | `up`, `down` or `unknown` (new servers are always `unknown`) |
| `last_checked` | Time of the last check as `YYYY-MM-DD HH:MM`, or `""` if never checked |

The file is saved after every change, so it always matches what the tool
shows.

### Reports

CSV reports are written to the `reports/` folder in the project, which is
created automatically. Each file is named after the time it was created, for
example `reports/inventory_2026-11-17_1544.csv`. The first line is a header
row with the field names above.

See [`reports/report.example.csv`](reports/report.example.csv) for an example.
Generated reports are ignored by git.

## Using the text menu

Start the tool without any flags:

```bash
python3 main.py
```

```text
=== Server Inventory Tool ===
1. Show all servers
2. Show servers in an environment
3. Add a server
4. Remove a server
5. Check a server
6. Check all servers
7. Export report as CSV
0. Quit
Choose an option:
```

| Choice | What it does |
|---|---|
| `1` | Shows all servers as a table |
| `2` | Asks for an environment (`dev`, `test` or `prod`) and shows only those servers |
| `3` | Asks for name, address, environment and role, and adds the server with status `unknown`. Names must be unique. |
| `4` | Asks for a name and removes that server. Servers in `prod` need an extra confirmation: type `yes` to remove. |
| `5` | Asks for a name, pings that server and shows whether it is up or down |
| `6` | Pings every server, shows each result as soon as it is ready, then shows the updated table |
| `7` | Writes a CSV report to `reports/` and shows its path |
| `0` | Quits the program |

The menu keeps running until you choose `0`. If you enter something that
isn't a valid choice, an unknown server name or an invalid environment, the
tool tells you and asks again. Every change (adding, removing, checking) is
saved to the data file right away.

Example table:

```text
Name           Address         Env   Role           Status    Last checked
------------------------------------------------------------------------------
web01          example.com     prod  web-server     up        2026-11-17 15:19
db01           127.0.0.1       prod  database       up        2026-11-17 15:19
test01         192.0.2.10      test  test-server    down      2026-11-17 15:19
mail01         203.0.113.25    prod  mail-server    unknown   -
```

A `-` under *Last checked* means the server has never been checked.

## Using the command line

With a flag, the tool runs one action and exits. This is the mode to use in
scripts. Run `python3 main.py --help` to see all flags.

| Command | What it does |
|---|---|
| `python3 main.py` | Starts the text menu |
| `python3 main.py --list` | Prints all servers |
| `python3 main.py --list --env prod` | Prints only the servers in `prod` (also `dev`, `test`) |
| `python3 main.py --check web01` | Pings `web01`, saves the result and prints its row |
| `python3 main.py --check-all` | Pings every server, saves the results and prints the table |
| `python3 main.py --export` | Writes a CSV report to `reports/` and prints its path |
| `python3 main.py --help` | Shows the help text |

Every flag has a short form: `-l`, `-e`, `-c`, `-a`, `-x`, `-h`.

Rules:

- Only one action at a time: `--list`, `--check`, `--check-all` and
  `--export` can't be combined. Combining them is an error (exit code 2).
- `--env` only works together with `--list`.
- `--verbose` (`-v`) can be added to any command.

### Verbose mode

`--verbose` prints what the tool is doing: which data file it uses, which
servers it loads and saves, the exact `ping` command for each server and its
result, and the final exit code.

```bash
python3 main.py --check db01 --verbose
```

```text
[verbose] Verbose mode is on
[verbose] Data file: /home/user/Server-Inventory-Tool/servers.json (set INVENTORY_DATA_FILE to change it)
[verbose] Reports folder: /home/user/Server-Inventory-Tool/reports
[verbose] Loaded 14 servers from /home/user/Server-Inventory-Tool/servers.json
[verbose] Action: check server 'db01'
[verbose] Checking server 'db01' at 127.0.0.1
[verbose] Running command: ping -c 1 -W 2 127.0.0.1
[verbose] ping exited with code 0 for 127.0.0.1
[verbose] Saved 14 servers to /home/user/Server-Inventory-Tool/servers.json
Name           Address         Env   Role           Status    Last checked
------------------------------------------------------------------------------
db01           127.0.0.1       prod  database       up        2026-11-17 15:44
[verbose] Process finished with exit code 0 (OK)
```

Verbose messages are written to *stderr* and the normal output to *stdout*,
so you can save the output to a file and still see the verbose messages in
the terminal:

```bash
python3 main.py --list --verbose > servers.txt
```

## Using it in scripts and pipelines

In command-line mode the **exit code** is the result. A script or a CI/CD
pipeline doesn't need to read the text output; it only checks the exit code.
`0` means everything went well, and `1` means at least one checked server is
down or doesn't exist. All codes are listed under [Exit codes](#exit-codes).

See the exit code of the last command:

```bash
python3 main.py --check-all
echo $?
```

React to it in a bash script:

```bash
#!/usr/bin/env bash
cd /opt/Server-Inventory-Tool

python3 main.py --check-all > /dev/null
exit_code=$?

if [ "$exit_code" -eq 0 ]; then
    echo "All servers are up"
elif [ "$exit_code" -eq 1 ]; then
    echo "At least one server is down"
else
    echo "Server Inventory Tool failed with exit code $exit_code"
fi
```

Run a nightly check and report with cron (02:00 every night). `;` runs the
export even when the check finds a server that is down:

```bash
0 2 * * * cd /opt/Server-Inventory-Tool && python3 main.py --check-all; python3 main.py --export
```

In a CI/CD pipeline, a step fails when its command exits with anything other
than `0`. Example for GitHub Actions:

```yaml
- name: Check that all servers respond
  run: python3 main.py --check-all
```

## Exit codes

| Code | Name | When | What to do |
|---|---|---|---|
| `0` | `OK` | Everything went well | Nothing |
| `1` | `CHECK_FAILED` | `--check` or `--check-all` found a server that is down, or `--check` was given a name that doesn't exist | Look at the printed table, or the message, to see which server |
| `2` | `INVALID_ARGUMENTS` | Unknown or conflicting flags, e.g. `--list --check-all`, or `--env` without `--list` | Run `python3 main.py --help` |
| `3` | `DATA_FILE_INVALID` | The data file is not valid JSON, or doesn't contain a list of servers | Fix the file, see [Data file format](#data-file-format) |
| `4` | `DATA_FILE_UNREADABLE` | The data file exists but can't be read, e.g. no permission | Check the file's permissions |
| `5` | `DATA_FILE_NOT_SAVED` | The data file can't be written, e.g. a read-only folder | Check the permissions of the file and its folder |
| `6` | `REPORT_NOT_SAVED` | The CSV report can't be written to `reports/` | Check the permissions of the `reports/` folder |
| `7` | `PING_NOT_AVAILABLE` | The `ping` command is not installed | Install it, see [Installation](#installation) |
| `130` | `INTERRUPTED` | The program was stopped with Ctrl+C | Nothing; this is the standard code for Ctrl+C |

Error messages are always printed to *stderr*. With `--verbose`, the code and
its name are also printed when the program ends, for example
`Process finished with exit code 3 (DATA_FILE_INVALID)`.

In the text menu, problems such as an unknown server name are shown as a
message and the menu keeps running. Pressing Ctrl+D at a menu prompt quits
like choosing `0` (exit code `0`).
