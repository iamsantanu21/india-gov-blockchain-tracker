# India Government Blockchain Tracker

An open, project-level database and dashboard of blockchain initiatives by Indian public bodies (Union, all 28 States and 8 Union Territories, regulators, courts and statutory bodies), 2017–2026.

**Dashboard:** https://iamsantanu21.github.io/india-gov-blockchain-tracker/  ·  **Dataset version:** 1.1.0  ·  **Licence:** CC BY 4.0

## What is in this repository

| Path | Content |
|---|---|
| `index.html` | The dashboard: map, project register, lifecycle timelines, challenges, NIC platform usage, evidence and coverage. It reads the CSV files below, so it updates whenever they change. |
| `data/*.csv` | The dataset as normalised tables (projects, stage events, challenges, sources, NIC snapshots, jurisdictions, bodies, vocabularies and supporting tables) |
| `datapackage.json` | Schemas, keys and controlled vocabularies (Frictionless Data Package) |
| `tools/` | `build.py` validates and rebuilds; `nic_snapshot.py` adds a NIC platform snapshot; `make_workbook.py` builds the Excel edition |
| `derived/` | Flat project table, summary numbers and an SQLite database (rebuilt by `tools/build.py`) |
| `India_Govt_Blockchain_Database_v1.1.xlsx` | Excel edition with summary formulas and a blind coding sheet |
| `METHODS.md`, `UPDATE_GUIDE.md`, `README_DATASET.md` | Method, update steps and the full dataset description |

Every push runs `tools/build.py` on GitHub Actions, so a wrong code, broken link between tables or impossible date is caught before it reaches the dashboard.

## Updating

Edit the CSV files (see `UPDATE_GUIDE.md`), run `python3 tools/build.py`, then commit and push. GitHub Pages republishes the dashboard within a minute or two.

## How to cite

Mondal, S. (2026). *Blockchain in Indian Government Administration: A Project-Level Dataset (2017–2026)* (Version 1.1.0) [Data set]. DOI to be added after deposit.

Map boundaries: DataMeet India community (CC BY 4.0). Prepared with AI assistance (Claude, Anthropic) and reviewed by the author.
