"""Private M2 Actions orchestration using existing Git credential-manager access.
Credentials stay in process memory and are never written to evidence or logs.
"""
import argparse, json, os, pathlib, subprocess, urllib.request, urllib.error

REPO = 'thomastt-cryoo/embroidery-aapp-'
parser = argparse.ArgumentParser()
parser.add_argument('command', choices=['dispatch', 'status', 'artifacts', 'download'])
parser.add_argument('--id')
args = parser.parse_args()
env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never')
p = subprocess.run(['git', '-c', 'credential.interactive=never', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n', text=True, capture_output=True, env=env, timeout=45)
fields = dict(line.split('=', 1) for line in p.stdout.splitlines() if '=' in line)
if not fields.get('password'):
    raise SystemExit('GitHub credential-manager access is unavailable; no action performed.')
headers = {'Authorization': 'Bearer '+fields['password'], 'Accept': 'application/vnd.github+json', 'User-Agent': 'Embroidery-Studio-M2', 'X-GitHub-Api-Version': '2022-11-28'}

def api(path, method='GET', body=None):
    req = urllib.request.Request('https://api.github.com/'+path, headers=headers, method=method, data=json.dumps(body).encode() if body is not None else None)
    if body is not None: req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        return json.loads(raw) if raw else {}

repo = api('repos/'+REPO)
assert repo['private'], 'Refusing to use a public repository for this milestone.'
if args.command == 'dispatch':
    api('repos/'+REPO+'/actions/workflows/release.yml/dispatches', 'POST', {'ref': 'main'})
    print('Dispatched private macOS workflow on main; no release or public artifact created.')
elif args.command == 'status':
    runs = api('repos/'+REPO+'/actions/workflows/release.yml/runs?per_page=5')['workflow_runs']
    for run in runs:
        print(json.dumps({k:run[k] for k in ['id','html_url','head_sha','status','conclusion','created_at','updated_at']},indent=2))
        if args.id and str(run['id']) == args.id:
            jobs=api('repos/'+REPO+'/actions/runs/'+args.id+'/jobs')['jobs']
            print(json.dumps([{'id':j['id'],'status':j['status'],'conclusion':j['conclusion'],'started_at':j['started_at'],'completed_at':j['completed_at'],'steps':j['steps']} for j in jobs],indent=2))
elif args.command == 'artifacts':
    print(json.dumps(api('repos/'+REPO+'/actions/runs/'+args.id+'/artifacts'),indent=2))
elif args.command == 'download':
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, hdrs, newurl): return None
    req=urllib.request.Request('https://api.github.com/repos/'+REPO+'/actions/artifacts/'+args.id+'/zip',headers=headers)
    try:
        response=urllib.request.build_opener(NoRedirect).open(req,timeout=30)
    except urllib.error.HTTPError as e:
        if e.code != 302: raise
        # The signed artifact URL carries its own authorization. Never forward the API token.
        response=urllib.request.urlopen(e.headers['Location'],timeout=120)
    target=pathlib.Path('dist/M2/macos-actions-artifact.zip')
    target.parent.mkdir(parents=True,exist_ok=True)
    with response, target.open('wb') as f:
        while block:=response.read(1024*1024): f.write(block)
    print(str(target),target.stat().st_size,'bytes')
