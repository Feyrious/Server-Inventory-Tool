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
