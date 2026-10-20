"""Package the verified Windows UI fix without replacing the approved M2 ZIPs."""
from pathlib import Path
import hashlib, json, zipfile

root = Path(__file__).resolve().parent.parent
evidence = root / 'reports/windows-ui-fix'
assert 'Finished 1 bundle' in (evidence / 'windows-build.txt').read_text(encoding='utf-8-sig')
source = root / 'app/src-tauri/target/release/bundle/nsis/Embroidery Studio_1.4.0_x64-setup.exe'
nsis = (root / 'app/src-tauri/target/release/nsis/x64/installer.nsi').read_text(encoding='utf-8-sig')
assert '!define INSTALLWEBVIEW2MODE "downloadBootstrapper"' in nsis
assets = json.loads((evidence / 'asset-preservation.json').read_text())
assert assets['allPreviewPixelsAndColourProfilesIdentical'] and assets['allOtherRuntimeFilesByteIdentical']
out = root / 'dist/Windows-UI-Fix'
out.mkdir(parents=True, exist_ok=True)
package = out / 'Embroidery-Studio-Windows.zip'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    z.write(source, 'Install Embroidery Studio.exe')
    z.writestr('START HERE.txt', 'Extract this ZIP, then open Install Embroidery Studio.exe.\n\nThis Windows update fixes the Sew order panel. Click the Stitches heading to expand or collapse it. Layer options & help contains the advanced layer tools.\n\nThis installs as Embroidery Studio separately from Lilo. Existing compatible projects are supported. The complete application is included and works offline after installation. If Microsoft WebView2 is missing, the installer downloads that Microsoft runtime. Automatic updates are disabled. This private review installer is unsigned.\n')
    z.write(root / 'LICENSE', 'LICENSE.txt')
    z.write(root / 'NOTICE.md', 'NOTICE.txt')
extracted = out / 'extracted-for-testing'
extracted.mkdir(exist_ok=True)
with zipfile.ZipFile(package) as z:
    assert z.testzip() is None
    assert sorted(z.namelist()) == ['Install Embroidery Studio.exe', 'LICENSE.txt', 'NOTICE.txt', 'START HERE.txt']
    z.extractall(extracted)
assert sha(extracted / 'Install Embroidery Studio.exe') == sha(source)
assert package.stat().st_size < 20_000_000
result = dict(zip=str(package), zipBytes=package.stat().st_size, zipSha256=sha(package),
              installerBytes=source.stat().st_size, installerSha256=sha(source),
              extractedInstaller=str(extracted / 'Install Embroidery Studio.exe'),
              zipIntegrity='pass', exactInstallerReadback='pass', limitBytes=20_000_000,
              assetsRetained=assets['fileCount'], webviewMode='downloadBootstrapper')
(evidence / 'package.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
