"""Install the rebuilt ZIP and capture native menu-bar branding; no GUI approvals."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'out'
EVIDENCE = OUT / 'evidence'
app = Path('/Applications/Embroidery Studio.app')
assert os.environ.get('GITHUB_ACTIONS') == 'true'
assert os.uname().sysname == 'Darwin'
package = OUT / 'installers/Install Embroidery Studio.pkg'
subprocess.run(['sudo', '-n', 'installer', '-pkg', package, '-target', '/'], check=True)
subprocess.run(['codesign', '--verify', '--deep', '--strict', '--all-architectures', app], check=True)
sealed = json.loads((EVIDENCE / 'mac-lossless-pkg-compression.json').read_text())
expected = {p['path']: (p.get('link', p.get('sha256')), p['mode']) for p in sealed['nativeAppManifest']}
actual = {str(p.relative_to(app)): (str(p.readlink()) if p.is_symlink() else hashlib.sha256(p.read_bytes()).hexdigest(), p.lstat().st_mode & 0o7777)
          for p in app.rglob('*') if p.is_symlink() or p.is_file()}
assert actual == expected, 'Installed app does not match the sealed package'
subprocess.run(['open', '-a', app], check=True)
time.sleep(12)
subprocess.run(['screencapture', '-x', EVIDENCE / 'native-menu-bar-branding.png'], check=True)
result = {'ciInstallation': 'pass', 'installedManifest': 'matches sealed build',
          'sourceTrayPngSha256': hashlib.sha256((ROOT / 'app/src-tauri/icons/tray-mono.png').read_bytes()).hexdigest(),
          'screenshot': 'native-menu-bar-branding.png', 'visualReview': 'pending owner/agent inspection',
          'securitySettingsChanged': False, 'functionalTestsRepeated': False,
          'consumerGatekeeperTested': False}
(EVIDENCE / 'native-branding-check.json').write_text(json.dumps(result, indent=2) + '\n')
(OUT / 'MACOS_BRANDING_REPORT.md').write_text(
    '# Mac menu-bar branding package\n\n'
    'The Lilo flower template asset was replaced by the monochrome Embroidery Studio hoop. '
    'Only branding assets changed in the application.\n\n'
    'The rebuilt ZIP passed the strict size gate. Command-line installation, all installed files/modes '
    'and strict universal signature verification passed. Actual Mac menu-bar screenshot: '
    'evidence/native-menu-bar-branding.png; visual review pending.\n\n'
    'The eight native functional checks on ARM and Intel passed for the previous ZIP, before this '
    'branding-only change; they were not repeated here. Clean consumer Gatekeeper and the full '
    'installer authentication walkthrough remain incomplete. Signing is still ad-hoc.\n', encoding='utf-8')
