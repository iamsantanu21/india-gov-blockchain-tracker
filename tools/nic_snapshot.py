#!/usr/bin/env python3
"""Add one NIC blockchain-platform snapshot to the dataset.

Usage:  python3 tools/nic_snapshot.py path/to/statistics.json [--retrieved YYYY-MM-DD]

The file is https://blockchain.gov.in/Statistics/statistics.json (open it in a browser and save the text).
The script
  * reads the data date inside the file (e.g. "14-10-2026"),
  * stops if that date is already in data/nic_snapshots.csv,
  * adds platform, application and department rows to data/nic_snapshots.csv,
  * adds a source row (NIC-YYYY-MM-DD) to data/sources.csv,
  * adds a 'latest_update' stage event for every mapped project and moves its status_as_of forward,
  * prints sanity checks (totals vs previous snapshot) and any department it could not map to a project.
Then run:  python3 tools/build.py   (validation + derived files)
"""
import csv, json, os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); DATA = os.path.join(ROOT, 'data')
CHAIN_PRODUCT = {'Central Board of Secondary Education': 'Certificate Chain', 'SSLC & PUC': 'Certificate Chain', 'Certificate Chain': 'Certificate Chain',
                 'Document Chain': 'Document Chain', 'Property Chain': 'Property Chain', 'Judiciary Chain': 'Judiciary Chain',
                 'ICJS Chain': 'ICJS Chain', 'Drug logistics': 'Logistics Chain'}
DEPT_MAP = [  # (organisation contains, department contains, application, project_id, canonical unit label)
 ('karnataka', 'revenue', 'Document Chain', 'S24', 'Karnataka – Revenue Department'),
 ('karnataka', 'revenue', 'Property Chain', 'S26', 'Karnataka – Revenue Department'),
 ('karnataka', 'economics', 'Document Chain', 'S23', 'Karnataka – Directorate of Economics & Statistics'),
 ('karnataka', 'town municipal', 'Property Chain', 'S27', 'Karnataka – Town Municipal Council'),
 ('karnataka', 'city corporation', 'Property Chain', 'S27', 'Karnataka – City Corporation'),
 ('jharkhand', 'revenue', 'Property Chain', 'S21', 'Jharkhand – Department of Revenue'),
 ('andhra pradesh', 'revenue', 'Property Chain', 'S06', 'Andhra Pradesh – Department of Revenue'),
 ('andhra pradesh', 'survey', 'Property Chain', 'S06', 'Andhra Pradesh – Department of Survey'),
 ('andhra pradesh', 'water', 'Document Chain', 'S04', 'Andhra Pradesh – Water Resources Department'),
 ('delhi', 'revenue', 'Document Chain', 'S74', 'Delhi – Revenue Department'),
 ('consumer affairs', 'consumer', 'Document Chain', 'C11', 'Ministry of Consumer Affairs – Department of Consumer Affairs'),
 ('maharashtra', 'general admin', 'Document Chain', 'S42', 'Maharashtra – General Administration Department'),
 ('rural development', 'rural skills', 'Document Chain', 'C12', 'Ministry of Rural Development – Rural Skills Division'),
 ('puducherry', 'civil supplies', 'Document Chain', 'S78', 'Puducherry – Department of Civil Supplies & Consumer Affairs'),
 ('puducherry', 'revenue', 'Document Chain', 'S77', 'Puducherry – Revenue Department'),
 ('puducherry', 'revenue', 'Property Chain', '', 'Puducherry – Revenue Department'),
 ('uttarakhand', 'good governance', 'Document Chain', 'S70', 'Uttarakhand – Department of IT, Good Governance & Science and Technology'),
 ('chhattisgarh', 'indira gandhi', 'Certificate Chain', 'S12', 'Chhattisgarh – Indira Gandhi Krishi Vishwavidyalaya, Raipur'),
 ('maharashtra', 'health sciences', 'Certificate Chain', 'S40', 'Maharashtra – Maharashtra University of Health Sciences'),
 ('maharashtra', 'nursing', 'Certificate Chain', 'S41', 'Maharashtra – State Board of Nursing & Paramedical Education'),
 ('manipur', 'higher secondary', 'Certificate Chain', 'S48', 'Manipur – Council of Higher Secondary Education'),
 ('justice', 'supreme court', 'Judiciary Chain', 'C08', 'Ministry of Law & Justice – Supreme Court of India'),
 ('justice', 'high court', 'ICJS Chain', 'C09', 'Ministry of Law & Justice – High Court of Karnataka'),
 ('central board', 'secondary education', 'Central Board of Secondary Education', 'O14', 'Central Board of Secondary Education'),
 ('karnataka', 'examination', 'SSLC & PUC', 'S25', 'Karnataka – School Examination and Assessment Board'),
 ('karnataka', 'medical supplies', 'Drug logistics', 'S22', 'Karnataka – State Medical Supplies Corporation Ltd')]
