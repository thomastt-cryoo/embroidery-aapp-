"""Package gate and truthful partial reports, including after CI/test failures."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'out'


def load(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def validate_package(out):
    archive = out / 'Embroidery-Studio-macOS.zip'
    size = archive.stat().st_size
    selected = load(out / 'evidence/mac-selected-package.json', {})
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    assert selected.get('sha256') == digest, 'ZIP changed after package selection'
    assert selected.get('completeUniversalApplication') and selected.get('kind') == 'pkg'
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert sorted(z.namelist()) == ['Install Embroidery Studio.pkg', 'LICENSE.txt', 'NOTICE.txt', 'START HERE.txt']
        installer = z.read('Install Embroidery Studio.pkg')
        assert installer.startswith(b'xar!'), 'Expected a real flat Apple package'
    result = dict(zipBytes=size, zipSha256=digest, installerBytes=len(installer),
                  limitBytes=20_000_000, underLimit=size < 20_000_000,
                  completeUniversalApplication=True, installerCount=1)
    (out / 'evidence/size-gate.json').write_text(json.dumps(result, indent=2) + '\n')
    (out / 'SHA256SUMS.txt').write_text(digest + '  Embroidery-Studio-macOS.zip\n')
    installers = out / 'installers'
    installers.mkdir(exist_ok=True)
    (installers / 'Install Embroidery Studio.pkg').write_bytes(installer)
    assert size < 20_000_000, f'Complete ZIP is {size:,} bytes; exceeds Etsy limit. No assets removed or split.'
    return result


def render_report(out, exit_code):
    out.mkdir(exist_ok=True)
    stages = load(out / 'evidence/test-stages.json', [])
    size = load(out / 'evidence/size-gate.json', {})
    capture = load(out / '02-macOS/installation/capture-results.json', {})
    mode = load(out / 'evidence/run-mode.json', {})
    verify_only = mode.get('mode') == 'verification-only'
    required = {'Desktop permission probe (read-only)', 'M3 GUI installation walkthrough',
                'Ordinary CI installation from the actual customer ZIP', 'Installed native app functional tests'}
    if not verify_only:
        required.add('Separate production browser regression')
    success = (exit_code == 0 and bool(stages) and all(s['status'] == 'pass' for s in stages)
               and required <= {s['name'] for s in stages}
               and size.get('underLimit') and (verify_only or (out / 'evidence/native-rust-tests.passed').exists()))
    status = 'CI checks passed; clean consumer Gatekeeper testing still required' if success else 'INCOMPLETE / FAILED — inspect evidence; do not claim native/customer approval'
    lines = ['# Codemagic Mac build and M3 evidence', '', status, '',
             f"Machine configured: mac_mini_m2, manual-only, {20 if verify_only else 80}-minute maximum. No billing or publishing configured.", '',
             'This ARM Mac builds a universal Intel/Apple silicon app. Native execution tests cover ARM only; Intel execution is not verified here.', '',
             '## Package', '',
             f"ZIP bytes: {size.get('zipBytes', 'not verified')}; strict limit: 20,000,000 bytes; under limit: {size.get('underLimit', 'not verified')}.", '',
             'If the size gate fails, the complete oversized package remains available for owner inspection. It is not Etsy-ready. No functionality is removed.', '',
             '## Test stages', '', '| Stage | Result | Detail |', '|---|---|---|']
    if verify_only:
        lines[4:4] = ['Verification only: original sealed ZIP reused; no app build, Rust tests or browser regression repeated. '
                      'The source run passed 96 Rust tests and the browser regression; those are historical results.', '']
    for stage in stages:
        detail = str(stage['detail']).replace('|', '/').replace('\n', ' ')
        lines.append(f"| {stage['name']} | {stage['status']} | {detail} |")
    if not stages:
        lines.append('| Build/dependencies | not completed | Test stages have not run |')
    lines += ['', '## Customer installation versus CI', '',
              'GUI installation captures, when available, use Finder, Archive Utility and Installer on this disposable CI Mac. Full-build mode attempts a Safari localhost download; verification-only mode transfers the sealed ZIP through private Git into Downloads. Neither is a clean consumer Etsy download or a consumer Gatekeeper test.', '',
              'Ordinary CI installation uses sudo installer, separately logged in evidence/ci-package-install.txt. It does not prove a customer can pass Gatekeeper or authentication.', '',
              'Gatekeeper consumer testing: NOT COMPLETED. The app remains ad-hoc signed, without Developer ID/notarization. No Gatekeeper warning screenshots are fabricated and no security settings or quarantine attributes are changed.', '',
              'GUI capture status: ' + str(capture.get('status', 'not available')) + '. ' + str(capture.get('stopReason') or capture.get('error') or ''), '',
              'No warning observed in an incomplete capture means unknown, not proof that customers will see no warning.', '',
              '## Screenshots and walkthrough', '',
              'Original full-resolution PNGs: 02-macOS/installation/originals and 02-macOS/functional/originals. Internal AX/debug logs are separate. Browser screenshots are under evidence/browser-acceptance and are not native installation evidence.', '',
              'See MACOS_ILLUSTRATED_GUIDE_DRAFT.md. Screenshots are private QA artifacts until reviewed for account information and personal paths; do not put unreviewed originals in an Etsy listing.', '',
              'Build logs, manifests, screenshot indexes and test reports are included in Mac-QA-evidence.zip. The customer download is only Embroidery-Studio-macOS.zip.', '']
    (out / 'M3_MACOS_RUN_REPORT.md').write_text('\n'.join(lines))
    guide = ['# Mac installation walkthrough — actual CI evidence draft', '',
             'This draft contains only screenshots captured in this run. Missing stages are not illustrated. It is not a completed clean-customer Gatekeeper guide. Review every screenshot for privacy before customer use.', '']
    screens = []
    for screen in capture.get('screens', []):
        if screen.get('customerCandidate'):
            screens.append((screen['label'], '02-macOS/installation/' + screen['file']))
    functional = load(out / '02-macOS/functional/originals/screenshots-index.json', [])
    for screen in functional:
        if screen.get('customerCandidate', False):
            screens.append((screen['label'], '02-macOS/functional/originals/' + screen['file']))
    captions = {
        'downloaded-zip-in-finder': 'Find the downloaded ZIP in Downloads',
        'zip-extracted': 'Open the ZIP to extract its contents',
        'select-installer': 'Open Install Embroidery Studio.pkg',
        'initial': 'Open Embroidery Studio from Applications',
        'image-picker': 'Choose the image you want to embroider',
        'converted': 'View the embroidery generated from your image',
        'stitches-without-reference': 'Preview the stitches without the source picture',
        'simulation-zero': 'Start the stitch preview',
        'simulation-complete': 'Watch the completed stitch preview',
        'hoop-picker': 'Choose the hoop that matches your machine',
        'stitch-setting-edited': 'Select a shape to adjust its stitches',
        'project-save-dialog': 'Save your editable project',
        'export': 'Choose the embroidery file format for your machine',
        'pes-save-dialog': 'Choose where to save the embroidery file',
        'project-reopened': 'Reopen your saved project',
    }
    for index, (label, relative) in enumerate(screens, 1):
        caption = captions.get(label, label.replace('-', ' ').capitalize())
        guide += [f'## {index}. {caption}', '',
                  f'![Actual Mac screen — privacy review pending](<{relative}>)', '']
    if not screens:
        guide += ['No customer-facing screenshots were captured. Desktop access or an actual Mac run is still required.', '']
    (out / 'MACOS_ILLUSTRATED_GUIDE_DRAFT.md').write_text('\n'.join(guide))
    # QA download only; installers and customer ZIP are independent artifacts.
    with zipfile.ZipFile(out / 'Mac-QA-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for folder in [out / 'evidence', out / '02-macOS']:
            for path in sorted(folder.rglob('*')):
                if path.is_file():
                    archive.write(path, path.relative_to(out))
        for name in ['M3_MACOS_RUN_REPORT.md', 'MACOS_ILLUSTRATED_GUIDE_DRAFT.md', 'SHA256SUMS.txt']:
            if (out / name).exists():
                archive.write(out / name, name)
    return success


def render_rebuild_report(out, exit_code):
    """A successful package rebuild must never imply native/customer approval."""
    out.mkdir(exist_ok=True)
    size = load(out / 'evidence/size-gate.json', {})
    success = (exit_code == 0 and size.get('underLimit') is True
               and (out / 'evidence/rebuild-package.passed').exists())
    lines = ['# Mac UI rebuild', '',
             'BUILD AND PACKAGE CHECKS PASSED' if success else 'BUILD INCOMPLETE / FAILED', '',
             ('Manual standard GitHub macos-15 runner; 40-minute maximum. No automatic publishing or VNC wait.'
              if os.environ.get('GITHUB_ACTIONS') == 'true' else
              'Manual mac_mini_m2 workflow; 40-minute maximum. No automatic publishing or VNC wait.'), '',
             f"ZIP bytes: {size.get('zipBytes', 'not verified')}; limit: strictly below 20,000,000 bytes.", '',
             f"ZIP SHA-256: {size.get('zipSha256', 'not verified')}", '',
             'Includes the latest source UI corrections. Logs include the exact source commit.', '',
             'A pass covers compilation, preserved-source checks, universal ARM/Intel binary identity, '
             'ad-hoc signature verification and customer ZIP integrity/size. It does not cover installation or application use.', '',
             'Native GUI, export, playback and browser regression tests were not repeated in this run. '
             'No installation screenshots were requested or fabricated.', '',
             'Clean consumer Gatekeeper testing remains incomplete. Signing remains ad-hoc; '
             'this rebuild does not add Developer ID signing or notarization.', '',
             'Download Embroidery-Studio-macOS.zip for the application. Mac-QA-evidence.zip is owner-only build evidence.', '']
    (out / 'MACOS_REBUILD_REPORT.md').write_text('\n'.join(lines), encoding='utf-8')
    with zipfile.ZipFile(out / 'Mac-QA-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((out / 'evidence').rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(out))
        for name in ['MACOS_REBUILD_REPORT.md', 'SHA256SUMS.txt']:
            if (out / name).exists():
                archive.write(out / name, name)
    return bool(success)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--initialize', action='store_true')
    parser.add_argument('--check-package', action='store_true')
    parser.add_argument('--exit-code', type=int, default=1)
    parser.add_argument('--build-only', action='store_true')
    args = parser.parse_args()
    (OUT / 'evidence').mkdir(parents=True, exist_ok=True)
    if args.check_package:
        print(json.dumps(validate_package(OUT), indent=2))
    elif args.build_only:
        render_rebuild_report(OUT, args.exit_code)
    else:
        render_report(OUT, args.exit_code)


if __name__ == '__main__':
    main()
