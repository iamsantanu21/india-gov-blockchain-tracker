# How to update the dataset and the dashboard

Requirements: Python 3.9+ and `pip install frictionless openpyxl`.

## Add or change a project
1. **Body:** if the implementing body is new, add a row to `data/bodies.csv` (next free `ORGnnn`, its `jurisdiction_id`, `level`, `body_category` and `government_level`).
2. **Project:** add a row to `data/projects.csv` with the next free ID (`C` Union, `S` State/UT, `O` other public body), including `implementation_model`. Use only values listed in `data/vocabularies.csv` for coded fields; add a new value there first if you need one.
3. **Sources:** add each new source to `data/sources.csv` (next free `Wnnn`, `source_type`, `evidence_score` 1–5) and link it in `data/project_sources.csv`.
4. **Dates:** add dated events to `data/stage_events.csv` (`<project_id>-Enn`, ISO date, precision, `source_id`, a short paraphrase). Always add a `latest_update` event.
5. **Challenges:** only when a source reports one for that project: `data/challenges.csv`.
6. **Validate and rebuild:** `python3 tools/build.py` (stops with a clear message if a code, key or date is wrong). It also regenerates `data/all_projects.csv`, the combined table the dashboard reads; never edit that file by hand. Then `python3 tools/make_workbook.py`.
7. **Log it:** add a row to `data/changelog.csv`.

## Add a monthly NIC platform snapshot
1. Open https://blockchain.gov.in/Statistics/statistics.json in a browser and save the page as `statistics.json`.
2. `python3 tools/nic_snapshot.py statistics.json` — adds the snapshot rows, a source row, and a latest-update event per NIC project. It warns if totals fall or departments cannot be matched to a project (add those to `DEPT_MAP` in the script).
3. `python3 tools/build.py`.

## Publish
1. **GitHub (dashboard):** commit and push the changed files. GitHub Pages republishes the dashboard within a minute or two, and the "Validate dataset" check runs `tools/build.py` on every push. The page reads the CSVs directly, so every chart, the map and the numbers update.
2. **New Zenodo version** (when the changes are worth a new citable version):
   - bump `version` in `tools/package_meta.json` and `CITATION.cff`, and add the changes to `data/changelog.csv`;
   - run `python3 tools/build.py`, `python3 tools/make_workbook.py` and `python3 tools/make_release.py` (writes `dataset/India_Govt_Blockchain_Dataset_v<version>.zip`);
   - on Zenodo open the record → *New version* → upload that zip (steps in `ZENODO_UPLOAD_GUIDE.md`), then add the new version DOI to `dataset/README.md` and `CITATION.cff`.
