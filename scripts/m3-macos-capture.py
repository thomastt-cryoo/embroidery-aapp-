"""Capture real native customer screens; never weaken system security or fake UI."""
import hashlib,json,os,pathlib,shutil,subprocess,time,threading,http.server

root=pathlib.Path(__file__).resolve().parent.parent
out=pathlib.Path(os.environ.get('M3_CAPTURE_OUT',str(root/'m3-capture'))); originals=out/'originals'; states=out/'internal'
for p in [originals,states]:p.mkdir(parents=True,exist_ok=True)
tool=pathlib.Path(os.environ['RUNNER_TEMP'])/'m3-native-ax'
subprocess.run(['swiftc',root/'scripts/m3-macos-ax.swift','-o',tool],check=True)
FINDER='com.apple.finder';SAFARI='com.apple.Safari';INSTALLER='com.apple.installer';STUDIO='io.github.thomasttcryoo.embroiderystudio'
events=[];screens=[];result={'status':'incomplete','warnings':[],'securityChanges':[]}
source=pathlib.Path(os.environ.get('M3_SOURCE_ZIP',str(pathlib.Path(os.environ['RUNNER_TEMP'])/'m3-source/Embroidery-Studio-macOS.zip')))
expected=os.environ.get('M3_SOURCE_SHA256','bfcc78a2f28f7b2f55d7112135f828dd1ad1d11220b15f0e815091f6a563bf17')
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
downloads=pathlib.Path.home()/'Downloads';downloads.mkdir(exist_ok=True)
archive=downloads/source.name

def run(args,**kwargs):return subprocess.run([str(x) for x in args],text=True,capture_output=True,timeout=45,**kwargs)
def ax(app,*args):
    p=run([tool,app,*args]);
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    value=json.loads(p.stdout);events.append({'target':app,'action':args,'result':value});return value
def tree(app):return ax(app,'snapshot')
def words(t):return '\n'.join(str(r.get(k,'')) for r in t for k in ['title','description','value','help','identifier'])
def snapshot(label,app,customer=True):
    current=tree(app); name=f'{len(screens)+1:03d}-{label}'
    (states/(name+'.json')).write_text(json.dumps(current,indent=2)+'\n')
    folder=originals if customer else states
    subprocess.run(['screencapture','-x',str(folder/(name+'.png'))],check=True)
    screens.append({'number':len(screens)+1,'label':label,'file':str((folder/(name+'.png')).relative_to(out)),'customerCandidate':customer,'privacyReview':'required before customer use','app':app})
    return current
def press(app,label):ax(app,'press',label);time.sleep(1)
def key(app,code,flags=0):ax(app,'key',code,flags);time.sleep(.6)
def wait(app,predicate,seconds=25):
    end=time.time()+seconds
    while time.time()<end:
        t=tree(app)
        if predicate(t):return t
        time.sleep(.8)
    snapshot('wait-stopped',app,False);raise RuntimeError('Expected native screen did not appear')
def app_open(app,path):subprocess.run(['open','-a',app,str(path)],check=True);time.sleep(3)
def quarantine(path):
    p=run(['xattr','-p','com.apple.quarantine',path]);return {'present':p.returncode==0,'value':p.stdout.strip()}

