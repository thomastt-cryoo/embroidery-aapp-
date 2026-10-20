# M3 — installation screenshot report

20 October 2026. **M3 is incomplete: GitHub refused to start the Mac runner. No new M3 installation screenshots exist.** Windows is excluded following the user's instruction: “just check mac leave the windows”. No Windows application or installer was opened for M3.

## Mac test attempt and blocker

The private [M3 capture run](https://github.com/thomastt-cryoo/embroidery-aapp-/actions/runs/39349167291) failed before any workflow step ran. No runner was assigned, and no artifacts were produced. GitHub's recorded error was:

> The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings

This message does not establish which account condition applies. GitHub documents that billing locks can also block Actions/free-tier access; the account owner needs to inspect that status. No billing setting, payment method, spending limit or repository visibility was changed. [GitHub's billing-lock troubleshooting](https://docs.github.com/en/billing/how-tos/troubleshooting/locked-account).

The requested Mac screenshot workflow is prepared in the private repository, but its native execution remains untested. It uses the unchanged M2 ZIP and the standard macOS interface. Its initial phase records the browser download, Finder/Archive Utility extraction, installer pages and actual warnings; it stops for inspection at an unfamiliar screen or authentication request. The proposed browser download is from a local-only test server, not an Etsy listing. That download/quarantine behaviour also requires verification on the Mac.

## Required coverage

| Customer stage | New M3 capture status |
|---|---|
| Open and extract downloaded ZIP | Blocked before Mac startup |
| Open installer | Blocked |
| Gatekeeper warning, if any | **Not tested**; cannot say “not encountered” |
| Every approval/continuation step | Not tested |
| Installation progress and completion | Not tested |
| First launch from this clean installation | Not tested |
| Upload an image | New capture pending; historical M2 evidence exists |
| Generate and preview | New capture pending; historical M2 native screenshot retained |
| Select hoop and export | New capture pending; historical M2 native screenshots retained |

No warnings or installation pages were mocked, fabricated or substituted with documentation images. No operating-system security settings or download security attributes were changed. No new Mac runner minutes were consumed because a runner never started.

## Files and screenshot locations

- [Mac guide draft](<C:/Users/mazin/Downloads/embroidry app/reports/M3/02-macOS/MACOS_INSTALLATION_GUIDE_DRAFT.md>) — explicitly incomplete and not ready for Etsy/customer distribution.
- [Reserved new M3 originals folder](<C:/Users/mazin/Downloads/embroidry app/reports/M3/02-macOS/originals/README.md>) — currently contains no captured PNGs.
- [001 — welcome example, historical M2](<C:/Users/mazin/Downloads/embroidry app/reports/M3/02-macOS/reference-M2/001-app-welcome-M2.png>)
- [002 — generated native preview, historical M2](<C:/Users/mazin/Downloads/embroidry app/reports/M3/02-macOS/reference-M2/002-generated-preview-M2.png>)
- [003 — native hoop selection, historical M2](<C:/Users/mazin/Downloads/embroidry app/reports/M3/02-macOS/reference-M2/003-hoop-selection-M2.png>)
- [004 — native export options, historical M2](<C:/Users/mazin/Downloads/embroidry app/reports/M3/02-macOS/reference-M2/004-export-options-M2.png>)
- [Screenshot provenance, dimensions and SHA-256 hashes](<C:/Users/mazin/Downloads/embroidry app/reports/M3/reference-screenshot-inventory.json>)
- [Windows exclusion](<C:/Users/mazin/Downloads/embroidry app/reports/M3/01-Windows/README.md>)
- [GitHub rejection evidence](<C:/Users/mazin/Downloads/embroidry app/reports/M3/internal/github-mac-start-failure.json>) and [runner evidence](<C:/Users/mazin/Downloads/embroidry app/reports/M3/internal/actions.json>)

The four reference images are real native Mac screenshots from M2 run 39346926486, preserved unchanged as separate **1920 × 1080 PNGs**. They were visually checked for personal account details, personal file paths and credentials; none are visible. They are labelled historical references, not new clean-install evidence. The welcome example includes M2's sample in Recent projects, so it must not represent a pristine customer profile. M2 screenshots showing file paths were excluded from the draft.

## Preservation and next step

The M2 customer ZIPs, application, engine and approved interface are unchanged. The Mac ZIP remains 19,870,862 bytes, SHA-256 `bfcc78a2f28f7b2f55d7112135f828dd1ad1d11220b15f0e815091f6a563bf17`. Commercial signing/notarization remains outstanding, as documented in M2.

Resume when the GitHub Mac runner can start or another actual Mac environment is available. Then capture every real screen transition, observe actual Gatekeeper behaviour without globally weakening security, finish native installation/first-use captures, check every image for privacy, and replace the draft with a complete illustrated guide. Windows remains out of scope. M3 must not be marked complete on the current evidence.
