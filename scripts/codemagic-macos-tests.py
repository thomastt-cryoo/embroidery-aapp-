"""Codemagic native installation/GUI evidence, separate from browser regression.

No permission prompts are approved, no TCC database is edited, no quarantine is
removed, and Gatekeeper is never disabled. Missing GUI access is a failed/blocked
test, never a passing native test. Runs only inside the disposable Mac checkout.
"""
import hashlib
import json
import os
from pathlib import Path
import plistlib
import platform
import signal
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'out'
EVIDENCE = OUT / 'evidence'
STAGES = EVIDENCE / 'test-stages.json'


def read_json(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def main():
    assert sys.platform == 'darwin', 'Actual macOS is required'
    assert Path(os.environ['CM_BUILD_DIR']).resolve() == ROOT, 'Disposable Codemagic checkout required'
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    stages = []
    verify_only = os.environ.get('M3_VERIFY_ONLY') == '1'

    def record(name, status, detail):
        stages.append({'name': name, 'status': status, 'detail': detail})
        STAGES.write_text(json.dumps(stages, indent=2) + '\n')

    def run(args, log, timeout=360, env=None):
        with (EVIDENCE / log).open('w') as f:
            process = subprocess.Popen(list(map(str, args)), cwd=ROOT, stdout=f,
                                       stderr=subprocess.STDOUT, env=env, start_new_session=True)
            try:
                code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                raise RuntimeError(f'Time limit reached; see {log}')
        if code:
            raise RuntimeError(f'Command exited {code}; see {log}')

    def stage(name, operation):
        try:
            detail = operation()
            record(name, 'pass', detail)
            return True
        except Exception as exc:
            record(name, 'failed', f'{type(exc).__name__}: {exc}')
            print(name, stages[-1]['detail'], flush=True)
            return False

    permissions = {}

    def probe():
        run(['swift', ROOT / 'scripts/m3-macos-permissions.swift'], 'mac-permissions.json', 90)
        permissions.update(read_json(EVIDENCE / 'mac-permissions.json'))
        return permissions

    stage('Desktop permission probe (read-only)', probe)
    can_capture = bool(permissions.get('screenCaptureAuthorized') and permissions.get('displayWidth'))
    can_control = bool(can_capture and permissions.get('accessibilityTrusted'))
    package = OUT / 'Embroidery-Studio-macOS.zip'
    capture_out = OUT / '02-macOS/installation'

    def capture_installation():
        env = dict(os.environ, M3_CAPTURE_OUT=str(capture_out), M3_SOURCE_ZIP=str(package),
                   M3_SOURCE_SHA256=hashlib.sha256(package.read_bytes()).hexdigest())
        run([sys.executable, ROOT / 'scripts/m3-macos-capture.py'], 'm3-installation-capture.txt', 360, env)
        result = read_json(capture_out / 'capture-results.json', {})
        if result.get('status') != 'installer-pages-complete' or not result.get('installedAppPresent'):
            raise RuntimeError(result.get('stopReason') or result.get('error') or 'Installer walkthrough incomplete')
        return 'Native GUI installer pages captured on CI; not clean consumer Gatekeeper approval'

    if can_control:
        stage('M3 GUI installation walkthrough', capture_installation)
    else:
        record('M3 GUI installation walkthrough', 'blocked',
               'Desktop capture/accessibility access is missing. No permissions changed; no screenshots invented.')

    def install_ci():
        # These are ordinary CI privileges, expressly separate from the GUI
        # walkthrough above. This is never evidence of consumer approval steps.
        extracted = Path(os.environ['RUNNER_TEMP']) / 'codemagic-customer-extracted'
        extracted.mkdir(exist_ok=True)
        with zipfile.ZipFile(package) as z:
            assert z.testzip() is None
            for item in z.infolist():
                assert (extracted / item.filename).resolve().is_relative_to(extracted.resolve())
            z.extractall(extracted)
        pkgs = list(extracted.glob('*.pkg'))
        assert len(pkgs) == 1, 'Expected one complete PKG'
        # Close only the Installer process opened by this runner's walkthrough.
        if can_control:
            subprocess.run(['pkill', '-x', 'Installer'], check=False, capture_output=True)
        run(['sudo', '-n', 'installer', '-pkg', pkgs[0], '-target', '/'], 'ci-package-install.txt', 240)
        app = Path('/Applications/Embroidery Studio.app')
        run(['codesign', '--verify', '--deep', '--strict', '--all-architectures', app], 'ci-codesign.txt')
        info = plistlib.loads((app / 'Contents/Info.plist').read_bytes())
        assert info['CFBundleIdentifier'] == 'io.github.thomasttcryoo.embroiderystudio'
        arches = subprocess.check_output(['lipo', '-archs', app / 'Contents/MacOS' / info['CFBundleExecutable']], text=True)
        assert {'arm64', 'x86_64'} <= set(arches.split()), arches
        built = ROOT / 'app/src-tauri/target/universal-apple-darwin/release/bundle/macos/Embroidery Studio.app'

        def manifest(folder):
            return {str(p.relative_to(folder)): (str(p.readlink()) if p.is_symlink() else
                    hashlib.sha256(p.read_bytes()).hexdigest(), p.lstat().st_mode & 0o7777)
                    for p in folder.rglob('*') if p.is_symlink() or p.is_file()}

        if verify_only:
            # Compare to the exact application manifest verified by Apple's
            # native PKG reader in the original successful build, no rebuild.
            sealed = read_json(EVIDENCE / 'mac-lossless-pkg-compression.json')
            expected = {item['path']: (item.get('link', item.get('sha256')), item['mode'])
                        for item in sealed['nativeAppManifest']}
            assert manifest(app) == expected, 'Installed content differs from the sealed original package'
        else:
            assert manifest(app) == manifest(built), 'Installed content differs from the built universal app'
        result = {'result': 'pass', 'zipSha256': hashlib.sha256(package.read_bytes()).hexdigest(),
                  'binaryArchitectures': arches.strip(), 'allInstalledFilesAndModesMatchBuild': True,
                  'method': 'sudo -n installer on disposable CI; not a customer Gatekeeper test',
                  'signature': 'ad-hoc, not Developer ID/notarized', 'securitySettingsChanged': False}
        (EVIDENCE / 'ci-install-results.json').write_text(json.dumps(result, indent=2) + '\n')
        return result

    installed = stage('Ordinary CI installation from the actual customer ZIP', install_ci)

    def native_ui():
        env = dict(os.environ, M2_MAC_DELIVERY_DIR=str(OUT),
                   M3_SCREENSHOT_DIR=str(OUT / '02-macOS/functional/originals'))
        run([sys.executable, ROOT / 'scripts/m2-macos-native-ui.py'], 'native-ui.txt', 480, env)
        result = read_json(EVIDENCE / 'native-ui/results.json', {})
        assert result.get('result') == 'pass', result.get('error')
        return {'passed': len(result['checks']), 'checks': result['checks'], 'architectureTested': platform.machine()}

    if installed and can_control:
        stage('Installed native app functional tests', native_ui)
    else:
        record('Installed native app functional tests', 'blocked',
               'Installation or desktop permissions unavailable; browser results cannot substitute for native results.')

    def browser_tests():
        run(['pnpm', '--filter', 'editor', 'exec', 'playwright-core', 'install', 'chromium'], 'chromium-setup.txt', 240)
        env = dict(os.environ, LILO_PRODUCTION='1', LILO_URL='http://127.0.0.1:4173',
                   LILO_EVIDENCE_OUT=str(EVIDENCE / 'browser-acceptance'))
        with (EVIDENCE / 'browser-server.txt').open('w') as f:
            server = subprocess.Popen([sys.executable, '-m', 'http.server', '4173', '--bind', '127.0.0.1',
                                       '--directory', str(ROOT / 'editor/dist')], stdout=f, stderr=f)
            try:
                time.sleep(1)
                assert server.poll() is None, 'Local browser server did not start'
                run(['node', ROOT / 'scripts/m2-ui-check.mjs'], 'browser-tests.txt', 600, env)
            finally:
                server.terminate()
                server.wait(timeout=10)
        result = read_json(EVIDENCE / 'browser-acceptance/results.json', {})
        assert not result.get('failure') and not result.get('problems'), result
        assert len(result.get('exports', [])) == 13 and result.get('externalNetworkBlocked')
        return 'Production frontend: real engine, 13 exports, save/reopen, simulation and offline regression; not native UI'

    if not verify_only:
        stage('Separate production browser regression', browser_tests)
    return 0 if all(s['status'] == 'pass' for s in stages) else 1


if __name__ == '__main__':
    sys.exit(main())