class Download(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path!='/Embroidery-Studio-macOS.zip':self.send_error(404);return
        self.send_response(200);self.send_header('Content-Type','application/zip');self.send_header('Content-Disposition','attachment; filename="Embroidery-Studio-macOS.zip"');self.send_header('Content-Length',str(source.stat().st_size));self.end_headers()
        with source.open('rb') as f:shutil.copyfileobj(f,self.wfile)
    def log_message(self,*args):pass

try:
    assert not pathlib.Path('/Applications/Embroidery Studio.app').exists(),'This capture needs a fresh Mac without the application'
    status=run(['spctl','--status'])
    result.update({'os':run(['sw_vers']).stdout,'zipSha256':expected,'zipBytes':source.stat().st_size,'cleanApplicationState':True,'gatekeeperBaseline':status.stdout.strip() or status.stderr.strip(),'downloadOrigin':'Actual Safari download from local-only test server; no public upload or security attribute modification'})
    if os.environ.get('M3_USE_CI_TRANSFER')=='1':
        shutil.copy2(source,archive)
        result['downloadOrigin']='Exact sealed customer ZIP fetched through private Git and copied to Downloads. No Safari/Etsy download or consumer quarantine claim.'
    else:
        server=http.server.HTTPServer(('127.0.0.1',8765),Download);threading.Thread(target=server.serve_forever,daemon=True).start()
        app_open('Safari','http://127.0.0.1:8765/Embroidery-Studio-macOS.zip')
        ax(SAFARI,'activate');time.sleep(1)
        for attempt in range(4):
            t=snapshot('browser-download-'+str(attempt+1),SAFARI,False)
            if archive.exists() and archive.stat().st_size==source.stat().st_size:break
            available=[r['title'] or r['description'] for r in t if r['role']=='AXButton']
            # Do not accept Safari security/privacy/download permission prompts.
            choice=next((v for v in available if v in ['Continue','Start Using Safari']),None)
            if choice:press(SAFARI,choice)
            else:time.sleep(2)
    assert archive.exists() and hashlib.sha256(archive.read_bytes()).hexdigest()==expected,'Customer ZIP transfer did not finish'
    result['zipQuarantine']=quarantine(archive)
    subprocess.run(['open','-R',str(archive)],check=True);time.sleep(2);ax(FINDER,'activate')
    snapshot('downloaded-zip-in-finder',FINDER)
    key(FINDER,31,1048576) # Command-O on the Finder-selected ZIP: Archive Utility.
    pkg=downloads/'Install Embroidery Studio.pkg'
    end=time.time()+25
    while time.time()<end and not pkg.exists():time.sleep(.5)
    assert pkg.exists(),'Archive Utility did not extract the PKG'
    snapshot('zip-extracted',FINDER)
    result['installerQuarantine']=quarantine(pkg)
    subprocess.run(['open','-R',str(pkg)],check=True);time.sleep(1)
    snapshot('select-installer',FINDER)
    key(FINDER,31,1048576);time.sleep(3)
    # Inspect actual applications/dialogs. Never synthesize a Gatekeeper screen.
    observed=None
    for app in [INSTALLER,FINDER]:
        try:
            current=snapshot('installer-opening',app);observed=(app,current)
            if app==INSTALLER:break
        except Exception as exc:events.append({'inspection':app,'error':str(exc)})
    assert observed,'No native installer or warning could be inspected'
    app,current=observed
    # Initial probe captures normal installer pages without entering passwords
    # or changing Gatekeeper/System Settings. Further steps depend on real UI.
    for step in range(7):
        buttons=[r['title'] or r['description'] for r in current if r['role']=='AXButton']
        content=words(current)
        if any(s in content.lower() for s in ['password','authenticate','unidentified developer','cannot be opened','can’t be opened','cannot check','can’t check','malware','unverified','not verified']):
            result['stopReason']='Actual warning or authentication screen requires inspection'
            if os.environ.get('M3_OWNER_ASSISTED')=='1':
                print('OWNER ACTION: Inspect the actual Mac warning/authentication screen in VNC. Only you may approve it; automation is paused.',flush=True)
                snapshot('owner-approval-required',app)
                for _ in range(45):
                    time.sleep(2);current=tree(app)
                    if not any(s in words(current).lower() for s in ['password','authenticate','unidentified developer','cannot be opened','can’t be opened','cannot check','can’t check','malware','unverified','not verified']):
                        snapshot('after-owner-action',app);result.pop('stopReason',None);break
                else:break
                continue
            break
        action=next((s for s in ['Continue','Install','Close'] if s in buttons),None)
        if not action:result['stopReason']='No known native installer action; inspect actual screenshot';break
        press(app,action);current=snapshot('installer-step-'+str(step+1),app)
        if action=='Close':result['status']='installer-pages-complete';break
    result['installedAppPresent']=pathlib.Path('/Applications/Embroidery Studio.app').exists()
except Exception as exc:
    result['error']=type(exc).__name__+': '+str(exc)
finally:
    result.update({'screens':screens,'events':events,'scope':'Native Mac GUI installation capture on CI only; not a clean consumer Gatekeeper test; no command-line installer fallback inside this capture; no security disabled'})
    (out/'capture-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='events'},indent=2))
