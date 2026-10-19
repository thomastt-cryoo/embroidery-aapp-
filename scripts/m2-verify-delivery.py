"""Validate complete final customer ZIPs and write auditable exact-byte evidence."""
import hashlib,json,pathlib,re,zipfile
root=pathlib.Path(__file__).resolve().parent.parent
out=root/'dist/M2-Etsy';evidence=root/'reports/M2/etsy'
expected={'Embroidery-Studio-Windows.zip':'Install Embroidery Studio.exe','Embroidery-Studio-macOS.zip':'Install Embroidery Studio.pkg'}
assert {p.name for p in out.iterdir()}==set(expected),'Customer folder must contain exactly two complete ZIPs'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
records=[]
for name,installer in expected.items():
    path=out/name
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        assert set(z.namelist())=={installer,'LICENSE.txt','NOTICE.txt','START HERE.txt'}
        payload=z.read(installer)
        assert payload.startswith(b'MZ' if installer.endswith('.exe') else b'xar!')
        # Git checks out platform-native line endings; legal text must match.
        assert z.read('LICENSE.txt').decode().replace('\r\n','\n')==(root/'LICENSE').read_text(encoding='utf-8')
        assert z.read('NOTICE.txt').decode().replace('\r\n','\n')==(root/'NOTICE.md').read_text(encoding='utf-8')
        record={'file':name,'bytes':path.stat().st_size,'sha256':sha(path),
                'under20000000':path.stat().st_size<20_000_000,'installer':installer,
                'installerBytes':len(payload),'installerSha256':hashlib.sha256(payload).hexdigest(),
                'zipIntegrity':'pass','completeSingleArchive':True,'entries':z.namelist()}
        records.append(record)
win=json.loads((evidence/'windows-package.json').read_text());mac=json.loads((evidence/'macos/mac-selected-package.json').read_text())
assert records[0]['sha256']==win['zipSha256'] and records[0]['under20000000']
assert records[1]['sha256']==mac['sha256'] and records[1]['bytes']==mac['bytes']
native=json.loads((evidence/'windows-native/results.json').read_text())
assert len(native['checks'])==9 and all(c['result']=='pass' for c in native['checks'])
mac_native=json.loads((evidence/'macos-intel/native-ui/results.json').read_text())
assert mac_native['result']=='partial'
assert sum(c['result']=='pass' for c in mac_native['checks'])==5
assert any(c['name']=='native canvas preview' and c['result']=='blocked' for c in mac_native['checks'])
graphics=json.loads((evidence/'graphics-probe/native-webkit-graphics.json').read_text())
assert graphics['appCodeLoaded'] is False
assert len(graphics['webgl']['observations'])==4 and all(c['contextLostBefore'] for c in graphics['webgl']['observations'])
assets=json.loads((evidence/'asset-preservation.json').read_text())
assert assets['fileCount']==458 and assets['allPreviewPixelsAndColourProfilesIdentical'] and assets['allOtherRuntimeFilesByteIdentical']
windows_build=(evidence/'windows-build.txt').read_text(encoding='utf-8-sig')
assert 'Finished 1 bundle' in windows_build
tests=(evidence/'windows-native-tests.txt').read_text(encoding='utf-8-sig')
counts=re.findall(r'test result: ok\. (\d+) passed; 0 failed',tests)
assert counts==['92','18'],counts
summary={'windowsNativeTests':[int(x) for x in counts],'windowsNativeWorkflowChecks':9,
         'runtimeFiles':458,'releaseBuild':'pass','webview':'downloadBootstrapper; absent-runtime branch not clean-VM tested',
         'engineAndApprovedInterface':'unchanged; source guard recorded separately'}
(evidence/'windows-build-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(evidence/'delivery-manifest.json').write_text(json.dumps({'decimalByteLimit':20_000_000,'packages':records,
    'macSizeLimitation':not records[1]['under20000000'],'macNativeFunctionalPasses':5,
    'macNativePreview':'blocked on hosted VM; independently reproduced outside the application',
    'signingPending':True,'published':False},indent=2)+'\n')
(evidence/'SHA256SUMS.txt').write_text(''.join(r['sha256']+'  '+r['file']+'\n' for r in records))
print(json.dumps(records,indent=2))
