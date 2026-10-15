#!/usr/bin/env python3
"""Validate and rebuild the India Government Blockchain dataset (Frictionless Data Package).

Edit the CSV files in data/, then run:   python3 tools/build.py
It will
  1. regenerate datapackage.json (schemas, keys, controlled vocabularies taken from data/vocabularies.csv),
  2. validate every table (types, required fields, enums, primary and foreign keys) and stop on errors,
  3. rebuild the derived files in derived/ (projects_flat.csv, summary.json) and the SQLite database.
Requires: Python 3.9+, `pip install frictionless`.
"""
import csv, json, os, sqlite3, sys, collections, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data'); DER = os.path.join(ROOT, 'derived'); os.makedirs(DER, exist_ok=True)
META = json.load(open(os.path.join(ROOT, 'tools', 'package_meta.json'), encoding='utf-8'))

def read(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f: return list(csv.DictReader(f))

VOC = collections.defaultdict(list)
for r in read('vocabularies.csv'): VOC[r['vocabulary']].append(r['code'])

DATE = r'^\d{4}(-\d{2}(-\d{2})?)?$'
def F(name, desc, typ='string', req=False, enum=None, pattern=None, **kw):
    f = {'name': name, 'type': typ, 'description': desc}
    c = {}
    if req: c['required'] = True
    if enum: c['enum'] = enum
    if pattern: c['pattern'] = pattern
    c.update(kw)
    if c: f['constraints'] = c
    return f

TABLES = [
 ('jurisdictions', 'Countries, States and Union Territories (ISO 3166-2 keyed). One row per jurisdiction searched.', [
   F('jurisdiction_id', 'ISO 3166-1 alpha-2 country code (IN) or ISO 3166-2 subdivision code (2023 revision, e.g. IN-KA)', req=True, pattern=r'^[A-Z]{2}(-[A-Z]{2})?$'),
   F('name', 'Official English name', req=True), F('type', 'Country, State or Union Territory', req=True, enum=['Country', 'State', 'Union Territory']),
   F('lgd_code', 'Local Government Directory (LGD) state code, Govt of India', 'integer'), F('parent_id', 'Parent jurisdiction'),
   F('search_result', 'Outcome of the systematic search for this jurisdiction'), F('search_note', 'Notes from the search'),
   F('last_searched', 'Date of the latest systematic search (ISO 8601)', pattern=DATE)], ['jurisdiction_id'], []),
 ('bodies', 'Public bodies (organisations) that implement, fund or mandate projects.', [
   F('body_id', 'Stable identifier (ORGnnn)', req=True, pattern=r'^ORG\d{3,}$'), F('name', 'Name as reported', req=True),
   F('jurisdiction_id', 'Jurisdiction of the body (IN for Union-level bodies)', req=True), F('body_type', 'Type of body as reported'),
   F('level', 'Coded tier of government', enum=VOC['level']), F('parent', 'Parent ministry or State')],
   ['body_id'], [('jurisdiction_id', 'jurisdictions', 'jurisdiction_id')]),
 ('projects', 'One row per blockchain/DLT initiative by one implementing public body (unit of analysis).', [
   F('project_id', 'Stable identifier: C = Union, S = State/UT, O = other public body', req=True, pattern=r'^[CSO]\d{2,}$'),
   F('record_status', 'active, merged or withdrawn', req=True, enum=['active', 'merged', 'withdrawn']),
   F('country', 'ISO 3166-1 alpha-2 country code', req=True, pattern=r'^[A-Z]{2}$'),
   F('tier', 'Tier of government', req=True, enum=VOC['tier']), F('jurisdiction_id', 'Implementing jurisdiction', req=True),
   F('body_id', 'Implementing body', req=True), F('level', 'Coded level of the implementing body', enum=VOC['level']),
   F('title', 'Project name', req=True), F('domain', 'Policy domain (author-defined)', req=True, enum=VOC['domain']),
   F('cofog_division', 'UN COFOG division (2-digit), assigned from domain', enum=VOC['cofog_division']),
   F('description', 'What the project does'), F('platform_reported', 'Blockchain platform as reported in sources'),
   F('tech_partner', 'Technology partner(s) as reported'), F('started_text', 'Start or announcement as reported (free text)'),
   F('start_year', 'Coded start year', 'integer', minimum=2015, maximum=2035),
   F('stage', 'Current lifecycle stage, from the latest dated source', req=True, enum=VOC['stage']),
   F('status_text', 'Current status as reported'), F('status_as_of', 'Date of the latest dated evidence on status (ISO 8601 partial date)', pattern=DATE),
   F('scale_text', 'Scale as reported (documents, users, transactions)'), F('scale_tier', 'Coded scale tier', enum=VOC['scale_tier']),
   F('use_case', 'Coded use-case type', enum=VOC['use_case']), F('chain_type', 'Coded chain type', enum=VOC['chain_type']),
   F('platform', 'Normalised platform', enum=VOC['platform']), F('service_type', 'G2C, G2B or G2G', enum=VOC['service_type']),
   F('problem', 'Main problem addressed', enum=VOC['problem']),
   F('evidence_score', 'Evidence score 1-5 (strongest linked source, capped by verify note)', 'integer', minimum=1, maximum=5),
   F('evidence_basis', 'How the evidence score was derived'), F('verify_note', 'Conflicts, caveats or verification flags'),
   F('related_projects', 'IDs of closely related rows (e.g. two sides of one agreement)'),
   F('last_reviewed', 'Date the row was last reviewed', pattern=DATE)],
   ['project_id'], [('jurisdiction_id', 'jurisdictions', 'jurisdiction_id'), ('body_id', 'bodies', 'body_id')]),
 ('stage_events', 'Dated lifecycle events per project (long format). Supports stage dates, time-to-live and pilot-to-production analysis.', [
   F('event_id', 'Stable identifier (<project_id>-Enn)', req=True), F('project_id', 'Project', req=True),
   F('event_type', 'Type of event', req=True, enum=VOC['event_type']), F('date', 'Event date, ISO 8601 partial date (YYYY, YYYY-MM or YYYY-MM-DD)', req=True, pattern=DATE),
   F('date_precision', 'year, month or day', req=True, enum=['year', 'month', 'day']), F('source_id', 'Source supporting the event', req=True),
   F('evidence', 'Short paraphrase of what the source says (no quotation)'), F('recorded_by', 'Who recorded the event'),
   F('recorded_on', 'Date recorded', pattern=DATE)],
   ['event_id'], [('project_id', 'projects', 'project_id'), ('source_id', 'sources', 'source_id')]),
 ('challenges', 'Challenges reported by sources for a specific project, coded on a TOE (technology-organisation-environment) scheme.', [
   F('challenge_id', 'Stable identifier (<project_id>-Cnn)', req=True), F('project_id', 'Project', req=True),
   F('challenge_code', 'Challenge code (see vocabularies: challenge_code)', req=True, enum=VOC['challenge_code']),
   F('description', 'Project-specific description'), F('source_id', 'Source reporting the challenge', req=True),
   F('evidence', 'Short paraphrase of the source'), F('recorded_by', 'Who coded it'), F('recorded_on', 'Date coded', pattern=DATE)],
   ['challenge_id'], [('project_id', 'projects', 'project_id'), ('source_id', 'sources', 'source_id')]),
 ('sources', 'Bibliographic sources with type and evidence score.', [
   F('source_id', 'Stable identifier (R/N/B/D = v1.0 references; W = added in v1.1)', req=True), F('author', 'Author or issuing body'),
   F('date', 'Publication date (ISO 8601 partial date)', pattern=DATE), F('date_precision', 'year, month or day', enum=['year', 'month', 'day']),
   F('title', 'Title', req=True), F('publisher', 'Publisher'), F('url', 'URL'), F('note', 'Access note when no URL'),
   F('source_type', 'Official, News, Secondary or Vendor', req=True, enum=VOC['source_type']),
   F('evidence_score', 'Evidence score of this source (1-5)', 'integer', req=True, minimum=1, maximum=5),
   F('accessed', 'Date accessed', pattern=DATE), F('added_in', 'Dataset version that added the source')],
   ['source_id'], []),
 ('project_sources', 'Links between projects and sources, with the role each source plays.', [
   F('project_id', 'Project', req=True), F('source_id', 'Source', req=True), F('role', 'Role of the source', req=True, enum=VOC['source_role'])],
   ['project_id', 'source_id'], [('project_id', 'projects', 'project_id'), ('source_id', 'sources', 'source_id')]),
 ('nic_snapshots', 'Time series of the NIC (National Informatics Centre) blockchain platform: documents and verifications by platform, application and department.', [
   F('snapshot_date', 'Data date of the snapshot', req=True, pattern=DATE), F('source_id', 'Source of the snapshot', req=True),
   F('level', 'platform, application or department', req=True, enum=['platform', 'application', 'department']),
   F('application', 'Application/chain as listed by NIC'), F('chain_product', 'NIC blockchain product family'),
   F('unit', 'Canonical organisation – department label (stable across snapshots)'), F('unit_as_published', 'Name as published in that snapshot'),
   F('project_id', 'Matching project row, if any'), F('metric', 'Metric', req=True, enum=VOC['nic_metric']),
   F('value', 'Value', 'integer', req=True, minimum=0), F('note', 'Notes')],
   [], [('source_id', 'sources', 'source_id'), ('project_id', 'projects', 'project_id')]),
 ('vocabularies', 'Controlled vocabularies, definitions and mappings (TOE/DOI for challenges, COFOG for domains, generic lifecycle for stages).', [
   F('vocabulary', 'Vocabulary name', req=True), F('code', 'Code', req=True), F('label', 'Label'), F('definition', 'Definition'), F('maps_to', 'Mapping to another standard')],
   ['vocabulary', 'code'], []),
 ('reliability', 'Coding consistency check: agreement and Cohen kappa on a 30% sample (v1.0.0).', None, [], []),
 ('policies', 'Policies, frameworks, tenders, judgments and parliamentary items.', None, [], []),
 ('literature', 'Related academic and practitioner literature.', None, [], []),
 ('context_stats', 'National context figures with sources.', None, [], []),
 ('excluded_items', 'Items checked and excluded, with reasons.', None, [], []),
 ('rti_drafts', 'Draft Right to Information applications for projects with unclear status.', None, [], []),
 ('changelog', 'Changes by version.', None, [], []),
]

def build_package():
    res = []
    for name, desc, fields, pk, fks in TABLES:
        path = f'data/{name}.csv'
        hdr = next(csv.reader(open(os.path.join(ROOT, path), encoding='utf-8')))
        if fields is None: fields = [{'name': h, 'type': 'string'} for h in hdr]
        assert [f['name'] for f in fields] == hdr, f'{name}: header mismatch\n{hdr}\n{[f["name"] for f in fields]}'
        schema = {'fields': fields, 'missingValues': ['']}
        if pk: schema['primaryKey'] = pk
        if fks: schema['foreignKeys'] = [{'fields': a, 'reference': {'resource': b, 'fields': c}} for a, b, c in fks]
        res.append({'name': name, 'path': path, 'profile': 'tabular-data-resource', 'format': 'csv', 'mediatype': 'text/csv',
                    'encoding': 'utf-8', 'description': desc, 'schema': schema})
    pkg = dict(META); pkg['resources'] = res
    json.dump(pkg, open(os.path.join(ROOT, 'datapackage.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    return pkg

def validate():
    from frictionless import Package, validate as fvalidate
    report = fvalidate(os.path.join(ROOT, 'datapackage.json'))
    if not report.valid:
        for e in report.errors[:15]: print(f'  [package] {e.type}: {e.message}')
        for task in report.tasks:
            for e in task.errors[:15]: print(f'  [{task.name}] {e.type}: {e.message}')
        sys.exit('VALIDATION FAILED - fix the rows above, then run again.')
    # extra rules frictionless cannot express
    P = {p['project_id']: p for p in read('projects.csv')}
    E = read('stage_events.csv')
    problems = []
    for pid, p in P.items():
        ev = [e for e in E if e['project_id'] == pid]
        if not any(e['event_type'] == 'latest_update' for e in ev): problems.append(f'{pid}: no latest_update event')
        if p['stage'] == 'Discontinued' and not any(e['event_type'] == 'discontinued' for e in ev): problems.append(f'{pid}: Discontinued without a discontinued event')
        lu = [e['date'] for e in ev if e['event_type'] == 'latest_update']
        if lu and p['status_as_of'] != max(lu): problems.append(f'{pid}: status_as_of {p["status_as_of"]} is not the latest latest_update date {max(lu)}')
    for e in E:
        if e['date'] > datetime.date.today().isoformat(): problems.append(f'{e["event_id"]}: date in the future')
    if problems:
        print('\n'.join(problems)); sys.exit('RULE CHECK FAILED')
    print('validation: OK')

def derived():
    P = read('projects.csv'); B = {b['body_id']: b for b in read('bodies.csv')}; J = {j['jurisdiction_id']: j for j in read('jurisdictions.csv')}
    E = read('stage_events.csv'); C = read('challenges.csv'); PS = read('project_sources.csv'); S = {s['source_id']: s for s in read('sources.csv')}
    ev = collections.defaultdict(dict)
    for e in sorted(E, key=lambda e: e['date']):
        d = ev[e['project_id']]
        if e['event_type'] == 'latest_update': d['latest_update'] = e['date']
        else: d.setdefault(e['event_type'], e['date'])      # first occurrence
    def months(a, b):
        if not a or not b or len(a) < 7 or len(b) < 7: return ''
        return (int(b[:4]) - int(a[:4])) * 12 + int(b[5:7]) - int(a[5:7])
    rows = []
    for p in P:
        d = ev[p['project_id']]
        start = d.get('announced') or d.get('pilot_started')
        rows.append({**p, 'body_name': B[p['body_id']]['name'], 'jurisdiction_name': J[p['jurisdiction_id']]['name'],
                     'date_announced': d.get('announced', ''), 'date_pilot_started': d.get('pilot_started', ''),
                     'date_pilot_completed': d.get('pilot_completed', ''), 'date_live': d.get('live', ''), 'date_scaled': d.get('scaled', ''),
                     'date_discontinued': d.get('discontinued', ''), 'date_latest_update': d.get('latest_update', ''),
                     'months_to_live': months(start, d.get('live', '')),
                     'challenge_codes': ';'.join(sorted({c['challenge_code'] for c in C if c['project_id'] == p['project_id']})),
                     'n_sources': sum(1 for x in PS if x['project_id'] == p['project_id']),
                     'n_official_sources': sum(1 for x in PS if x['project_id'] == p['project_id'] and S[x['source_id']]['source_type'] == 'Official')})
    with open(os.path.join(DER, 'projects_flat.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    # summary numbers (used in README / paper) - active records only
    P = [p for p in P if p['record_status'] == 'active']
    st = collections.Counter(p['stage'] for p in P); n = len(P)
    known = [p for p in P if p['chain_type'] not in ('Not disclosed',)]
    summ = {'version': META['version'], 'n_projects': n, 'by_stage': dict(st), 'by_tier': dict(collections.Counter(p['tier'] for p in P)),
            'pilot_to_production': round(st['Implemented'] / (st['Implemented'] + st['Pilot completed'] + st['Unclear (no recent update)']), 4),
            'permissioned_share_of_disclosed': round(sum(p['chain_type'] == 'Permissioned' for p in known) / len(known), 4),
            'jurisdictions_with_projects': len({p['jurisdiction_id'] for p in P if p['jurisdiction_id'] != 'IN'}),
            'n_records_merged_or_withdrawn': len(read('projects.csv')) - n,
            'n_sources': len(S), 'n_events': len(E), 'n_challenges': len(C),
            'evidence_mean': round(sum(int(p['evidence_score']) for p in P) / n, 2),
            'evidence_official_share': round(sum(int(p['evidence_score']) >= 4 for p in P) / n, 4)}
    json.dump(summ, open(os.path.join(DER, 'summary.json'), 'w'), indent=1)
    print(json.dumps(summ))

def sqlite():
    dbp = os.path.join(DER, 'india_gov_blockchain.sqlite')
    if os.path.exists(dbp): os.remove(dbp)
    con = sqlite3.connect(dbp)
    pkg = json.load(open(os.path.join(ROOT, 'datapackage.json'), encoding='utf-8'))
    TYPES = {'integer': 'INTEGER', 'number': 'REAL'}
    for r in pkg['resources']:
        fl = r['schema']['fields']; cols = ', '.join(f'"{f["name"]}" {TYPES.get(f["type"], "TEXT")}' for f in fl)
        pk = r['schema'].get('primaryKey'); cols += f', PRIMARY KEY ({", ".join(pk)})' if pk else ''
        for fk in r['schema'].get('foreignKeys', []):
            cols += f', FOREIGN KEY ({fk["fields"]}) REFERENCES {fk["reference"]["resource"]}({fk["reference"]["fields"]})'
        con.execute(f'CREATE TABLE "{r["name"]}" ({cols})')
        rows = read(os.path.basename(r['path']))
        def cv(v, t): return (int(v) if t == 'integer' and v != '' else (None if v == '' else v))
        con.executemany(f'INSERT INTO "{r["name"]}" VALUES ({",".join("?" * len(fl))})', [[cv(x[f['name']], f['type']) for f in fl] for x in rows])
    con.execute('''CREATE VIEW v_project_timeline AS SELECT p.project_id, p.title, p.stage, e.event_type, e.date, e.date_precision, s.title AS source_title, s.url
                   FROM projects p JOIN stage_events e USING(project_id) LEFT JOIN sources s ON s.source_id = e.source_id ORDER BY p.project_id, e.date''')
    con.commit(); con.close(); print('sqlite: OK')

if __name__ == '__main__':
    build_package(); validate(); derived(); sqlite()
