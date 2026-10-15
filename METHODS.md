# Methods: data model, collection, coding and quality control (v1.1.0)

## 1. Scope and unit of analysis

One project = one distinct use of blockchain/DLT by one implementing public body. When one NIC chain serves several departments, each onboarded department is a separate project. Window: first announcements (2017) to 15 October 2026.

**Included:** a public authority implemented, funded or mandated the initiative; it used or explicitly planned to use blockchain/DLT; at least one traceable source exists. Central bank digital currency (e₹) rows are included but flagged, because the RBI has not confirmed DLT use.
**Excluded:** no blockchain disclosed; NGO or private projects without a named government client; academic prototypes; tender-search false positives (listed in `excluded_items.csv`).

## 2. Data model (new in v1.1.0)

The dataset is a Frictionless Data Package (`datapackage.json`). Tables are normalised and linked by keys:

```
jurisdictions (ISO 3166-2) ─┬─ bodies ── projects ──┬── stage_events ── sources
                            └──────────── projects  ├── challenges ──── sources
                                                    ├── project_sources ─ sources
                                                    └── nic_snapshots ── sources
vocabularies: every coded field's allowed values, definitions and mappings
```

Standards used: ISO 3166-1/3166-2 (2023 revision: IN-CG, IN-OD, IN-TS, IN-UK) and Government of India LGD state codes for places; ISO 8601 partial dates (YYYY, YYYY-MM, YYYY-MM-DD) with an explicit precision field; UN COFOG divisions for policy function (assigned from the domain; approximate); G2C/G2B/G2G service types; Frictionless Table Schema for types, enums, primary and foreign keys. `tools/build.py` validates every table and also checks that each project has a latest-update event and no event is dated in the future.

## 3. Sources and search procedure

1. **National sweep:** NBF/Vishvasya, NIC chains, NITI Aayog, RBI, SEBI, TRAI, Supreme Court and eCourts, Election Commission, Union ministries.
2. **Jurisdiction-by-jurisdiction sweep:** each of the 28 States and 8 UTs searched individually, with follow-up queries on land records, certificates, police, health, agriculture and tenders (result per jurisdiction in `jurisdictions.csv`).
3. **Stage-date research (v1.1.0):** every project was researched again for dated events (announced, pilot started, pilot completed, live, scaled, discontinued, latest update). Rules: only dates a source supports; year or month precision when that is all a source gives; the date of a news article is not the event date unless it reports the event as happening then; evidence is paraphrased in at most 25 words. Researchers also checked whether the dated evidence still supports each project's stage. This added 208 sources. A separate check of a random sample (18 events, 8 challenges, 9 stage decisions, all NIC values) found 20 of 26 sampled events and challenges fully supported, the rest partly supported or unreachable; its fixes are applied.
4. **Official platform data:** the NIC Centre of Excellence publishes `blockchain.gov.in/Statistics/statistics.json`. It was read in a browser on 15 Oct 2026 (data date 14-10-2026); an Internet Archive capture of the same file (data date 23-07-2024) gives the 2024 baseline; the per-department table of 3 Oct 2026 (read in a browser) and the dashboard totals shown in a December 2025 presentation (as on 14-12-2025) fill in between. Department names are mapped to canonical units and to project IDs.
5. **Derived events:** where a department appears in an NIC snapshot with at least 100 documents and the project had no earlier go-live date, a "live by" event is recorded at that snapshot date (actual go-live may be earlier). The newest snapshot also gives a latest-update event for each mapped project.

## 4. Changes to records in v1.1.0

All changes are logged in `changelog.csv`. Stages changed for seven projects after the stage-date research: C19 → Pilot completed; S16 → Proposed / Planned; S17 → Unclear; S28 → In progress; S36 → Unclear; S61 → Unclear; S62 → Pilot completed. S36 describes the same June 2023 agreement as S17 from the provider's side, so it is kept as a `merged` record and excluded from counts (117 active projects). One project was added (S79, a blockchain birth certificate issued in New Town, Kolkata, December 2018). An independent check of a random sample of events, challenges and stage decisions led to further corrections: S68 kept as In progress (pilot trading since February 2026), two source dates fixed (R11, R15), status texts aligned with stages, and several event and challenge wordings made more precise. NIC-listed projects take their scale from the newest NIC snapshot.

## 5. Coded variables

Use-case (13 values), chain type, normalised platform, service type, start year, scale tier (counts of actual use only; targets and budgets excluded), main problem addressed, level of government, COFOG division and evidence score. Allowed values and definitions are in `vocabularies.csv`.

**Evidence score:** each source is scored 5 (official, live/current data), 4 (other official document), 3 (mainstream news), 2 (trade/crypto press or secondary), 1 (vendor, opinion or unverified). A project takes the score of its strongest linked source, capped at 1 if flagged unverified and at 2 if only vendor or slide-deck sources exist. In v1.1.0, 20 scores rose because official or news sources were found, and one fell (S46, blockchain claim not confirmed).

**Challenges (TOE):** coded only when a source reports the challenge for that specific project. Codes T1 interoperability/integration, T2 scalability, T3 security/privacy, T4 data quality/digitisation; O1 funding, O2 skills, O3 vendor dependence, O4 coordination/governance; E1 legal/regulatory, E2 user adoption, E3 policy discontinuity, E4 ecosystem/standards. `vocabularies.csv` gives a suggested mapping to Diffusion of Innovations attributes for discussion; that mapping is analytical, not empirical. Only 20 of 117 projects have a source that reports any challenge, so the absence of a code is not evidence of a smooth rollout.

## 6. Reliability

A random 30% sample (35 rows, seed 2026) was re-coded blind from the descriptive fields (v1.0.0): kappa 0.96 stage, 0.90 use-case, 0.96 chain type, 0.86 service type, 0.90 scale tier. Both codings were made with the same AI assistant, so this is a consistency check, not an independent inter-rater test. The workbook's "Your Coding Sheet" lets a human coder code the same rows; agreement and kappa against the v1.1.0 codes are calculated automatically, and that figure should be reported.

## 7. Limitations

1. Only publicly reported initiatives are covered.
2. "Unclear" (27 projects) means no public update was found, not failure; the 29 RTI drafts target these.
3. Chain type is undisclosed for 44.4% of projects and scale is unreported for 60.7%.
4. Some go-live dates are "live by" dates (earliest dated proof of use).
5. NIC snapshots are irregular before October 2026; department detail is missing for December 2025.
6. AI assistance was used throughout; the author reviewed the data.

## 8. Updates

Monthly NIC snapshots (`tools/nic_snapshot.py`), RTI replies and new projects are added through the same tables and released as new versions (semantic versioning; Zenodo "New version").
