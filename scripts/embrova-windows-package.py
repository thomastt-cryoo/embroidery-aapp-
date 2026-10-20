"""Package the complete branded installer; preserve historical delivery ZIPs."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent.parent
evidence = ROOT / 'reports/embrova-branding'
evidence.mkdir(exist_ok=True)
source = ROOT / 'app/src-tauri/target/release/bundle/nsis/Embrova_1.4.0_x64-setup.exe'
nsis = (ROOT / 'app/src-tauri/target/release/nsis/x64/installer.nsi').read_text(encoding='utf-8-sig')
assert '!define INSTALLWEBVIEW2MODE "downloadBootstrapper"' in nsis
assert '!define WEBVIEW2INSTALLERPATH ""' in nsis
assets = json.loads((ROOT / 'reports/M2/etsy/asset-preservation.json').read_text())
assert assets['allPreviewPixelsAndColourProfilesIdentical'] and assets['allOtherRuntimeFilesByteIdentical']
out = ROOT / 'dist/Embrova'
out.mkdir(exist_ok=True)
archive = out / 'Embrova-Windows.zip'
pending = evidence / 'windows-package.pending'
with zipfile.ZipFile(pending, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    z.write(source, 'Install Embrova.exe')
    z.writestr('START HERE.txt', 'Extract this ZIP, open Install Embrova.exe, and follow the installer.\n\n'
                'The complete application is included. If Microsoft WebView2 is missing, the installer '
                'downloads that Microsoft runtime. The application works offline after installation.\n\n'
                'Embrova installs separately from the original Lilo app and supports compatible .lilo projects. '
                'Automatic updates are disabled. This installer is unsigned.\n')
    z.write(ROOT / 'LICENSE', 'LICENSE.txt')
    z.write(ROOT / 'NOTICE.md', 'NOTICE.txt')
with zipfile.ZipFile(pending) as z:
    assert z.testzip() is None
    assert sorted(z.namelist()) == ['Install Embrova.exe', 'LICENSE.txt', 'NOTICE.txt', 'START HERE.txt']
    assert hashlib.sha256(z.read('Install Embrova.exe')).hexdigest() == hashlib.sha256(source.read_bytes()).hexdigest()
assert pending.stat().st_size < 20_000_000, 'Complete installer exceeds Etsy limit; no parts or runtime assets removed'
pending.replace(archive)
result = {'zipBytes': archive.stat().st_size, 'limitBytes': 20_000_000,
          'zipSha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
          'installerBytes': source.stat().st_size, 'zipIntegrity': 'pass',
          'installerReadback': 'pass', 'underLimit': archive.stat().st_size < 20_000_000,
          'webviewMode': 'downloadBootstrapper', 'runtimeAssets': assets['fileCount']}
(evidence / 'windows-package.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
assert result['underLimit'], 'Complete installer exceeds Etsy limit; no parts or runtime assets removed'