UNMAPPED = []

def num(s):
    s = str(s).strip().replace(',', '')
    return int(s) if re.fullmatch(r'\d+', s) else None
def clean_org(o):
    o = o.strip().replace(' - UT', '')
    return o.title() if o.isupper() else o
def map_dept(org, dept, app):
    o, d = org.lower(), dept.lower()
    for a, b, ap, pid, lab in DEPT_MAP:
        if a in o and b in d and ap == app: return pid, lab
    UNMAPPED.append((org, dept, app)); return '', f'{org} – {dept}'
def inr(n):
    s = str(int(n)); head, tail = s[:-3], s[-3:]; parts = []
    while len(head) > 2: parts.insert(0, head[-2:]); head = head[:-2]
    return ','.join(([head] if head else []) + parts + [tail]) if len(s) > 3 else s

def rows_from_stats(j, date, sid):
    out = []
    def add(level, app, org, dept, metric, value, note=''):
        if value is None: return
        pid, lab = map_dept(org, dept, app) if level == 'department' else (('C01' if level == 'platform' else ''), '')
        pub = (app if 'single department' in note else (f'{org} – {dept}' if org != dept else org)) if level == 'department' else ''
        out.append([date, sid, level, app, CHAIN_PRODUCT.get(app, ''), lab, pub, pid, metric, value, note])
    arr = lambda k: [x['name'] if isinstance(x, dict) else x for x in (j.get(k, {}).get(k, []) if isinstance(j.get(k), dict) else j.get(k, []))]
    add('platform', '', '', '', 'documents', num(j['txn']['length']))
    if 'reads' in j: add('platform', '', '', '', 'verifications_total', num(j['reads']['length']))
    add('platform', '', '', '', 'products', num(j['Blockchain']['length']))
    add('platform', '', '', '', 'departments', num(j['dept']['length']))
    add('platform', '', '', '', 'organisations_states', num(j['state']['length']))
    for s in arr('txn_applications'):
        name, v = s.rsplit(' - ', 1); add('application', name.strip(), '', '', 'documents', num(v))
    for s in arr('read_applications'):
        name, tot, mon = s.rsplit(' - ', 2)
        add('application', name.strip(), '', '', 'verifications_total', num(tot)); add('application', name.strip(), '', '', 'verifications_current_month', num(mon), 'month-to-date on the data date')
    APPKEY = {'txn_cert_applications': 'Certificate Chain', 'txn_doc_applications': 'Document Chain', 'txn_icjs_applications': 'ICJS Chain',
              'txn_jud_applications': 'Judiciary Chain', 'txn_property_applications': 'Property Chain', 'read_certificate_applications': 'Certificate Chain',
              'read_document_applications': 'Document Chain', 'read_icjs_applications': 'ICJS Chain', 'read_judiciary_applications': 'Judiciary Chain',
              'read_property_applications': 'Property Chain', 'read_cbse_applications': 'Central Board of Secondary Education', 'read_sslcpuc_applications': 'SSLC & PUC'}
    for key, app in APPKEY.items():
        for s in arr(key):
            parts = [x.strip() for x in s.split('$')]; org, dept, note = clean_org(parts[0]), parts[1], ''
            if key == 'read_cbse_applications': org = dept = 'Central Board of Secondary Education'; note = "Listed under 'Karnataka Examination Authority' on the dashboard (labelling quirk)."
            if key == 'read_sslcpuc_applications': org, dept = 'Karnataka', 'Karnataka School Examination and Assessment Board'
            if key.startswith('txn'): add('department', app, org, dept, 'documents', num(parts[2]), note)
            else:
                add('department', app, org, dept, 'verifications_total', num(parts[2]), note)
                add('department', app, org, dept, 'verifications_current_month', num(parts[3]), 'month-to-date on the data date')
    for s in arr('txn_applications'):
        name, v = s.rsplit(' - ', 1); name = name.strip()
        single = {'Central Board of Secondary Education': ('Central Board of Secondary Education', 'Central Board of Secondary Education'),
                  'SSLC & PUC': ('Karnataka', 'Karnataka School Examination and Assessment Board'), 'Drug logistics': ('Karnataka', 'Karnataka State Medical Supplies Corporation Ltd')}
        if name in single: add('department', name, *single[name], 'documents', num(v), 'application total (single department)')
    return out

