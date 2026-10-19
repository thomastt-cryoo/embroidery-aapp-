"""Verify real native rendering from the delivered ZIP without adding app test hooks."""
import json, os, pathlib, re, subprocess, tempfile

root=pathlib.Path(__file__).resolve().parent.parent
received=pathlib.Path('received').resolve()
out=received/'evidence'
subprocess.run(['python3',str(root/'scripts/m2-macos-etsy.py'),'install','--out',str(received)],check=True)
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
