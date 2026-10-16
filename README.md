# India Government Blockchain Tracker

An open, project-level database and dashboard of blockchain initiatives by Indian public bodies (Union, all 28 States and 8 Union Territories, regulators, courts and statutory bodies), 2017–2026.

**Dashboard:** https://iamsantanu21.github.io/india-gov-blockchain-tracker/  ·  **Dataset version:** 1.1.0  ·  **DOI:** [10.5281/zenodo.23136332](https://doi.org/10.5281/zenodo.23136332) (all versions)  ·  **Licence:** CC BY 4.0

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23136332.svg)](https://doi.org/10.5281/zenodo.23136332)

## What is in this repository

| Path | Content |
|---|---|
| `index.html` | The dashboard: map, project register, lifecycle timelines, challenges, NIC platform usage, evidence and coverage. It reads the CSV files below, so it updates whenever they change. |
| `data/all_projects.csv` | **The combined table: every project in one row** with level of government, type of body, region, who built it, stage dates, NIC usage, challenges and evidence (57 columns). The dashboard reads this file. Built automatically – do not edit by hand. |
| `data/*.csv` (others) | The source tables (projects, bodies, jurisdictions, stage events, challenges, sources, NIC snapshots, vocabularies and supporting tables) |
| `datapackage.json` | Schemas, keys and controlled vocabularies (Frictionless Data Package) |
| `tools/` | `build.py` validates and rebuilds; `nic_snapshot.py` adds a NIC platform snapshot; `make_workbook.py` builds the Excel edition; `make_release.py` builds the release zip in `dataset/` |
| `derived/` | Summary numbers and an SQLite database (rebuilt by `tools/build.py`) |
| `India_Govt_Blockchain_Database_v1.1.xlsx` | Excel edition with summary formulas and a blind coding sheet |
| `dataset/` | **The dataset release archive** (`India_Govt_Blockchain_Dataset_v1.1.0.zip`), the same package that is deposited on Zenodo, with the list of versions and DOIs |
| `METHODS.md`, `UPDATE_GUIDE.md`, `README_DATASET.md`, `ZENODO_UPLOAD_GUIDE.md` | Method, update steps, the full dataset description and how to add a Zenodo version |

Every push runs `tools/build.py` on GitHub Actions, so a wrong code, broken link between tables or impossible date is caught before it reaches the dashboard.

## Updating

Edit the CSV files (see `UPDATE_GUIDE.md`), run `python3 tools/build.py`, then commit and push. GitHub Pages republishes the dashboard within a minute or two.

## How to cite

Mondal, S., & Chithralekha, T. (2026). *Blockchain in Indian Government Administration: A Project-Level Dataset (2017–2026)* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23136332

To cite version 1.1.0 exactly, use https://doi.org/10.5281/zenodo.23415599.

Map boundaries: DataMeet India community (CC BY 4.0).