def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    j = json.load(open(sys.argv[1], encoding='utf-8-sig'))
    dd = j['txn']['date']; d, m, y = dd.split('-'); date = f'{y}-{m}-{d}'
    retrieved = sys.argv[sys.argv.index('--retrieved') + 1] if '--retrieved' in sys.argv else datetime.date.today().isoformat()
    path = os.path.join(DATA, 'nic_snapshots.csv'); rows = list(csv.reader(open(path, encoding='utf-8'))); hdr, body = rows[0], rows[1:]
    if any(r[0] == date for r in body): sys.exit(f'Snapshot {date} is already in nic_snapshots.csv - nothing to do.')
    sid = f'NIC-{date}'
    new = rows_from_stats(j, date, sid)
    # sanity checks against the previous snapshot
    prev_date = max(r[0] for r in body)
    def plat(rs, d, m): return next((int(r[9]) for r in rs if r[0] == d and r[2] == 'platform' and r[8] == m), None)
    p_docs, n_docs = plat(body, prev_date, 'documents'), plat(new, date, 'documents')
    app_sum = sum(int(r[9]) for r in new if r[2] == 'application' and r[8] == 'documents')
    print(f'documents: {prev_date} {p_docs} -> {date} {n_docs}; application sum {app_sum}')
    if p_docs and n_docs < p_docs: print('WARNING: platform documents went DOWN since the previous snapshot - check the file.')
    if n_docs and abs(app_sum - n_docs) > 0.01 * n_docs: print('WARNING: application totals differ from the platform total by more than 1%.')
    if UNMAPPED: print('Unmapped departments (add them to DEPT_MAP if they match a project):', sorted(set(UNMAPPED)))
    with open(path, 'w', newline='', encoding='utf-8') as f: w = csv.writer(f); w.writerow(hdr); w.writerows(body + new)
    # source row
    sp = os.path.join(DATA, 'sources.csv'); S = list(csv.reader(open(sp, encoding='utf-8')))
    if not any(r[0] == sid for r in S[1:]):
        S.append([sid, 'NIC Centre of Excellence in Blockchain Technology', date, 'day', f'Blockchain platform statistics file (statistics.json; data date {dd})',
                  'National Informatics Centre, MeitY', 'https://blockchain.gov.in/Statistics/statistics.json', '', 'Official', '5', retrieved, 'snapshot'])
        with open(sp, 'w', newline='', encoding='utf-8') as f: csv.writer(f).writerows(S)
    # latest_update events + status_as_of
    ep = os.path.join(DATA, 'stage_events.csv'); E = list(csv.reader(open(ep, encoding='utf-8')))
    pp = os.path.join(DATA, 'projects.csv'); PR = list(csv.reader(open(pp, encoding='utf-8'))); ph = PR[0]
    links = os.path.join(DATA, 'project_sources.csv'); L = list(csv.reader(open(links, encoding='utf-8')))
    units = {}
    for r in new:
        if r[2] == 'department' and r[8] == 'documents' and r[7]: units.setdefault(r[7], []).append(f'{r[5]}: {inr(r[9])} documents')
    for pid, txt in units.items():
        k = sum(1 for e in E[1:] if e[1] == pid) + 1
        while any(e[0] == f'{pid}-E{k:02d}' for e in E): k += 1
        E.append([f'{pid}-E{k:02d}', pid, 'latest_update', date, 'day', sid, f'NIC statistics file (data date {date}) lists {"; ".join(txt)}.', 'Derived from official NIC snapshot', retrieved])
        for r in PR[1:]:
            if r[0] == pid and r[ph.index('status_as_of')] < date: r[ph.index('status_as_of')] = date
        if not any(x[0] == pid and x[1] == sid for x in L[1:]): L.append([pid, sid, 'event evidence'])
    for p_, rows_ in ((ep, E), (pp, PR), (links, L)):
        with open(p_, 'w', newline='', encoding='utf-8') as f: csv.writer(f).writerows(rows_)
    ch = os.path.join(DATA, 'changelog.csv'); C = list(csv.reader(open(ch, encoding='utf-8')))
    ver = C[-1][0] if len(C) > 1 else ''
    C.append([ver, retrieved, 'snapshot added', 'nic_snapshots', f'NIC platform snapshot for {date} ({len(new)} rows; {len(units)} projects updated).', sid])
    with open(ch, 'w', newline='', encoding='utf-8') as f: csv.writer(f).writerows(C)
    print(f'added {len(new)} snapshot rows and {len(units)} latest_update events for {date}. Now run: python3 tools/build.py')

if __name__ == '__main__': main()
