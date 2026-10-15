# How to update the dataset and the dashboard

Requirements: Python 3.9+ and `pip install frictionless openpyxl`.

## Add or change a project
1. **Body:** if the implementing body is new, add a row to `data/bodies.csv` (next free `ORGnnn`, its `jurisdiction_id`, `level`).
2. **Project:** add a row to `data/projects.csv` with the next free ID (`C` Union, `S` State/UT, `O` other public body). Use only values listed in `data/vocabularies.csv` for coded fields; add a new value there first if you need one.
3. **Sources:** add each new source to `data/sources.csv` (next free `Wnnn`, `source_type`, `evidence_score` 1–5) and link it in `data/project_sources.csv`.
4. **Dates:** add dated events to `data/stage_events.csv` (`<project_id>-Enn`, ISO date, precision, `source_id`, a short paraphrase). Always add a `latest_update` event.
5. **Challenges:** only when a source reports one for that project: `data/challenges.csv`.
6. **Validate and rebuild:** `python3 tools/build.py` (stops with a clear message if a code, key or date is wrong), then `python3 tools/make_workbook.py`.
7. **Log it:** add a row to `data/changelog.csv`.

## Add a monthly NIC platform snapshot
1. Open https://blockchain.gov.in/Statistics/statistics.json in a browser and save the page as `statistics.json`.
2. `python3 tools/nic_snapshot.py statistics.json` — adds the snapshot rows, a source row, and a latest-update event per NIC project. It warns if totals fall or departments cannot be matched to a project (add those to `DEPT_MAP` in the script).
3. `python3 tools/build.py`.

## Publish
- **Dashboard:** republish the changed files under `data/` to the dashboard artifact. The page reads the CSVs directly, so every chart, the map and the KPIs update. (In a Claude session: "update my India Government Blockchain Tracker with these files".)
- **Zenodo:** open the record → *New version* → upload the new zip → bump `version` in `tools/package_meta.json` and `CITATION.cff`.
