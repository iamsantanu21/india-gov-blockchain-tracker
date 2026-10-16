# Blockchain in Indian Government Administration: A Project-Level Dataset (2017–2026)

**Version:** 1.1.0 · **Data as on:** 15 October 2026 (NIC platform data as on 14 October 2026)
**Authors:** Santanu Mondal (ORCID 0009-0001-6243-1709) and T. Chithralekha, Pondicherry University · **Licence:** CC BY 4.0
**DOI (all versions, always the latest):** [10.5281/zenodo.23136332](https://doi.org/10.5281/zenodo.23136332) · this version 1.1.0: [10.5281/zenodo.23415599](https://doi.org/10.5281/zenodo.23415599) · version 1.0.0: [10.5281/zenodo.23136333](https://doi.org/10.5281/zenodo.23136333)

## What this is

A standardised, source-linked database of **117 blockchain / distributed-ledger initiatives** (118 records; one duplicate is kept as a merged record) run, funded or mandated by Indian public bodies: Union ministries, all 28 States and 8 Union Territories (each searched individually), districts, municipal bodies, regulators (RBI, SEBI, TRAI), the Supreme Court, the Election Commission, statutory boards and PSUs.

From v1.1.0 the data are a **Frictionless Data Package**: normalised CSV tables with primary keys, foreign keys and controlled vocabularies, described in `datapackage.json`. New projects, dated events and platform snapshots can be added and checked automatically, and the online dashboard recalculates from the same files.

## Start here: `data/all_projects.csv`

**One combined table of every project** – Union ministries, State and UT departments, districts, municipal bodies, PSUs, regulators, courts, statutory boards and institutes – one row per project, 57 columns. Besides the basic fields it classifies each project by:

| Column | Values |
|---|---|
| `government_level` | Union · State · Union Territory · District · Municipal |
| `body_category` | Ministry / department · Government (whole of government) · IT / e-governance agency · Policy / planning body · PSU / state-owned company · Regulator / central bank · Court / judiciary · Election commission · Statutory board / authority · University / research institute · Society / foundation · District administration · Municipal body |
| `region` | Northern · Central · Eastern · Western · Southern · North-Eastern · Island UTs · National (MHA Zonal Councils / North Eastern Council) |
| `implementation_model` | Government IT (NIC / C-DAC / NeGD) · State IT agency (in-house) · Private technology vendor · Academic / research partner · Banks, depositories or telecom operators · Government–industry consortium · International organisation · Not applicable (policy or judgment) · Not disclosed |
| `platform_family` | Hyperledger family · Ethereum / EVM chains · Other public chains · Other enterprise DLT · CBDC infrastructure · Not disclosed |

It also carries the stage and generic stage, the first date of each lifecycle event, months to go-live, years since the latest evidence, the latest NIC documents and verifications, challenge codes and TOE dimensions, the evidence score and label, source counts and the strongest source URL. **The dashboard reads this table.** It is built automatically by `tools/build.py` from the tables below, so it is always in step with them: edit the source tables, not this one.

## Source tables (`data/`)

| Table | Rows | Content |
|---|---|---|
| `projects.csv` | 118 | One row per project (117 active, 1 merged): tier, jurisdiction (ISO 3166-2), body, domain (+ UN COFOG division), stage, status, scale, coded variables, evidence score |
| `stage_events.csv` | 314 | Dated lifecycle events: announced, pilot started/completed, live, scaled, latest update; each with a source |
| `challenges.csv` | 39 | Challenges reported by a source for a specific project, coded T1–T4 / O1–O4 / E1–E4 (TOE) |
| `sources.csv` | 339 | All sources with type (Official / News / Secondary / Vendor) and evidence score |
| `project_sources.csv` | 500 | Which source supports which project, and in what role |
| `nic_snapshots.csv` | 202 | NIC blockchain platform time series (23 Jul 2024, 14 Dec 2025, 3 Oct 2026, 14 Oct 2026) by platform, application and department |
| `jurisdictions.csv` | 37 | India + 36 States/UTs: ISO 3166-2 (2023 codes), LGD code, region, search result |
| `bodies.csv` | 110 | Implementing public bodies, with `body_category` and `government_level` |
| `vocabularies.csv` | 137 | Controlled lists and mappings: stage → generic lifecycle; challenge → TOE dimension and DOI attribute; domain → COFOG |
| `reliability.csv`, `policies.csv`, `literature.csv`, `context_stats.csv`, `excluded_items.csv`, `rti_drafts.csv`, `changelog.csv` | | Supporting tables |

`derived/` holds files rebuilt by `tools/build.py`: `summary.json` (headline numbers) and `india_gov_blockchain.sqlite` (all tables + a timeline view). `India_Govt_Blockchain_Database_v1.1.xlsx` is the Excel edition with live summary formulas and a blind coding sheet. `dashboard.html` is the tracker dashboard (serve the folder with `python3 -m http.server` and open it).

## Key figures (v1.1.0)

- 117 projects: 50 implemented (42.7%), 16 in progress, 13 proposed/planned, 11 pilots completed, 27 unclear (23.1%).
- Pilot-to-production rate (implemented ÷ [implemented + pilot completed + unclear]) = 56.8%.
- 52 projects have a dated go-live; for 19 with month-level start and go-live dates the median time to go-live is 6 months.
- Certificates and identity projects are implemented most often (20 of 28); land registry least (5 of 22).
- By level: Union 39, State 65, UT 6, district 4, municipal 3. Projects built on government IT (NIC / C-DAC / NeGD) are implemented far more often (31 of 43, 72%) than vendor-built ones (9 of 30, 30%), partly because each department onboarded to an NIC chain counts as its own project.
- Where chain type is disclosed, 72.3% are permissioned. 27 of 36 States/UTs have at least one project.
- 61.5% of projects are backed by an official source (evidence score 4–5); mean score 3.85.
- NIC platform (14 Oct 2026): 11,31,10,631 documents and 47,76,36,605 verifications, up from 8,11,92,971 documents on 23 Jul 2024.

## Updating

See `UPDATE_GUIDE.md`. In short: edit the CSVs → `python3 tools/build.py` (validates and rebuilds) → `python3 tools/make_workbook.py` → publish the changed CSVs to the dashboard and a new Zenodo version. New NIC snapshots: `python3 tools/nic_snapshot.py statistics.json`.

## How to cite

Mondal, S., & Chithralekha, T. (2026). *Blockchain in Indian Government Administration: A Project-Level Dataset (2017–2026)* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23136332

To cite this exact version: Mondal, S., & Chithralekha, T. (2026). *Blockchain in Indian Government Administration: A Project-Level Dataset (2017–2026)* (Version 1.1.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23415599

## Credits and disclosure

Map boundaries: DataMeet India community, *India States* (CC BY 4.0), simplified. Source discovery, extraction, stage-date research, challenge coding and the consistency check were carried out with the assistance of Claude (Anthropic), an AI system. The authors reviewed the dataset and are responsible for its content. "Unclear" means no public update was found, not that a project failed.
