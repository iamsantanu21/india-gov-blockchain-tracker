# Zenodo: adding a new version (about 10 minutes)

All versions (concept DOI): https://doi.org/10.5281/zenodo.23136332 · Version 1.0.0: https://doi.org/10.5281/zenodo.23136333 · Version 1.1.0: https://doi.org/10.5281/zenodo.23415599 (published 16 Oct 2026). Use the same steps for later versions.

Your record is https://zenodo.org/records/23136333 (DOI 10.5281/zenodo.23136333, version v1).
A published Zenodo record cannot have its files replaced. You add the update as a **new version** of the same record.

1. Log in to Zenodo and open https://zenodo.org/records/23136333.
2. Click **New version** (right-hand side). Zenodo copies all the details from v1 into a new draft.
3. **Files:** delete `India_Govt_Blockchain_Dataset_v1.0.0.zip` from the draft and upload **India_Govt_Blockchain_Dataset_v1.1.0.zip**.
4. Change these fields (keep everything else as it is):

| Zenodo field | New value |
|---|---|
| Version | 1.1.0 |
| Publication date | today's date |
| Description | paste the text below |
| Keywords | add: land records; digital certificates; CBDC; public sector; TOE framework; Frictionless Data Package |

5. Click **Publish**.

## Description (paste into the Description box)

Standardised, source-linked database of 117 blockchain / distributed-ledger initiatives by Indian public bodies: Union ministries, all 28 States and 8 Union Territories (each searched individually), districts, municipal bodies, regulators (RBI, SEBI, TRAI), the Supreme Court, the Election Commission, statutory boards and public sector undertakings.

Version 1.1.0 restructures the data as a Frictionless Data Package: 17 linked CSV tables with schemas, primary and foreign keys and controlled vocabularies. One combined table (all_projects.csv, 57 columns) gives every project in one row, classified by level of government, type of public body, region (Zonal Councils), who built it, use-case, COFOG domain and platform family. The package adds 314 dated lifecycle events (announced, pilot, live, scaled, latest evidence), 39 source-reported challenges coded on the technology–organisation–environment (TOE) framework, an evidence score (1–5) per project, links to 339 sources, ISO 3166-2 and LGD codes for all 36 States and UTs, and a time series of the NIC blockchain platform by department (July 2024 to October 2026; 11.31 crore documents and 47.76 crore verifications on 14 October 2026).

Also included: a validation and build tool (Python), SQLite and Excel editions, an offline copy of the dashboard, methods, a codebook, a coding-consistency check (Cohen's kappa), excluded items, draft RTI applications and a changelog listing every change from version 1.0.0.

## After publishing

- The new version gets its **own new DOI**. The v1 DOI (10.5281/zenodo.23136333) keeps working and its page shows "a newer version is available".
- On the record page, the **Cite all versions** box shows a DOI that always points to the latest version. Use that one in the paper and the dashboard if you want one DOI that never goes out of date.
