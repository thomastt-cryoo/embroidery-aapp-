# Codemagic Mac build and M3 evidence

INCOMPLETE / FAILED — inspect evidence; do not claim native/customer approval

Machine configured: mac_mini_m2, manual-only, 80-minute maximum. No billing or publishing configured.

This ARM Mac builds a universal Intel/Apple silicon app. Native execution tests cover ARM only; Intel execution is not verified here.

## Package

ZIP bytes: 19871801; strict limit: 20,000,000 bytes; under limit: True.

If the size gate fails, the complete oversized package remains available for owner inspection. It is not Etsy-ready. No functionality is removed.

## Test stages

| Stage | Result | Detail |
|---|---|---|
| Desktop permission probe (read-only) | pass | {'accessibilityTrusted': False, 'displayHeight': 768, 'displayWidth': 1024, 'screenCaptureAuthorized': False, 'securityPermissionsChanged': False} |
| M3 GUI installation walkthrough | blocked | Desktop capture/accessibility access is missing. No permissions changed; no screenshots invented. |
| Ordinary CI installation from the actual customer ZIP | pass | {'result': 'pass', 'zipSha256': '9d5bd61cb8531d67cf5b3990b659d3713accd792e08065371340717235f3e481', 'binaryArchitectures': 'x86_64 arm64', 'allInstalledFilesAndModesMatchBuild': True, 'method': 'sudo -n installer on disposable CI; not a customer Gatekeeper test', 'signature': 'ad-hoc, not Developer ID/notarized', 'securitySettingsChanged': False} |
| Installed native app functional tests | blocked | Installation or desktop permissions unavailable; browser results cannot substitute for native results. |
| Separate production browser regression | pass | Production frontend: real engine, 13 exports, save/reopen, simulation and offline regression; not native UI |

## Customer installation versus CI

GUI installation captures, when available, use Finder, Archive Utility and Installer on this disposable CI Mac. Full-build mode attempts a Safari localhost download; verification-only mode transfers the sealed ZIP through private Git into Downloads. Neither is a clean consumer Etsy download or a consumer Gatekeeper test.

Ordinary CI installation uses sudo installer, separately logged in evidence/ci-package-install.txt. It does not prove a customer can pass Gatekeeper or authentication.

Gatekeeper consumer testing: NOT COMPLETED. The app remains ad-hoc signed, without Developer ID/notarization. No Gatekeeper warning screenshots are fabricated and no security settings or quarantine attributes are changed.

GUI capture status: not available. 

No warning observed in an incomplete capture means unknown, not proof that customers will see no warning.

## Screenshots and walkthrough

Original full-resolution PNGs: 02-macOS/installation/originals and 02-macOS/functional/originals. Internal AX/debug logs are separate. Browser screenshots are under evidence/browser-acceptance and are not native installation evidence.

See MACOS_ILLUSTRATED_GUIDE_DRAFT.md. Screenshots are private QA artifacts until reviewed for account information and personal paths; do not put unreviewed originals in an Etsy listing.

Build logs, manifests, screenshot indexes and test reports are included in Mac-QA-evidence.zip. The customer download is only Embroidery-Studio-macOS.zip.
