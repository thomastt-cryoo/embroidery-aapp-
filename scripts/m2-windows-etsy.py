"""Create one standard ZIP containing the complete native Windows installer."""
from pathlib import Path
import hashlib, json, shutil, zipfile

root=Path(__file__).resolve().parent.parent
source=root/'app/src-tauri/target/release/bundle/nsis/Embrova_1.4.0_x64-setup.exe'
evidence=root/'reports/M2/etsy'
assert 'Finished 1 bundle' in (evidence/'windows-build.txt').read_text(encoding='utf-8-sig'), 'Final build has not completed'
nsis=(root/'app/src-tauri/target/release/nsis/x64/installer.nsi').read_text(encoding='utf-8-sig')
assert '!define INSTALLWEBVIEW2MODE "downloadBootstrapper"' in nsis
assert '!define WEBVIEW2INSTALLERPATH ""' in nsis
assets=json.loads((evidence/'asset-preservation.json').read_text())
assert assets['allPreviewPixelsAndColourProfilesIdentical'] and assets['allOtherRuntimeFilesByteIdentical']
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
out=root/'dist/M2-Etsy';out.mkdir(exist_ok=True)
final=out/'Embrova-Windows.zip'
with zipfile.ZipFile(final,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    z.write(source,'Install Embrova.exe')
    z.writestr('START HERE.txt','Extract this ZIP, then open Install Embrova.exe and follow the installer.\n\nIf Microsoft WebView2 is missing, the standard installer downloads it from Microsoft; this step needs internet access. The complete application is included and works offline after installation.\n\nYour existing Lilo application and file defaults are preserved. Embrova uses its own shortcut and Documents/Embrova folder. Automatic updates are disabled. This private review installer is unsigned.\n')
    z.write(root/'LICENSE','LICENSE.txt')
    z.write(root/'NOTICE.md','NOTICE.txt')
extracted=root/'reports/M2/build-artifacts'/('windows-zip-'+sha(final)[:12])
extracted.mkdir(exist_ok=True)
with zipfile.ZipFile(final) as z:
    assert z.testzip() is None
    assert sorted(z.namelist())==['Install Embrova.exe','LICENSE.txt','NOTICE.txt','START HERE.txt']
    z.extractall(extracted)
assert sha(extracted/'Install Embrova.exe')==sha(source)
result={'zip':str(final),'zipBytes':final.stat().st_size,'limitBytes':20_000_000,'underLimit':final.stat().st_size<20_000_000,
        'zipSha256':sha(final),'installerBytes':source.stat().st_size,'installerSha256':sha(source),
        'extractedInstaller':str(extracted/'Install Embrova.exe'),'zipIntegrity':'pass','exactInstallerReadback':'pass',
        'webviewMode':'downloadBootstrapper','embeddedOfflineWebviewInstaller':False,
        'runtimeAssetsRetained':assets['fileCount'],'pngPixelsAndProfilesPreserved':True,
        'allOtherRuntimeAssetBytesPreserved':True,'applicationComponentDownloads':False}
(evidence/'windows-package.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
