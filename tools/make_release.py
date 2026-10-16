"""Build the release archive for Zenodo from this repository.

    python3 tools/make_release.py            # writes dataset/India_Govt_Blockchain_Dataset_v<version>.zip
    python3 tools/make_release.py --force    # rebuild even if that version's zip already exists

Run it after tools/build.py and tools/make_workbook.py. The version comes from tools/package_meta.json.
A version that is already deposited on Zenodo should not be rebuilt: bump the version first.
The archive holds everything needed to use and rebuild the dataset offline (README.md in the archive is README_DATASET.md here).
"""
import glob, json, os, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META = json.load(open(os.path.join(ROOT, 'tools', 'package_meta.json'), encoding='utf-8'))
VER = META['version']
OUT_DIR = os.path.join(ROOT, 'dataset'); os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, f'India_Govt_Blockchain_Dataset_v{VER}.zip')
XLSX = f'India_Govt_Blockchain_Database_v{VER.rsplit(".", 1)[0]}.xlsx'

if os.path.exists(OUT) and '--force' not in sys.argv:
    sys.exit(f'{os.path.relpath(OUT, ROOT)} already exists. Bump "version" in tools/package_meta.json for a new release, or pass --force.')

FILES = {  # path in archive: path in repository
    'README.md': 'README_DATASET.md', 'METHODS.md': 'METHODS.md', 'UPDATE_GUIDE.md': 'UPDATE_GUIDE.md',
    'ZENODO_UPLOAD_GUIDE.md': 'ZENODO_UPLOAD_GUIDE.md', 'CITATION.cff': 'CITATION.cff', 'LICENSE.txt': 'LICENSE.txt',
    'datapackage.json': 'datapackage.json', XLSX: XLSX, 'geo/india_states.json': 'geo/india_states.json'}
for pattern in ['data/*.csv', 'derived/*', 'raw/nic/*.json', 'tools/*.py', 'tools/package_meta.json']:
    for p in sorted(glob.glob(os.path.join(ROOT, pattern))):
        rel = os.path.relpath(p, ROOT).replace(os.sep, '/'); FILES[rel] = rel

missing = [src for src in FILES.values() if not os.path.exists(os.path.join(ROOT, src))]
if missing: sys.exit('Missing files (run tools/build.py and tools/make_workbook.py first): ' + ', '.join(missing))

html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
note = '<!-- Offline copy: run `python3 -m http.server` in this folder and open http://localhost:8000/dashboard.html -->\n'
html = html.replace('<body>\n', '<body>\n' + note, 1) if '<body>\n' in html else note + html

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    for arc, src in sorted(FILES.items()):
        z.write(os.path.join(ROOT, src), arc)
    z.writestr('dashboard.html', html)
print(f'release: {os.path.relpath(OUT, ROOT)} ({len(FILES) + 1} files, {os.path.getsize(OUT) / 1024:.0f} kB)')
