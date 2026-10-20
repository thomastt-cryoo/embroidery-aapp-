#!/bin/bash
# The owner starts this from the Mac desktop. It never approves permissions.
set -euo pipefail
cd "${CM_BUILD_DIR:?Use the desktop launcher}"
export RUNNER_TEMP="$PWD/.codemagic-tmp"
export M3_VERIFY_ONLY=1 M3_OWNER_ASSISTED=1 M3_USE_CI_TRANSFER=1 PYTHONUNBUFFERED=1
source .codemagic-venv/bin/activate
finish() {
  code=$?
  trap - EXIT
  python scripts/codemagic-macos-report.py --exit-code "$code" || true
  if test -f out/evidence/owner-started; then
    printf '%s\n' "$code" > out/evidence/owner-exit-code
  fi
  echo 'Verification finished. Return to Codemagic for the QA artifacts.'
  exit "$code"
}
trap finish EXIT
echo 'Approve the requesting test host (normally Terminal) in Accessibility and Screen Recording.'
echo 'If asked to quit and reopen Terminal, reopen it and double-click the desktop launcher again.'
swift scripts/m3-macos-request-permissions.swift
python - <<'PY'
import json,subprocess,time
for attempt in range(60):
    p=subprocess.run(['swift','scripts/m3-macos-permissions.swift'],capture_output=True,text=True,timeout=45)
    if p.returncode==0:
        state=json.loads(p.stdout)
        if state.get('accessibilityTrusted') and state.get('screenCaptureAuthorized'):
            break
    time.sleep(2)
else:
    raise SystemExit('Permissions are still unavailable; no application/security settings were modified by this script.')
PY
touch out/evidence/owner-started
python scripts/codemagic-macos-tests.py
