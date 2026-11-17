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
