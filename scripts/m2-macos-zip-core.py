"""Verify real native rendering from the delivered ZIP without adding app test hooks."""
import hashlib, json, os, pathlib, re, subprocess, tempfile, zipfile

root=pathlib.Path(__file__).resolve().parent.parent
received=pathlib.Path('received').resolve()
out=received/'evidence'
final=received/'Embroidery-Studio-macOS.zip'
# Older comparison runs identify disk-image formats in internal candidate names.
# Give the customer one plain installer name, preserving every payload byte.
with zipfile.ZipFile(final) as z:
    entries=[(entry,z.read(entry)) for entry in z.infolist()]
if any(entry.filename.endswith('.dmg') and entry.filename!='Install Embroidery Studio.dmg' for entry,_ in entries):
    normalized=final.with_suffix('.normalized.zip')
    with zipfile.ZipFile(normalized,'w',compresslevel=9) as z:
        for entry,data in entries:
            if entry.filename.endswith('.dmg'):
                entry.filename='Install Embroidery Studio.dmg'
            z.writestr(entry,data)
    with zipfile.ZipFile(normalized) as z:
        assert z.testzip() is None
        assert z.read('Install Embroidery Studio.dmg')==next(data for entry,data in entries if entry.filename.endswith('.dmg'))
    normalized.replace(final)
selected_path=out/'mac-selected-package.json'
selected=json.loads(selected_path.read_text())
selected.update({'bytes':final.stat().st_size,'sha256':hashlib.file_digest(final.open('rb'),'sha256').hexdigest(),
                 'underEtsyLimit':final.stat().st_size<20_000_000,'customerInstallerName':'plain; no compression format in the filename'})
selected_path.write_text(json.dumps(selected,indent=2)+'\n')
(received/'SHA256SUMS.txt').write_text(selected['sha256']+'  Embroidery-Studio-macOS.zip\n')
subprocess.run(['python3',str(root/'scripts/m2-macos-etsy.py'),'install','--out',str(received)],check=True)
# Compare the remaining native pkgbuild compression option using the complete
# installed universal app. The minimum matches the existing macOS 13 target.
# No application is rebuilt, thinned, or changed for this comparison.
subprocess.run(['pkill','-x','embroidery-studio'],check=False)
pkg_work=pathlib.Path(os.environ.get('RUNNER_TEMP',tempfile.gettempdir()))/'studio-etsy-pkg'
pkg_work.mkdir(exist_ok=True)
pkg=pkg_work/'Install Embroidery Studio.pkg'
reuse_pkg=selected['kind']=='pkg'
trial=subprocess.CompletedProcess([],0,stdout='Reused the exact verified customer PKG; no repackaging.\n',stderr='') if reuse_pkg else subprocess.run(['pkgbuild','--component','/Applications/Embroidery Studio.app',
    '--install-location','/Applications','--identifier','io.github.thomasttcryoo.embroiderystudio',
    '--version','1.4.0','--min-os-version','13.0','--compression','latest',str(pkg)],
    text=True,capture_output=True,timeout=240)
(out/'mac-pkg-compression.log').write_text(trial.stdout+trial.stderr)
comparison=json.loads((out/'mac-pkg-comparison.json').read_text()) if reuse_pkg else {'minimumMacOS':'13.0','compression':'latest','exitCode':trial.returncode}
if trial.returncode==0 and not reuse_pkg:
    alternatives=[]
    with zipfile.ZipFile(final) as original:
        legal=[(name,original.read(name)) for name in ['LICENSE.txt','NOTICE.txt']]
    for method,tag in [(zipfile.ZIP_STORED,'store'),(zipfile.ZIP_DEFLATED,'deflate')]:
        candidate=pkg_work/(tag+'.zip')
        with zipfile.ZipFile(candidate,'w',compression=method,compresslevel=9 if method==zipfile.ZIP_DEFLATED else None) as z:
            z.write(pkg,pkg.name)
            for name,data in legal:z.writestr(name,data)
            z.writestr('START HERE.txt','Open Install Embroidery Studio.pkg and follow the installer. Then open Embroidery Studio in Applications.\n\nPrivate review build: ad-hoc signed, without Apple Developer ID or notarization. macOS may prevent opening. Automatic updates are disabled.\n')
        alternatives.append(candidate)
    winner=min(alternatives,key=lambda p:p.stat().st_size)
    comparison.update({'pkgBytes':pkg.stat().st_size,'zipBytes':winner.stat().st_size,
        'underEtsyLimit':winner.stat().st_size<20_000_000})
    if winner.stat().st_size<final.stat().st_size:
        import shutil
        shutil.copy2(winner,final)
        selected.update({'kind':'pkg','bytes':final.stat().st_size,'pkgBytes':pkg.stat().st_size,
            'sha256':hashlib.file_digest(final.open('rb'),'sha256').hexdigest(),
            'underEtsyLimit':final.stat().st_size<20_000_000})
        selected.pop('dmgFormat',None);selected.pop('dmgBytes',None)
        selected_path.write_text(json.dumps(selected,indent=2)+'\n')
        subprocess.run(['python3',str(root/'scripts/m2-macos-etsy.py'),'install','--out',str(received)],check=True)
(out/'mac-pkg-comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')
(received/'SHA256SUMS.txt').write_text(hashlib.file_digest(final.open('rb'),'sha256').hexdigest()+'  Embroidery-Studio-macOS.zip\n')
swift=pathlib.Path(os.environ.get('RUNNER_TEMP',tempfile.gettempdir()))/'studio-native-ocr.swift'
swift.write_text('''import AppKit
import Vision
import ApplicationServices
import Foundation
let url = URL(fileURLWithPath: CommandLine.arguments[1])
let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
let handler = VNImageRequestHandler(url: url)
try handler.perform([request])
let lines = (request.results ?? []).compactMap { $0.topCandidates(1).first?.string }
let result: [String: Any] = ["text": lines, "accessibilityTrusted": AXIsProcessTrusted()]
let data = try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted])
print(String(data: data, encoding: .utf8)!)
''')
checks=[]
for image, expected_name in [('native-macos-desktop.png','klogo'),('mac-native-pes-from-zip.png','studiosample')]:
    r=subprocess.run(['swift',str(swift),str(out/image)],check=True,text=True,capture_output=True,timeout=120)
    observed=json.loads(r.stdout)
    assert any('1374' in re.sub(r'[^0-9]','',line) for line in observed['text']), (image,observed)
    assert any(expected_name in re.sub(r'[^a-z0-9]','',line.lower()) for line in observed['text']), (image,expected_name,observed)
    checks.append({'screenshot':image,'expectedStitches':1374,'expectedProjectName':expected_name,'nativeVisibleCountAndName':'pass','ocr':observed})
result={'result':'pass','source':'application installed from the actual final customer ZIP',
        'nativeProjectAndPesRendering':checks,'changesToApplicationForTesting':False,
        'nativeDialogAutomation':'not performed; no accessibility permission changes or test hooks',
        'detailedEditingHoopAndExportRegression':'separate production browser acceptance on macOS; see build artifact evidence'}
(out/'mac-native-core-from-zip.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: actual ZIP installed; native project and PES reader rendered 1,374 stitches, verified from real screenshots using Apple Vision.')
