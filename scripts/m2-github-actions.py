"""Private M2 Actions orchestration using existing Git credential-manager access.
Credentials stay in process memory and are never written to evidence or logs.
"""
import argparse, json, os, pathlib, subprocess, urllib.request, urllib.error

REPO = 'thomastt-cryoo/embroidery-aapp-'
parser = argparse.ArgumentParser()
parser.add_argument('command', choices=['dispatch', 'verify', 'status', 'artifacts', 'download', 'job-logs', 'cancel', 'cancel-site', 'evidence'])
parser.add_argument('--id')
parser.add_argument('--workflow', default='release.yml')
parser.add_argument('--output')
parser.add_argument('--artifact-name', default='Embroidery-Studio-macOS-M2-Etsy-private')
parser.add_argument('--runner', choices=['macos-14','macos-15-intel'], default='macos-14')
args = parser.parse_args()
env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never')
p = subprocess.run(['git', '-c', 'credential.interactive=never', 'credential', 'fill'], input='protocol=https\nhost=github.com\nusername=thomastt-cryoo\n\n', text=True, capture_output=True, env=env, timeout=45)
fields = dict(line.split('=', 1) for line in p.stdout.splitlines() if '=' in line)
if not fields.get('password'):
    raise SystemExit('GitHub credential-manager access is unavailable; no action performed.')
headers = {'Authorization': 'Bearer '+fields['password'], 'Accept': 'application/vnd.github+json', 'User-Agent': 'Embroidery-Studio-M2', 'X-GitHub-Api-Version': '2022-11-28'}

def api(path, method='GET', body=None):
    req = urllib.request.Request('https://api.github.com/'+path, headers=headers, method=method, data=json.dumps(body).encode() if body is not None else None)
    if body is not None: req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raise SystemExit(str(e.code)+': '+e.read().decode())

repo = api('repos/'+REPO)
assert repo['private'], 'Refusing to use a public repository for this milestone.'
if args.command == 'dispatch':
    api('repos/'+REPO+'/actions/workflows/'+args.workflow+'/dispatches', 'POST', {'ref': 'main'})
    print('Dispatched private macOS workflow on main; no release or public artifact created.')
elif args.command == 'verify':
    assert args.id and args.id.isdigit(), 'A successful build run id is required.'
    api('repos/'+REPO+'/actions/workflows/mac-zip-verification.yml/dispatches','POST',{'ref':'main','inputs':{'runId':args.id,'artifactName':args.artifact_name,'runner':args.runner}})
    print('Dispatched private native verification of the actual customer ZIP; no new application build.')
elif args.command == 'status':
    runs = api('repos/'+REPO+'/actions/workflows/'+args.workflow+'/runs?per_page=5')['workflow_runs']
    for run in runs:
        print(json.dumps({k:run[k] for k in ['id','html_url','head_sha','status','conclusion','created_at','updated_at']},indent=2))
        if args.id and str(run['id']) == args.id:
            jobs=api('repos/'+REPO+'/actions/runs/'+args.id+'/jobs')['jobs']
            print(json.dumps([{'id':j['id'],'status':j['status'],'conclusion':j['conclusion'],'started_at':j['started_at'],'completed_at':j['completed_at'],'steps':j['steps']} for j in jobs],indent=2))
elif args.command == 'cancel':
    assert args.id and args.id.isdigit()
    run=api('repos/'+REPO+'/actions/runs/'+args.id)
    assert run['path']=='.github/workflows/mac-zip-verification.yml', 'Only this milestone verification may be cancelled.'
    api('repos/'+REPO+'/actions/runs/'+args.id+'/cancel','POST')
    print('Cancelled superseded private ZIP verification run:',args.id)
elif args.command == 'cancel-site':
    runs=api('repos/'+REPO+'/actions/workflows/site.yml/runs?per_page=10')['workflow_runs']
    for run in runs:
        print(json.dumps({'id':run['id'],'status':run['status'],'conclusion':run['conclusion']}))
        if run['status'] != 'completed':
            api('repos/'+REPO+'/actions/runs/'+str(run['id'])+'/cancel','POST')
            print('Cancelled inherited website workflow; no publishing requested.')
elif args.command == 'artifacts':
    print(json.dumps(api('repos/'+REPO+'/actions/runs/'+args.id+'/artifacts'),indent=2))
elif args.command == 'evidence':
    from datetime import datetime
    runs = api('repos/'+REPO+'/actions/workflows/'+args.workflow+'/runs?per_page=100')['workflow_runs']
    selected = []
    total_seconds = 0
    for run in runs:
        item = {k:run[k] for k in ['id','html_url','head_sha','status','conclusion','created_at','updated_at']}
        jobs = api('repos/'+REPO+'/actions/runs/'+str(run['id'])+'/jobs')['jobs']
        item['jobs'] = [{k:j[k] for k in ['id','name','status','conclusion','started_at','completed_at','runner_name','labels']} for j in jobs]
        for job in item['jobs']:
            if job['completed_at'] and job['started_at'] and job['runner_name']:
                seconds = int((datetime.fromisoformat(job['completed_at'].replace('Z','+00:00')) - datetime.fromisoformat(job['started_at'].replace('Z','+00:00'))).total_seconds())
                job['elapsedSeconds'] = seconds
                total_seconds += seconds
            elif not job['runner_name']:
                job['elapsedSeconds'] = 0
                job['runnerNeverAssigned'] = True
        if str(run['id']) == args.id:
            item['artifacts'] = api('repos/'+REPO+'/actions/runs/'+args.id+'/artifacts')['artifacts']
        selected.append(item)
    target = pathlib.Path(args.output or 'reports/M2/evidence/actions-final.json')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps({'repository':REPO,'private':repo['private'],'selectedRunId':args.id,'measuredMacJobSeconds':total_seconds,'allowanceVerified':False,'runs':selected},indent=2)+'\n')
    print('Saved private run, artifact and measured runner-time evidence:',target)
elif args.command in ['download','job-logs']:
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, hdrs, newurl): return None
    endpoint='artifacts/'+args.id+'/zip' if args.command=='download' else 'jobs/'+args.id+'/logs'
    req=urllib.request.Request('https://api.github.com/repos/'+REPO+'/actions/'+endpoint,headers=headers)
    try:
        response=urllib.request.build_opener(NoRedirect).open(req,timeout=30)
    except urllib.error.HTTPError as e:
        if e.code != 302: raise
        # The signed artifact URL carries its own authorization. Never forward the API token.
        response=urllib.request.urlopen(e.headers['Location'],timeout=120)
    target=pathlib.Path(args.output or 'reports/M2/build-artifacts/macos-actions-artifact.zip')
    target.parent.mkdir(parents=True,exist_ok=True)
    with response, target.open('wb') as f:
        while block:=response.read(1024*1024): f.write(block)
    print(str(target),target.stat().st_size,'bytes')
