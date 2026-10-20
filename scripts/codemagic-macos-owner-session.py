"""Create an owner-launched Terminal test and wait, without rebuilding the app."""
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'out'
EXPECTED = 'cf594cb3c34373aee45a150aca7cb2f9326fff9c19fa41fe5a4f4bdd2012b426'


def main():
    assert sys.platform == 'darwin' and Path(os.environ['CM_BUILD_DIR']).resolve() == ROOT
    evidence = OUT / 'evidence'
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / 'run-mode.json').write_text(json.dumps({
        'mode': 'verification-only', 'maximumMinutes': 20, 'applicationRebuilt': False,
        'sourceBuild': '6ad6d5e57550aed810905b59', 'sourceZipSha256': EXPECTED,
        'nativeRustTests': '96 passed in source build; not rerun here',
        'browserRegression': 'passed in source build; not rerun here',
    }, indent=2) + '\n')
    # The archive lives on a dedicated branch in the same private repository,
    # outside main and customer packages. No public download/token is needed.
    subprocess.run(['git', 'fetch', '--depth=1', 'origin', 'refs/heads/codex/m3-macos-verification-package'], check=True)
    with (OUT / 'Embroidery-Studio-macOS.zip').open('wb') as archive:
        subprocess.run(['git', 'show', 'FETCH_HEAD:Embroidery-Studio-macOS.zip'], stdout=archive, check=True)
    assert hashlib.sha256((OUT / 'Embroidery-Studio-macOS.zip').read_bytes()).hexdigest() == EXPECTED
    source = ROOT / 'reports/M3/codemagic-setup/run-2/evidence'
    for name in ['mac-selected-package.json', 'mac-lossless-pkg-compression.json']:
        (evidence / name).write_bytes((source / name).read_bytes())
    subprocess.run([sys.executable, ROOT / 'scripts/codemagic-macos-report.py', '--check-package'], check=True)
    desktop = Path.home() / 'Desktop'
    desktop.mkdir(exist_ok=True)
    launcher = desktop / 'START MAC SCREENSHOT TEST.command'
    launcher.write_text('#!/bin/bash\nexport CM_BUILD_DIR=' + shlex.quote(str(ROOT)) +
                        '\ncd "$CM_BUILD_DIR"\nbash scripts/codemagic-macos-verify-terminal.sh\n')
    launcher.chmod(0o755)
    (desktop / 'READ ME FIRST.txt').write_text(
        'Double-click START MAC SCREENSHOT TEST.command.\n'
        'In macOS Privacy & Security, approve Accessibility and Screen Recording for the requesting test host (normally Terminal).\n'
        'Only you approve these permissions. No Gatekeeper or other security protection is disabled.\n'
        'If macOS asks to quit/reopen Terminal, do that and double-click the launcher again.\n'
        'No application rebuild takes place. The existing sealed ZIP is reused.\n'
        'Connect through VNC and start the launcher within five minutes to avoid idle usage.\n')
    print('READY: Connect using VNC. Double-click START MAC SCREENSHOT TEST.command on the Mac desktop. '
          'Approve only the requesting test host in Accessibility and Screen Recording. '
          'Waiting at most five minutes for you to start; no app compilation.', flush=True)
    started = time.monotonic()
    while time.monotonic() - started < 5 * 60:
        if (evidence / 'owner-started').exists():
            break
        time.sleep(1)
    else:
        print('Stopped to conserve minutes: no owner-started test. Desktop permissions were not changed.', flush=True)
        return 1
    while time.monotonic() - started < 18 * 60:
        result = evidence / 'owner-exit-code'
        if result.exists():
            return int(result.read_text().strip())
        time.sleep(1)
    print('Stopped: verification time limit. No additional build will start.', flush=True)
    return 1


if __name__ == '__main__':
    sys.exit(main())
