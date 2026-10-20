"""Verify the owner's exact rebuilt ZIP; never rebuild or change OS permissions."""
import hashlib
import importlib.util
import json
import platform
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'out'
EXPECTED = '3381ddb207a0e535b780752c58957c3f95d68465921022ab90d306ea54d5e33d'
spec = importlib.util.spec_from_file_location('package_report', ROOT / 'scripts/codemagic-macos-report.py')
package_report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package_report)


def prepare():
    archive = OUT / 'Embroidery-Studio-macOS.zip'
    assert hashlib.file_digest(archive.open('rb'), 'sha256').hexdigest() == EXPECTED, 'Wrong application ZIP'
    evidence = OUT / 'evidence'
    evidence.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'reports/mac-sidebar-fix/rebuild-evidence/evidence'
    for name in ['mac-selected-package.json', 'mac-lossless-pkg-compression.json']:
        shutil.copy2(source / name, evidence / name)
    package_report.validate_package(OUT)
    (evidence / 'source.json').write_text(json.dumps({
        'applicationSourceCommit': '471e1fc1a3544dda51048afcecc177844b7602f6',
        'zipSha256': EXPECTED, 'applicationRebuilt': False,
        'architecture': platform.machine(), 'system': platform.platform(),
        'noSecuritySettingsChanged': True,
    }, indent=2) + '\n')


def report():
    stages_path = OUT / 'evidence/test-stages.json'
    stages = json.loads(stages_path.read_text()) if stages_path.exists() else []
    OUT.mkdir(exist_ok=True)
    lines = ['# GitHub native Mac verification', '',
             f'Runner architecture: {platform.machine()}. Existing customer ZIP reused; no rebuild.', '',
             f'Expected ZIP SHA-256: `{EXPECTED}`', '',
             '| Stage | Result | Details |', '|---|---|---|']
    for stage in stages:
        detail = str(stage['detail']).replace('|', '/').replace('\n', ' ')
        lines.append(f"| {stage['name']} | {stage['status']} | {detail} |")
    if not stages:
        lines.append('| Preparation | incomplete | Inspect workflow logs |')
    lines += ['', 'A blocked or failed automation step is not proof of an application defect. '
              'Partial native checks are in evidence/native-ui/results.json if that test started.', '',
              'No browser/export regression was repeated. Native PES Save-dialog testing is part of '
              'the requested remaining installed-app checks.', '',
              'Consumer Gatekeeper verification remains incomplete. Command-line CI installation '
              'does not represent approval of customer security warnings. No global security, '
              'quarantine or privacy permission changes are made.', '',
              'Screenshots are actual runner screenshots when available; review before customer use. '
              'These CI logs/artifacts are accessible in this public repository.', '']
    (OUT / 'GITHUB_MACOS_RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    {'prepare': prepare, 'report': report}[sys.argv[1]]()
