"""Native macOS ZIP regression through existing, already-authorized accessibility."""
import hashlib,json,os,pathlib,shutil,subprocess,time,zipfile
from PIL import Image
root=pathlib.Path(__file__).resolve().parent.parent
out=root/os.environ.get('M2_MAC_DELIVERY_DIR','received')/'evidence/native-ui';out.mkdir(parents=True,exist_ok=True)
tool=pathlib.Path(os.environ['RUNNER_TEMP'])/'studio-native-ax'
subprocess.run(['swiftc',root/'scripts/m2-macos-ax.swift','-o',tool],check=True)
checks=[];events=[];result='incomplete'
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

def control(role,label):
    return next(r for r in ax('snapshot') if r['role']==role and label in [r['title'],r['description'],r['help']])

def slider_end(label,end):
    # A native range click dispatches its input event. Safari does not use
    # Home/End like Chromium, so click the observed track end and finish with
    # ordinary left/right keys to cover its thumb's inset.
    ax('range',label,1 if end else 0)
    for _ in range(12):ax('key',124 if end else 123,0)
    time.sleep(.5)

def number_input(label,value):
    ax('click',label);time.sleep(.4);key(0,1048576);ax('type',str(value));time.sleep(.4);key(48)
def choose(path,saving=False):
    # macOS standard Open/Save sheet: reveal its Go to Folder field, paste
    # an absolute test-fixture path, then confirm through the normal sheet.
    key(5,1048576|131072);time.sleep(1)
    snap('path-entry')
    ax('type',str(path.parent if saving else path));time.sleep(1);snap('path-entered');key(36);time.sleep(1)
    if saving:
        snap('save-filename');ax('filename',path.name);time.sleep(.3)
    key(36);time.sleep(1)
def check(name,detail):
    checks.append({'name':name,'result':'pass','detail':detail})
    (out/'checks-live.json').write_text(json.dumps(checks,indent=2)+'\n')
app='/Applications/Embroidery Studio.app'
try:
    # The runner contains only the scripted test document, never user work.
    subprocess.run(['pkill','-x','embroidery-studio'],check=False);time.sleep(1)
    subprocess.run(['open','-na',app],check=True);time.sleep(4);ax('activate');time.sleep(.5)
    initial=snap('initial')
    if 'Skip the tour' in text(initial):press('Skip the tour')
    current=ax('snapshot')
    if 'Upload image' not in text(current):press('Home')
    wait_for('Upload image');press('Upload image');time.sleep(1)
    snap('image-picker');choose(root/'engine/test/fixtures/k-logo.png')
    wait_for('1,374',90);snap('converted');check('native image conversion','1,374 stitches from actual PNG file picker')
    current=ax('snapshot')
    assert 'could not start' not in text(current) and 'needs WebGL' not in text(current),'Native drawing canvas failed'
    # Remove the original picture so screenshot colour evidence proves stitch
    # rendering rather than the imported PNG. No browser or test hooks are used.
    reference=next(r for r in current if r['role']=='AXCheckBox' and r['title']=='Reference')
    if reference['value']=='1':press('Reference')
    press('Fit');time.sleep(2);snap('stitches-without-reference')
    pixels=Image.open(out/'stitches-without-reference.png').convert('RGB')
    # The runner's app window is centred; this crop excludes sidebars and toolbars.
    w,h=pixels.size;crop=pixels.crop((int(w*.32),int(h*.23),int(w*.72),int(h*.74)))
    red=blue=0
    for r,g,b in crop.getdata():
        if r>100 and r>g*1.5 and r>b*1.5:red+=1
        if b>60 and b>r*1.5 and b>g*1.2:blue+=1
    assert red>100 and blue>100,f'Native stitch pixels missing: red={red}, blue={blue}'
    check('native canvas preview',f'Actual installed application screenshot, reference hidden: {red} red and {blue} blue pixels in central stitch area')
    # Real native simulation must visibly remove and redraw the stitched design.
    slider_end('Scrub stitches',False);time.sleep(1);snap('simulation-zero')
    zero=control('AXSlider','Scrub stitches')
    assert float(zero['value'])==0,zero
    slider_end('Playback speed',True)
    speed=control('AXSlider','Playback speed')
    assert float(speed['value'])==50,speed
    auto=next(r for r in ax('snapshot') if r['role']=='AXCheckBox' and r['title']=='Auto-continue')
    if auto['value']!='1':press('Auto-continue')
    press('Play');time.sleep(8);wait_for('1,374');snap('simulation-complete')
    current=ax('snapshot');scrub=control('AXSlider','Scrub stitches')
    assert float(scrub['value'])>=1374,scrub
    check('native simulation','Played from zero to the end at 50x through native controls')
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
    # Select a generated satin object by its observed native element bounds.
    ax('click','Ultramarine satin 1');wait_for('Pull compensation')
    number_input('Pull compensation value',.35)
    time.sleep(2);snap('stitch-setting-edited')
    edited=control('AXSlider','Pull compensation')
    assert abs(float(edited['value'])-.35)<.001,edited
    # Each completed keyboard adjustment is a real undo step. Restore the
    # original value using the same input rather than discarding a new design.
    number_input('Pull compensation value',.15)
    time.sleep(2)
    restored=control('AXSlider','Pull compensation')
    assert abs(float(restored['value'])-.15)<.001,restored
    check('native stitch editing','Selected generated satin, changed pull compensation 0.15 to 0.35, then restored 0.15 through native range input')
    # The observed compact native Save sheet opens with its proposed filename
    # selected. Confirm it normally; XPC-hosted fields are not in the app's AX
    # tree. Find only the newly written agent fixture on this disposable runner.
    save_start=time.time()
    # Leave stitch-input focus through the visible File menu. The application's
    # normal keyboard guard intentionally ignores shortcuts while typing.
    ax('click','File');wait_for('Save ⌘S');menu=snap('project-file-menu')
    save_item=next(r for r in menu if r['role']=='AXMenuItem' and r['title'].startswith('Save ') and not r['title'].startswith('Save As'))
    ax('click',save_item['title']);time.sleep(2);snap('project-save-dialog');key(36)
    project=None
    for _ in range(30):
        candidates=[p for p in (pathlib.Path.home()/'Documents/Embroidery Studio').glob('*.lilo') if p.stat().st_mtime>=save_start]
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
        folders=[pathlib.Path.home()/'Documents/Embroidery Studio',pathlib.Path.home()/'Documents',pathlib.Path.home()/'Desktop',root]
        candidates=[p for folder in folders for p in folder.glob('*.pes') if p.stat().st_mtime>=export_start]
        if candidates:pes=max(candidates,key=lambda p:p.stat().st_mtime);break
        time.sleep(.5)
    assert pes is not None,'Native Save sheet did not produce a new PES file'
    assert pes.read_bytes().startswith(b'#PES')
    shutil.copy2(pes,out/'Native-Mac-ZIP-sample.pes')
    check('native PES export',str(pes.stat().st_size)+' bytes with valid PES header')
    # Use the OS file-open event to reopen the project saved by this native app.
    subprocess.run(['open','-a',app,project],check=True);wait_for('1,374');snap('project-reopened')
    check('native project reopening','Native saved project reopened with 1,374 stitches')
    result='pass'
except Exception as exc:
    result='incomplete';error=type(exc).__name__+': '+str(exc)
    try:snap('failure')
    except Exception:pass
finally:
    report={'result':result,'checks':checks,'automation':'native Accessibility API; no application changes or browser substitutes',
            'source':'actual final customer ZIP installed on macOS','error':locals().get('error'),'events':events}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='events'},indent=2))
    if result!='pass':raise SystemExit(1)
