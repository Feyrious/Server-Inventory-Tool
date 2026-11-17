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
