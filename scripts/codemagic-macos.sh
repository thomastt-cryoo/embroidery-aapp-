#!/bin/bash
# Codemagic-only orchestration; never included in the application or installer.
set -euo pipefail
cd "${CM_BUILD_DIR:?Run this workflow on the connected Codemagic project}"
mkdir -p out/evidence out/02-macOS .codemagic-tmp
export RUNNER_TEMP="$PWD/.codemagic-tmp"
export LILO_FONTS_CACHE="$HOME/Library/Caches/EmbroideryStudio/fonts"
export PATH="$HOME/.cargo/bin:$PATH"
export PYTHONUNBUFFERED=1
# No credentials, account emails or environment dumps are written to artifacts.
finish() {
  code=$?
  trap - EXIT
  python3 scripts/codemagic-macos-report.py --exit-code "$code" || true
  exit "$code"
}
trap finish EXIT
test "$(uname -s)" = Darwin
test "$(uname -m)" = arm64
# Reject automatic invocation even if somebody later adds a webhook/schedule.
case "${CM_TRIGGER_SOURCE:-api}" in webhook|schedule) echo 'Manual builds only.'; exit 1 ;; esac
python3 scripts/codemagic-macos-report.py --initialize
{ sw_vers; xcodebuild -version; node --version; git rev-parse HEAD; } > out/evidence/environment.txt
if ! git cat-file -e 6334c8b^{commit} 2>/dev/null; then
  if test "$(git rev-parse --is-shallow-repository)" = true; then
    git fetch --unshallow origin
  else
    git fetch origin main
  fi
fi
python3 -m venv .codemagic-venv
source .codemagic-venv/bin/activate
python -m pip install --disable-pip-version-check Pillow==12.3.0 > out/evidence/python-setup.txt 2>&1
npm install --global pnpm@10.0.0 > out/evidence/pnpm-setup.txt 2>&1
if ! command -v rustup >/dev/null; then
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs -o "$RUNNER_TEMP/rustup-init.sh"
  sh "$RUNNER_TEMP/rustup-init.sh" -y --profile minimal --default-toolchain stable
fi
rustup toolchain install stable --profile minimal
rustup default stable
rustup target add aarch64-apple-darwin x86_64-apple-darwin
{ rustc --version; cargo --version; python --version; pnpm --version; } >> out/evidence/environment.txt
pnpm install --frozen-lockfile 2>&1 | tee out/evidence/dependencies.txt
pnpm fonts 2>&1 | tee out/evidence/fonts.txt
pnpm check-versions 2>&1 | tee out/evidence/versions.txt
pnpm guide:check 2>&1 | tee out/evidence/guide.txt
node scripts/m2-package-check.mjs 2>&1 | tee out/evidence/preservation.txt

# Same universal application and lossless PKG compression used for finalized M2.
pnpm tauri build --target universal-apple-darwin --bundles app 2>&1 | tee out/evidence/macos-build.txt
cp reports/M2/etsy/asset-preservation.json out/evidence/asset-preservation.json
python scripts/m2-macos-etsy.py package \
  --app 'app/src-tauri/target/universal-apple-darwin/release/bundle/macos/Embroidery Studio.app' \
  --mode raw --pkg-only --out out 2>&1 | tee out/evidence/packaging.txt
python scripts/codemagic-macos-report.py --check-package
# Reuse the target compiled above; avoid a second unrelated host release build.
cargo test --release --target aarch64-apple-darwin --manifest-path app/src-tauri/Cargo.toml --lib \
  2>&1 | tee out/evidence/native-rust-tests.txt
touch out/evidence/native-rust-tests.passed
python scripts/codemagic-macos-tests.py
