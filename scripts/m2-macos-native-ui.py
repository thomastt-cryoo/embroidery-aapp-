"""Native macOS ZIP regression through existing, already-authorized accessibility."""
import hashlib,json,os,pathlib,shutil,subprocess,time,zipfile
root=pathlib.Path(__file__).resolve().parent.parent
out=root/'received/evidence/native-ui';out.mkdir(parents=True,exist_ok=True)
tool=pathlib.Path(os.environ['RUNNER_TEMP'])/'studio-native-ax'
subprocess.run(['swiftc',root/'scripts/m2-macos-ax.swift','-o',tool],check=True)
checks=[];events=[]
def ax(*args):
    p=subprocess.run([tool,*map(str,args)],text=True,capture_output=True,timeout=30)
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    value=json.loads(p.stdout);events.append({'action':args,'result':value});return value
def snap(name):
    tree=ax('snapshot');(out/(name+'.json')).write_text(json.dumps(tree,indent=2)+'\n')
    subprocess.run(['screencapture','-x',out/(name+'.png')],check=True)
    return tree
def text(tree):return '\n'.join(str(r.get(k,'')) for r in tree for k in ['title','description','value','help'])
def wait_for(expected,seconds=60):
    end=time.time()+seconds
    while time.time()<end:
        tree=ax('snapshot')
        if expected in text(tree):return tree
        time.sleep(1)
    snap('failed-wait');raise AssertionError('Native UI did not show '+expected)
def press(label):
    ax('press',label);time.sleep(.6)
def key(code,flags=0):ax('key',code,flags);time.sleep(.4)
def choose(path,saving=False):
    # macOS standard Open/Save sheet: reveal its Go to Folder field, paste
    # an absolute test-fixture path, then confirm through the normal sheet.
    key(5,1048576|131072);time.sleep(.5)
    snap('path-entry')
    ax('paste',str(path.parent if saving else path));time.sleep(.5);key(36);time.sleep(.8)
    if saving:
        snap('save-filename');ax('filename',path.name);time.sleep(.3)
    key(36);time.sleep(1)
def check(name,detail):checks.append({'name':name,'result':'pass','detail':detail})
app='/Applications/Embroidery Studio.app'
try:
    # The runner contains only the scripted test document, never user work.
    subprocess.run(['pkill','-x','embroidery-studio'],check=False);time.sleep(1)
    subprocess.run(['open','-na',app],check=True);time.sleep(4)
    initial=snap('initial')
    if 'Skip the tour' in text(initial):press('Skip the tour')
    current=ax('snapshot')
    if 'Upload image' not in text(current):press('Home')
    wait_for('Upload image');press('Upload image');time.sleep(1)
    snap('image-picker');choose(root/'engine/test/fixtures/k-logo.png')
    wait_for('1,374',90);snap('converted');check('native image conversion','1,374 stitches from actual PNG file picker')
    current=ax('snapshot')
    graphics_error='The canvas needs WebGL' in text(current)
    if graphics_error:
        checks.append({'name':'native canvas preview','result':'blocked','detail':'Native WebView reports WebGL unavailable on the hosted VM. No application or graphics settings were changed.'})
    # Select the same prominent hoop control observed in the native tree.
    hoop=next((r for r in current if r['role']=='AXButton' and (r['title'].startswith('Hoop:') or r['description'].startswith('Hoop:'))),None)
    if hoop:
        press(hoop['title'] or hoop['description'])
        wait_for('Search hoops');ax('set','Search hoops','100x100');time.sleep(1)
        snap('hoop-picker')
        choices=ax('snapshot')
        found=next(r for r in choices if r['role']=='AXButton' and '4 x 4 in' in (r['title']+' '+r['description']))
        press(found['title'] or found['description']);wait_for('100 × 100');check('native hoop selection','100 × 100 mm selected from search')
    else:raise AssertionError('Native hoop selector was not exposed as expected; evidence retained')
    # The observed compact native Save sheet opens with its proposed filename
    # selected. Confirm it normally; XPC-hosted fields are not in the app's AX
    # tree. Find only the newly written agent fixture on this disposable runner.
    save_start=time.time()
    key(1,1048576);time.sleep(1);snap('project-save-dialog');key(36)
    project=None
    for _ in range(30):
        candidates=[p for p in pathlib.Path.home().rglob('k-logo.lilo') if p.stat().st_mtime>=save_start]
        if candidates:project=max(candidates,key=lambda p:p.stat().st_mtime);break
        time.sleep(.5)
    assert project is not None,'Native Save sheet did not produce a new project'
    with zipfile.ZipFile(project) as z:
        doc=json.loads(z.read('project.json'));assert len(doc['design']['objects'])==6
    check('native project save','Actual native Save sheet wrote a valid project with six editable objects')
    shutil.copy2(project,out/'Native-Mac-ZIP-sample.lilo')
    press('Export');wait_for('Save PES');snap('export')
    current=ax('snapshot');save=next(r for r in current if r['role']=='AXButton' and ('Save PES' in r['title'] or 'Save PES' in r['description']))
    export_start=time.time()
    press(save['title'] or save['description']);time.sleep(1);snap('pes-save-dialog');key(36)
    pes=None
    for _ in range(30):
        candidates=[p for p in pathlib.Path.home().rglob('k-logo.pes') if p.stat().st_mtime>=export_start]
        if candidates:pes=max(candidates,key=lambda p:p.stat().st_mtime);break
        time.sleep(.5)
    assert pes is not None,'Native Save sheet did not produce a new PES file'
    assert pes.read_bytes().startswith(b'#PES')
    shutil.copy2(pes,out/'Native-Mac-ZIP-sample.pes')
    check('native PES export',str(pes.stat().st_size)+' bytes with valid PES header')
    # Use the OS file-open event to reopen the project saved by this native app.
    subprocess.run(['open','-a',app,project],check=True);wait_for('1,374');snap('project-reopened')
    check('native project reopening','Native saved project reopened with 1,374 stitches')
    result='partial' if graphics_error else 'pass'
except Exception as exc:
    result='incomplete';error=str(exc)
    try:snap('failure')
    except Exception:pass
finally:
    report={'result':result,'checks':checks,'automation':'native Accessibility API; no application changes or browser substitutes',
            'source':'actual final customer ZIP installed on macOS','error':locals().get('error'),'events':events}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='events'},indent=2))
    if result!='pass':raise SystemExit(1)
