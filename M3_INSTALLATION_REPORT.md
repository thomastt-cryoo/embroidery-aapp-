# M3 — current Mac verification and installation screenshots

> **Branding status:** This report's native screenshots and functional results refer to the earlier temporary-name package. The final Embrova build is being verified separately. Its Windows delivery is already verified; [branding checkpoint](reports/embrova-branding/CHECKPOINT_2_WINDOWS.md) records the exact new ZIP and source. Earlier Mac files below retain their historical names and must not be presented as the final Embrova download.

20 October 2026. **The installed application passed all eight native functional checks on both Apple silicon and Intel Macs. The reported sidebar defect is visibly corrected. The complete customer installation/security walkthrough remains incomplete.** Windows was left alone, as requested.

## Tested package

- Customer ZIP: `dist/Mac-Verified-Latest/Embroidery-Studio-macOS.zip` — **19,866,936 bytes**, below Etsy's 20,000,000-byte limit by 133,064 bytes.
- SHA-256: `3381ddb207a0e535b780752c58957c3f95d68465921022ab90d306ea54d5e33d`.
- One complete installer: **19,851,396 bytes**; universal Intel/Apple silicon app.
- Application source: `471e1fc1a3544dda51048afcecc177844b7602f6`, including the Stitches and sidebar corrections.
- The actual owner-supplied ZIP was tested unchanged. No rebuild, engine edits, Windows app interaction or public Release/website publishing took place during verification. The owner had made the repository public; GitHub logs and artifacts are consequently public.

## Native results

[GitHub verification run 39377920327](https://github.com/thomastt-cryoo/embroidery-aapp-/actions/runs/39377920327) used standard `macos-14` and `macos-15-intel` runners. Actual systems were macOS 14.8.9 ARM and macOS 15.7.9 Intel. Both reported existing Accessibility and Screen Recording authorization. No permissions or security settings were changed.

| Check | Apple silicon | Intel |
|---|---|---|
| Actual ZIP integrity, checksum, size | Pass | Pass |
| Command-line CI installation; installed files/modes match sealed build | Pass | Pass |
| Strict ad-hoc signature and both binary architectures | Pass | Pass |
| Native image picker and image conversion | Pass; 1,374 stitches | Pass; 1,374 stitches |
| Native embroidery rendering with reference image hidden | Pass | Pass |
| Playback from zero to the end at 50x | Pass | Pass |
| Hoop selection, 100 x 100 mm | Pass | Pass |
| Select satin shape, edit pull compensation, restore original | Pass | Pass |
| Native Save dialog writes valid editable project | Pass; six objects | Pass; six objects |
| Native PES export through actual Save dialog | Pass; 4,072 bytes | Pass; 4,072 bytes |
| Reopen saved project | Pass; 1,374 stitches | Pass; 1,374 stitches |
| Corrected sidebar brand/navigation | Real screenshot and bounds reviewed | Real screenshot and bounds reviewed |

Saved project ZIPs were independently opened locally and contained six editable objects. Native PES outputs have valid PES headers and are retained as test evidence. This is representative native coverage; other machine formats were not individually exercised through native Save dialogs in this run. The prior 13-format browser results were not repeated.

## Why GitHub shows red

The separate M3 installer screenshot stage remains incomplete. Its failure is not a failed conversion, playback, save or export check.

- Apple silicon: extraction, introduction and installer steps were captured. The real macOS administrator-password dialog is visible in screenshot `006-installer-step-2.png`. The installer accessibility action returned error -25204. No password was entered and the authentication dialog was not approved by automation.
- Intel: the installer capture did not reach a known actionable installer screen; its last screenshot still shows Finder. No installer completion is claimed there.
- Both then installed successfully using the normal command-line CI installer, in a separate logged stage, before all eight native application checks passed.

The password prompt is a macOS installation authentication screen, not evidence of a broken app or an export problem. This CI capture does not test an Etsy/browser download with quarantine. **Clean consumer Gatekeeper testing remains unverified.** The application remains ad-hoc signed, without Developer ID signing/notarization. No Gatekeeper warning was captured; that is not proof customers will see none. No warnings were fabricated and no protections were disabled.

## Screenshots and illustrated guide

All paths below are relative to this repository. Original PNG files are separate, unedited **1920 x 1080** screenshots from the actual Mac runners. There are **40 PNGs** in this selected successful-functional run.

- `reports/M3/02-macOS/github-current-20261020/01-Apple-silicon/installation/` — 6 installer/extraction/authentication PNGs.
- `reports/M3/02-macOS/github-current-20261020/01-Apple-silicon/functional/` — 15 launch/import/preview/playback/hoop/edit/save/export/reopen PNGs.
- `reports/M3/02-macOS/github-current-20261020/02-Intel/installation/` — 4 extraction/installer-attempt PNGs; no completion claim.
- `reports/M3/02-macOS/github-current-20261020/02-Intel/functional/` — 15 native application PNGs.
- `reports/M3/02-macOS/github-current-20261020/screenshots-index.json` — every filename, dimensions, hash and customer-candidate flag.
- `reports/M3/02-macOS/github-current-20261020/MACOS_GUIDE_DRAFT.md` — illustrated guide with the missing installer steps explicitly marked.
- Each platform's `evidence/` folder — stage results, permissions, package identity, native functional summary.
- Each platform's `test-files/` folder — actual native-saved `.lilo` project and exported `.pes` file.

Diagnostic path-entry screenshots, the generic CI account authentication screen, and the reopened-project screenshot containing a CI filesystem path are retained as evidence but excluded from the customer illustration sequence. No personal owner account, private password or token appears in the selected guide. The draft must not be advertised as a complete customer installation guide.

Full original downloaded artifacts, native AX event logs and first-attempt evidence are preserved locally under `reports/mac-sidebar-fix/github-native/39377920327/` and `39377431255/`. Downloadable GitHub artifacts are named `Mac-native-verification-macos-14` and `Mac-native-verification-macos-15-intel`, with two-day retention. The selected PNGs/results/test files above remain locally and in version control beyond that expiry.

## Test-driver repairs and remaining work

The first run verified conversion, rendering, playback and hoop selection on both architectures, then stopped because the driver clicked an offscreen satin row. The driver now chooses an observed visible row. A separate false installer-warning detection came from a hidden menu item named Passwords; prompt detection now checks window content. Archive Utility's grouped extraction folder is recognized and the extracted installer is checksum-verified. These changes are confined to tests.

The previously unverified native playback, editing, project saving/reopening and PES export now pass. Remaining work is the complete clean consumer installer/security walkthrough and its missing progress/completion screenshots. No additional builds or repeated functional runs are scheduled, and no later milestone has started.
