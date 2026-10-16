#!/usr/bin/env python3
"""Validate and rebuild the India Government Blockchain dataset (Frictionless Data Package).

Edit the CSV files in data/, then run:   python3 tools/build.py
It will
  1. regenerate datapackage.json (schemas, keys, controlled vocabularies taken from data/vocabularies.csv),
  2. validate every table (types, required fields, enums, primary and foreign keys) and stop on errors,
  3. rebuild data/all_projects.csv (the combined master table used by the dashboard), derived/summary.json and the SQLite database.
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

ALLP_FIELDS = [
 ('project_id', 'Project ID (C = Union, S = State/UT, O = other public body)', 'string', None), ('project_name', 'Project name', 'string', None),
 ('description', 'What the project does', 'string', None), ('record_status', 'active, merged or withdrawn', 'string', ['active', 'merged', 'withdrawn']),
 ('government_level', 'Union, State, Union Territory, District or Municipal', 'string', 'government_level'),
 ('body_category', 'Kind of public body', 'string', 'body_category'), ('implementing_body', 'Implementing body', 'string', None),
 ('parent_ministry_or_state', 'Parent ministry or State', 'string', None), ('dataset_group', 'v1.0 grouping: Union government, State / UT government, Other public body', 'string', 'tier'),
 ('jurisdiction_id', 'ISO 3166-2 code (IN = Union / national)', 'string', None), ('state_ut', 'State or UT name (Union / national for IN)', 'string', None),
 ('jurisdiction_type', 'State, Union Territory or National', 'string', ['State', 'Union Territory', 'National']), ('region', 'Region (Zonal Councils / NEC)', 'string', 'region'),
 ('lgd_code', 'LGD state code', 'integer', None), ('domain', 'Policy domain', 'string', 'domain'), ('cofog_division', 'UN COFOG division', 'string', 'cofog_division'),
 ('cofog_label', 'COFOG division name', 'string', None), ('use_case', 'Use-case type', 'string', 'use_case'), ('problem', 'Main problem addressed', 'string', 'problem'),
 ('service_type', 'G2C, G2B or G2G', 'string', 'service_type'), ('platform_reported', 'Platform as reported', 'string', None),
 ('platform', 'Normalised platform', 'string', 'platform'), ('platform_family', 'Platform family', 'string', 'platform_family'),
 ('chain_type', 'Chain type', 'string', 'chain_type'), ('tech_partner', 'Technology partner(s)', 'string', None),
 ('implementation_model', 'Who built or runs the technology', 'string', 'implementation_model'), ('is_nic_chain', 'Runs on an NIC chain (Yes/No)', 'string', ['Yes', 'No']),
 ('stage', 'Current stage', 'string', 'stage'), ('stage_generic', 'Generic lifecycle stage (for cross-country comparison)', 'string', None),
 ('status_text', 'Current status as reported', 'string', None), ('status_as_of', 'Date of latest dated evidence', 'string', DATE),
 ('start_year', 'Start year', 'integer', None), ('date_announced', 'First announced', 'string', DATE), ('date_pilot_started', 'Pilot started', 'string', DATE),
 ('date_pilot_completed', 'Pilot completed', 'string', DATE), ('date_live', 'First live (go-live or live-by date)', 'string', DATE),
 ('date_scaled', 'Scaled', 'string', DATE), ('date_discontinued', 'Discontinued', 'string', DATE), ('date_latest_update', 'Latest dated evidence', 'string', DATE),
 ('months_to_live', 'Months from first announcement or pilot to go-live (month precision or better)', 'integer', None),
 ('years_since_update', 'Years from the latest evidence to the dataset date', 'number', None),
 ('scale_text', 'Scale as reported', 'string', None), ('scale_tier', 'Scale tier', 'string', 'scale_tier'),
 ('nic_documents_latest', 'Documents on NIC chains at the latest snapshot', 'integer', None), ('nic_verifications_latest', 'Verifications on NIC chains at the latest snapshot', 'integer', None),
 ('nic_snapshot_date', 'Date of that NIC snapshot', 'string', DATE), ('challenge_codes', 'Reported challenge codes (;-separated)', 'string', None),
 ('toe_dimensions', 'TOE dimensions of reported challenges', 'string', None), ('n_challenges', 'Number of reported challenges', 'integer', None),
 ('evidence_score', 'Evidence score 1-5', 'integer', None), ('evidence_label', 'Meaning of the evidence score', 'string', None),
 ('n_sources', 'Number of linked sources', 'integer', None), ('n_official_sources', 'Number of linked official sources', 'integer', None),
 ('primary_source_url', 'URL of the strongest source', 'string', None), ('verify_note', 'Caveats and verification flags', 'string', None),
 ('related_projects', 'Related rows', 'string', None), ('last_reviewed', 'Date last reviewed', 'string', DATE)]

def allp_schema():
    out = []
    for n, d, t, e in ALLP_FIELDS:
        kw = {}
        if isinstance(e, list): kw['enum'] = e
        elif e == DATE: kw['pattern'] = DATE
        elif isinstance(e, str): kw['enum'] = VOC[e]
        out.append(F(n, d, t, req=n in ('project_id', 'project_name', 'stage'), **kw))
    return out

TABLES = [
 ('all_projects', 'COMBINED MASTER TABLE: every project (Union, State, UT, district, municipal, PSU, regulator, court ...) in one row with all classifications, dates, NIC usage, challenges and evidence. Built automatically by tools/build.py from the other tables - do not edit by hand.',
  allp_schema(), ['project_id'], [('project_id', 'projects', 'project_id')]),
 ('jurisdictions', 'Countries, States and Union Territories (ISO 3166-2 keyed). One row per jurisdiction searched.', [
   F('jurisdiction_id', 'ISO 3166-1 alpha-2 country code (IN) or ISO 3166-2 subdivision code (2023 revision, e.g. IN-KA)', req=True, pattern=r'^[A-Z]{2}(-[A-Z]{2})?$'),
   F('name', 'Official English name', req=True), F('type', 'Country, State or Union Territory', req=True, enum=['Country', 'State', 'Union Territory']),
   F('lgd_code', 'Local Government Directory (LGD) state code, Govt of India', 'integer'), F('parent_id', 'Parent jurisdiction'),
   F('search_result', 'Outcome of the systematic search for this jurisdiction'), F('search_note', 'Notes from the search'),
   F('last_searched', 'Date of the latest systematic search (ISO 8601)', pattern=DATE),
   F('region', 'Region (MHA Zonal Councils / North Eastern Council; see vocabularies)', enum=VOC['region'])], ['jurisdiction_id'], []),
 ('bodies', 'Public bodies (organisations) that implement, fund or mandate projects.', [
   F('body_id', 'Stable identifier (ORGnnn)', req=True, pattern=r'^ORG\d{3,}$'), F('name', 'Name as reported', req=True),
   F('jurisdiction_id', 'Jurisdiction of the body (IN for Union-level bodies)', req=True), F('body_type', 'Type of body as reported'),
   F('level', 'Coded tier of government (v1.0 coding)', enum=VOC['level']), F('parent', 'Parent ministry or State'),
   F('body_category', 'Kind of public body (see vocabularies: body_category)', req=True, enum=VOC['body_category']),
   F('government_level', 'Union, State, Union Territory, District or Municipal', req=True, enum=VOC['government_level'])],
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
   F('tech_partner', 'Technology partner(s) as reported'),
   F('implementation_model', 'Who built or runs the technology (see vocabularies)', req=True, enum=VOC['implementation_model']),
   F('started_text', 'Start or announcement as reported (free text)'),
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

def build_all_projects():
    """Write data/all_projects.csv: one row per project, joined with body, place, events, NIC usage, challenges and sources."""
    P = read('projects.csv'); B = {b['body_id']: b for b in read('bodies.csv')}; J = {j['jurisdiction_id']: j for j in read('jurisdictions.csv')}
    E = read('stage_events.csv'); C = read('challenges.csv'); PS = read('project_sources.csv'); S = {s['source_id']: s for s in read('sources.csv')}
    N = read('nic_snapshots.csv'); V = collections.defaultdict(dict)
    for v in read('vocabularies.csv'): V[v['vocabulary']][v['code']] = v
    asof = max(p['last_reviewed'] for p in P)
    def mid(d):
        y = int(d[:4]); m = int(d[5:7]) if len(d) >= 7 else 7; dd = int(d[8:10]) if len(d) == 10 else 15
        return datetime.date(y, m, dd)
    def months(a, b):
        if not a or not b or len(a) < 7 or len(b) < 7: return ''
        m = (int(b[:4]) - int(a[:4])) * 12 + int(b[5:7]) - int(a[5:7])
        return m if m >= 0 else ''
    ev = collections.defaultdict(dict)
    for e in sorted(E, key=lambda e: e['date']):
        d = ev[e['project_id']]
        if e['event_type'] == 'latest_update': d['latest_update'] = e['date']
        else: d.setdefault(e['event_type'], e['date'])
    nic = {}
    for r in N:
        if r['level'] == 'department' and r['project_id'] and r['metric'] in ('documents', 'verifications_total'):
            nic.setdefault(r['project_id'], []).append(r)
    ROLE = {'citation': 0, 'event evidence': 1, 'challenge evidence': 2, 'additional': 3}
    rows = []
    for p in P:
        pid = p['project_id']; b = B.get(p['body_id'], {}); j = J.get(p['jurisdiction_id'], {}); d = ev.get(pid, {})
        start = d.get('announced') or d.get('pilot_started')
        chs = [c for c in C if c['project_id'] == pid]
        codes = sorted({c['challenge_code'] for c in chs})
        dims = sorted({V['challenge_code'].get(c, {}).get('maps_to', '').split('|')[0] for c in codes} - {''})
        links = sorted([x for x in PS if x['project_id'] == pid and x['source_id'] in S],
                       key=lambda x: (-int(S[x['source_id']]['evidence_score']), ROLE.get(x['role'], 9)))
        best = next((S[x['source_id']]['url'] for x in links if S[x['source_id']]['url']), '')
        nrows = nic.get(pid, []); ndate = max((r['snapshot_date'] for r in nrows), default='')
        ndocs = sum(int(r['value']) for r in nrows if r['snapshot_date'] == ndate and r['metric'] == 'documents') if ndate else ''
        nver = sum(int(r['value']) for r in nrows if r['snapshot_date'] == ndate and r['metric'] == 'verifications_total') if ndate else ''
        upd = p['status_as_of'] or d.get('latest_update', '')
        rows.append({
            'project_id': pid, 'project_name': p['title'], 'description': p['description'], 'record_status': p['record_status'],
            'government_level': b.get('government_level', ''), 'body_category': b.get('body_category', ''), 'implementing_body': b.get('name', ''),
            'parent_ministry_or_state': b.get('parent', ''), 'dataset_group': p['tier'],
            'jurisdiction_id': p['jurisdiction_id'], 'state_ut': 'Union / national' if p['jurisdiction_id'] == 'IN' else j.get('name', ''),
            'jurisdiction_type': 'National' if p['jurisdiction_id'] == 'IN' else j.get('type', ''), 'region': j.get('region', ''),
            'lgd_code': j.get('lgd_code', ''), 'domain': p['domain'], 'cofog_division': p['cofog_division'],
            'cofog_label': V['cofog_division'].get(p['cofog_division'], {}).get('label', ''), 'use_case': p['use_case'], 'problem': p['problem'],
            'service_type': p['service_type'], 'platform_reported': p['platform_reported'], 'platform': p['platform'],
            'platform_family': V['platform'].get(p['platform'], {}).get('maps_to', ''), 'chain_type': p['chain_type'], 'tech_partner': p['tech_partner'],
            'implementation_model': p['implementation_model'], 'is_nic_chain': 'Yes' if (p['platform'].startswith('NIC') or nrows) else 'No',
            'stage': p['stage'], 'stage_generic': V['stage'].get(p['stage'], {}).get('maps_to', ''), 'status_text': p['status_text'],
            'status_as_of': p['status_as_of'], 'start_year': p['start_year'],
            'date_announced': d.get('announced', ''), 'date_pilot_started': d.get('pilot_started', ''), 'date_pilot_completed': d.get('pilot_completed', ''),
            'date_live': d.get('live', ''), 'date_scaled': d.get('scaled', ''), 'date_discontinued': d.get('discontinued', ''),
            'date_latest_update': d.get('latest_update', ''), 'months_to_live': months(start, d.get('live', '')),
            'years_since_update': round((mid(asof) - mid(upd)).days / 365.25, 1) if upd else '',
            'scale_text': p['scale_text'], 'scale_tier': p['scale_tier'],
            'nic_documents_latest': ndocs, 'nic_verifications_latest': nver, 'nic_snapshot_date': ndate,
            'challenge_codes': ';'.join(codes), 'toe_dimensions': ';'.join(dims), 'n_challenges': len(chs),
            'evidence_score': p['evidence_score'], 'evidence_label': V['evidence_score'].get(str(p['evidence_score']), {}).get('label', ''),
            'n_sources': len(links), 'n_official_sources': sum(1 for x in links if S[x['source_id']]['source_type'] == 'Official'),
            'primary_source_url': best, 'verify_note': p['verify_note'], 'related_projects': p['related_projects'], 'last_reviewed': p['last_reviewed']})
    order = {'Union': 0, 'State': 1, 'Union Territory': 2, 'District': 3, 'Municipal': 4}
    rows.sort(key=lambda r: (order.get(r['government_level'], 9), r['state_ut'], r['project_id']))
    hdr = [f[0] for f in ALLP_FIELDS]
    assert list(rows[0].keys()) == hdr
    with open(os.path.join(DATA, 'all_projects.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=hdr); w.writeheader(); w.writerows(rows)
    old = os.path.join(DER, 'projects_flat.csv')
    if os.path.exists(old): os.remove(old)
    print(f'all_projects.csv: {len(rows)} rows x {len(hdr)} columns')

def summary():
    A = [r for r in read('all_projects.csv') if r['record_status'] == 'active']; n = len(A)
    st = collections.Counter(p['stage'] for p in A)
    known = [p for p in A if p['chain_type'] != 'Not disclosed']
    summ = {'version': META['version'], 'n_projects': n, 'by_stage': dict(st),
            'by_government_level': dict(collections.Counter(p['government_level'] for p in A)),
            'by_body_category': dict(collections.Counter(p['body_category'] for p in A)),
            'by_region': dict(collections.Counter(p['region'] for p in A)),
            'by_implementation_model': dict(collections.Counter(p['implementation_model'] for p in A)),
            'pilot_to_production': round(st['Implemented'] / (st['Implemented'] + st['Pilot completed'] + st['Unclear (no recent update)']), 4),
            'permissioned_share_of_disclosed': round(sum(p['chain_type'] == 'Permissioned' for p in known) / len(known), 4),
            'jurisdictions_with_projects': len({p['jurisdiction_id'] for p in A if p['jurisdiction_id'] != 'IN'}),
            'n_records_merged_or_withdrawn': len(read('projects.csv')) - n,
            'n_sources': len(read('sources.csv')), 'n_events': len(read('stage_events.csv')), 'n_challenges': len(read('challenges.csv')),
            'evidence_mean': round(sum(int(p['evidence_score']) for p in A) / n, 2),
            'evidence_official_share': round(sum(int(p['evidence_score']) >= 4 for p in A) / n, 4)}
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
        def cv(v, t): return None if v == '' else (int(v) if t == 'integer' else float(v) if t == 'number' else v)
        con.executemany(f'INSERT INTO "{r["name"]}" VALUES ({",".join("?" * len(fl))})', [[cv(x[f['name']], f['type']) for f in fl] for x in rows])
    con.execute('''CREATE VIEW v_project_timeline AS SELECT p.project_id, p.title, p.stage, e.event_type, e.date, e.date_precision, s.title AS source_title, s.url
                   FROM projects p JOIN stage_events e USING(project_id) LEFT JOIN sources s ON s.source_id = e.source_id ORDER BY p.project_id, e.date''')
    con.commit(); con.close(); print('sqlite: OK')

if __name__ == '__main__':
    build_all_projects(); build_package(); validate(); summary(); sqlite()
