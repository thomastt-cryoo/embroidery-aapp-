"""Recover the exact already-built universal app; no compilation or UI changes."""
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import zipfile

root = Path(__file__).resolve().parent.parent
assert os.environ.get('GITHUB_ACTIONS') == 'true' and os.uname().sysname == 'Darwin'
run_id = os.environ['SOURCE_BUILD_RUN']
assert run_id.isdigit()
source = root / 'received/Embrova-macOS.zip'
work = root / 'replay'
work.mkdir()
with zipfile.ZipFile(source) as z:
    assert z.testzip() is None
    assert sorted(z.namelist()) == ['Install Embrova.pkg', 'LICENSE.txt', 'NOTICE.txt', 'START HERE.txt']
    package = work / 'source.pkg'
    package.write_bytes(z.read('Install Embrova.pkg'))
assert package.read_bytes().startswith(b'xar!')
subprocess.run(['pkgutil', '--expand-full', package, work / 'expanded'], check=True)
apps = list((work / 'expanded').rglob('Embrova.app'))
assert len(apps) == 1
app = apps[0]
info = plistlib.loads((app / 'Contents/Info.plist').read_bytes())
assert info['CFBundleName'] == 'Embrova'
assert info['CFBundleIdentifier'] == 'io.github.thomasttcryoo.embroiderystudio'
binary = app / 'Contents/MacOS' / info['CFBundleExecutable']
icon_name = info['CFBundleIconFile']
if not icon_name.endswith('.icns'):
    icon_name += '.icns'
icon = app / 'Contents/Resources' / icon_name
icon_sha = hashlib.sha256(icon.read_bytes()).hexdigest()
assert icon_sha == hashlib.sha256((root / 'app/src-tauri/icons/icon.icns').read_bytes()).hexdigest(), 'Artifact has an older or unexpected application icon'
source_environment = (root / 'received/evidence/environment.txt').read_text()
source_commits = re.findall(r'^[a-f0-9]{40}$', source_environment, re.M)
assert len(source_commits) == 1, 'Original source commit evidence is missing'
arches = subprocess.check_output(['lipo', '-archs', binary], text=True).split()
assert {'arm64', 'x86_64'} <= set(arches)
subprocess.run(['codesign', '--verify', '--deep', '--strict', '--all-architectures', app], check=True)
out = root / 'out/evidence'
out.mkdir(parents=True)
record = {'sourceBuildRun': run_id, 'sourceZipSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'applicationSourceCommit': source_commits[0], 'nativeIconSha256': icon_sha,
          'binarySha256': hashlib.sha256(binary.read_bytes()).hexdigest(), 'architectures': arches,
          'applicationRebuilt': False, 'applicationFilesModified': False,
          'originalSignature': 'verified strict, all architectures'}
(out / 'repackaging-source.json').write_text(json.dumps(record, indent=2) + '\n')
with Path(os.environ['GITHUB_ENV']).open('a') as f:
    f.write('RECOVERED_APP=' + str(app) + '\n')
