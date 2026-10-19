"""Native macOS runner smoke check. Separate from browser conversion acceptance."""
import hashlib, json, os, pathlib, platform, plistlib, subprocess, sys, time, urllib.request

app = pathlib.Path(sys.argv[1]).resolve()
out = pathlib.Path(sys.argv[2]).resolve()
out.mkdir(parents=True, exist_ok=True)
with (app/'Contents/Info.plist').open('rb') as f:
    info = plistlib.load(f)
assert info['CFBundleIdentifier'] == 'io.github.thomasttcryoo.embroiderystudio', info
assert info['CFBundleName'] == 'Embroidery Studio', info
binary = app/'Contents/MacOS'/info['CFBundleExecutable']
arches = subprocess.check_output(['lipo', '-archs', str(binary)], text=True).strip()
assert 'arm64' in arches and 'x86_64' in arches, arches
assert not any(app.rglob('node_modules'))
assert not any(app.rglob('.git'))
assert not any(app.rglob('*.map'))
sample = pathlib.Path('reports/M1/evidence/acceptance/exports/k-logo.lilo').resolve()
subprocess.run(['open', '-na', str(app), '--args', str(sample)], check=True)
health = None
for _ in range(60):
    try:
        health = json.load(urllib.request.urlopen('http://127.0.0.1:17842/api/health', timeout=2))
        if health.get('app') == 'embroidery-studio': break
    except Exception:
        pass
    time.sleep(1)
assert health and health.get('app') == 'embroidery-studio', health
time.sleep(12)
subprocess.run(['screencapture', '-x', str(out/'native-macos-desktop.png')], check=True)
subprocess.run(['codesign', '--verify', '--deep', '--strict', str(app)], check=True)
result = {'os': platform.platform(), 'architecture': platform.machine(), 'appIdentifier': info['CFBundleIdentifier'], 'version': info['CFBundleShortVersionString'], 'binaryArchitectures': arches, 'nativeLaunch': 'pass', 'health': health, 'nativeScreenshot': 'native-macos-desktop.png', 'sampleOpenRequested': str(sample.name), 'signature': 'ad-hoc; not Developer ID or notarized', 'scope': 'Native application launched on actual macOS; health and package identity checked. Inspect screenshot for rendered sample. Detailed conversion/edit/export acceptance runs separately in Chromium on this same macOS runner.'}
(out/'native-macos-results.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
