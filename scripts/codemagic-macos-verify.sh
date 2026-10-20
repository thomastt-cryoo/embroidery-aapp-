#!/bin/bash
# Only verification of the already-built, checksum-sealed private Mac package.
set -euo pipefail
cd "${CM_BUILD_DIR:?Codemagic checkout required}"
test "$(uname -s)" = Darwin
test "$(uname -m)" = arm64
case "${CM_TRIGGER_SOURCE:-api}" in webhook|schedule) exit 1 ;; esac
mkdir -p out/evidence .codemagic-tmp
finish() {
  code=$?
  trap - EXIT
  python3 scripts/codemagic-macos-report.py --exit-code "$code" || true
  exit "$code"
}
trap finish EXIT
python3 -m venv .codemagic-venv
source .codemagic-venv/bin/activate
python -m pip install --disable-pip-version-check Pillow==12.3.0 > out/evidence/python-setup.txt 2>&1
python scripts/codemagic-macos-owner-session.py
