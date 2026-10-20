# Codemagic Mac build and M3 evidence

INCOMPLETE / FAILED — inspect evidence; do not claim native/customer approval

Machine configured: mac_mini_m2, manual-only, 80-minute maximum. No billing or publishing configured.

This ARM Mac builds a universal Intel/Apple silicon app. Native execution tests cover ARM only; Intel execution is not verified here.

## Package

ZIP bytes: not verified; strict limit: 20,000,000 bytes; under limit: not verified.

If the size gate fails, the complete oversized package remains available for owner inspection. It is not Etsy-ready. No functionality is removed.

## Test stages

| Stage | Result | Detail |
|---|---|---|
| Build/dependencies | not completed | Test stages have not run |

## Customer installation versus CI

GUI installation captures, when available, use an actual Safari localhost download, Finder, Archive Utility and Installer on this disposable CI Mac. The localhost origin and CI permissions differ from a clean customer Mac.

Ordinary CI installation uses sudo installer, separately logged in evidence/ci-package-install.txt. It does not prove a customer can pass Gatekeeper or authentication.

Gatekeeper consumer testing: NOT COMPLETED. The app remains ad-hoc signed, without Developer ID/notarization. No Gatekeeper warning screenshots are fabricated and no security settings or quarantine attributes are changed.

GUI capture status: not available. 

No warning observed in an incomplete capture means unknown, not proof that customers will see no warning.

## Screenshots and walkthrough

Original full-resolution PNGs: 02-macOS/installation/originals and 02-macOS/functional/originals. Internal AX/debug logs are separate. Browser screenshots are under evidence/browser-acceptance and are not native installation evidence.

See MACOS_ILLUSTRATED_GUIDE_DRAFT.md. Screenshots are private QA artifacts until reviewed for account information and personal paths; do not put unreviewed originals in an Etsy listing.

Build logs, manifests, screenshot indexes and test reports are included in Mac-QA-evidence.zip. The customer download is only Embroidery-Studio-macOS.zip.
