# Blockchain in Indian Government Administration: A Project-Level Dataset (2017–2026)

**Version:** 1.1.0 · **Data as on:** 15 October 2026 (NIC platform data as on 14 October 2026)
**Author:** Santanu Mondal, Pondicherry University (ORCID 0009-0001-6243-1709) · **Licence:** CC BY 4.0

## What this is

A standardised, source-linked database of **117 blockchain / distributed-ledger initiatives** (118 records; one duplicate is kept as a merged record) run, funded or mandated by Indian public bodies: Union ministries, all 28 States and 8 Union Territories (each searched individually), districts, municipal bodies, regulators (RBI, SEBI, TRAI), the Supreme Court, the Election Commission, statutory boards and PSUs.

From v1.1.0 the data are a **Frictionless Data Package**: normalised CSV tables with primary keys, foreign keys and controlled vocabularies, described in `datapackage.json`. New projects, dated events and platform snapshots can be added and checked automatically, and the online dashboard recalculates from the same files.

## Tables (`data/`)

| Table | Rows | Content |
|---|---|---|
| `projects.csv` | 118 | One row per project (117 active, 1 merged): tier, jurisdiction (ISO 3166-2), body, domain (+ UN COFOG division), stage, status, scale, coded variables, evidence score |
| `stage_events.csv` | 314 | Dated lifecycle events: announced, pilot started/completed, live, scaled, latest update; each with a source |
| `challenges.csv` | 39 | Challenges reported by a source for a specific project, coded T1–T4 / O1–O4 / E1–E4 (TOE) |
| `sources.csv` | 339 | All sources with type (Official / News / Secondary / Vendor) and evidence score |
| `project_sources.csv` | 500 | Which source supports which project, and in what role |
| `nic_snapshots.csv` | 202 | NIC blockchain platform time series (23 Jul 2024, 14 Dec 2025, 3 Oct 2026, 14 Oct 2026) by platform, application and department |
| `jurisdictions.csv` | 37 | India + 36 States/UTs: ISO 3166-2 (2023 codes), LGD code, search result |
| `bodies.csv` | 110 | Implementing public bodies |
| `vocabularies.csv` | 137 | Controlled lists and mappings: stage → generic lifecycle; challenge → TOE dimension and DOI attribute; domain → COFOG |
| `reliability.csv`, `policies.csv`, `literature.csv`, `context_stats.csv`, `excluded_items.csv`, `rti_drafts.csv`, `changelog.csv` | | Supporting tables |

`derived/` holds files rebuilt by `tools/build.py`: `projects_flat.csv` (one wide row per project with first event dates, months to go-live, challenge codes and source counts), `summary.json` and `india_gov_blockchain.sqlite` (all tables + a timeline view). `India_Govt_Blockchain_Database_v1.1.xlsx` is the Excel edition with live summary formulas and a blind coding sheet. `dashboard.html` is the tracker dashboard (serve the folder with `python3 -m http.server` and open it).

## Key figures (v1.1.0)

- 117 projects: 50 implemented (42.7%), 16 in progress, 13 proposed/planned, 11 pilots completed, 27 unclear (23.1%).
- Pilot-to-production rate (implemented ÷ [implemented + pilot completed + unclear]) = 56.8%.
- 52 projects have a dated go-live; for 19 with month-level start and go-live dates the median time to go-live is 6 months.
- Certificates and identity projects are implemented most often (20 of 28); land registry least (5 of 22).
- Where chain type is disclosed, 72.3% are permissioned. 27 of 36 States/UTs have at least one project.
- 61.5% of projects are backed by an official source (evidence score 4–5); mean score 3.85.
- NIC platform (14 Oct 2026): 11,31,10,631 documents and 47,76,36,605 verifications, up from 8,11,92,971 documents on 23 Jul 2024.

## Updating

See `UPDATE_GUIDE.md`. In short: edit the CSVs → `python3 tools/build.py` (validates and rebuilds) → `python3 tools/make_workbook.py` → publish the changed CSVs to the dashboard and a new Zenodo version. New NIC snapshots: `python3 tools/nic_snapshot.py statistics.json`.

## How to cite

Mondal, S. (2026). *Blockchain in Indian Government Administration: A Project-Level Dataset (2017–2026)* (Version 1.1.0) [Data set]. Zenodo. https://doi.org/[DOI to be added after upload]

## Credits and disclosure

Map boundaries: DataMeet India community, *India States* (CC BY 4.0), simplified. Source discovery, extraction, stage-date research, challenge coding and the consistency check were carried out with the assistance of Claude (Anthropic), an AI system. The author reviewed the dataset and is responsible for its content. "Unclear" means no public update was found, not that a project failed.
