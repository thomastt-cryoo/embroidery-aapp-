# M2 checkpoint 6 — final ZIP workflows verified

20 October 2026. **Both final packages meet the size limit, and native workflow tests passed on all tested platforms.**

## Completed

Windows ZIP: **16,955,299 bytes**. Universal Mac ZIP: **19,870,862 bytes**. Each archive contains one complete installer and instructions/licence/notices. Final verification checked archive integrity, installer headers, exact hashes, required entries, legal text, both size limits and matching native installation evidence. The customer folder contains exactly two ZIPs.

The native Mac preview is fixed. Both Mac types successfully installed and tested the same sealed universal package; test-driver changes did not rebuild it. The embroidery engine and approved M1 layout remain protected. Original Lilo remains intact, and nothing was published publicly.

## Tests and results

| Final package | Native result | Evidence |
|---|---|---|
| Windows x64 | 11 checks passed | Healthy GPU, lost-WebGL fallback, PNG conversion, editing/Undo, hoop, simulation, Save/reopen, PES export, runtime assets and normal launch |
| macOS 14 Apple Silicon | 8 workflow checks passed, plus install/launch/project/PES loading | PNG conversion, visible stitches, simulation, hoop, editing, Save, PES export and reopen |
| macOS 15 Intel | 8 workflow checks passed, plus install/launch/project/PES loading | Same complete native sequence |

The PNG generated **1,374 stitches / six editable objects**. Both Mac native runs changed pull compensation **0.15 → 0.35 → 0.15 mm**, selected a **100 × 100 mm** hoop, played simulation from zero at **50×**, saved a valid editable project, exported a **4,072-byte PES**, and reopened the saved project after starting an empty document. Native screenshots were inspected. Visible red/blue stitches were also checked with the source reference image hidden.

Final native GitHub runs: [Apple Silicon](https://github.com/thomastt-cryoo/embroidery-aapp-/actions/runs/39346926486) and [Intel](https://github.com/thomastt-cryoo/embroidery-aapp-/actions/runs/39346935897), both successful. Downloaded evidence archives matched GitHub SHA-256 metadata before extraction. Evidence and customer files are retained locally.

The final source/identity guard passed earlier; no application changes followed. Supporting software-renderer and production browser regression results are summarized in the root final report. They are separately identified from native tests.

## Problems and limitations

Earlier native Mac test runs failed because of driver assumptions and event handling. The latest saved-file mismatch was a test error: Apple's dialog remembered the image folder while the driver searched Documents only. The final tests validate the actual saved file in either observed fixture location. Those earlier failed workflows remain failures in the evidence history.

Windows is unsigned; Mac is ad-hoc signed without Developer ID/notarization. These remain private review builds, and clean consumer trust prompts are not certified. macOS 13, physical Mac GPU behaviour, absent-WebView2 installation on a clean Windows VM, physical sew-out and network transfer remain untested. Signing/repackaging must retain the size limits.

Measured Mac runner elapsed time across M2: **156 minutes 42 seconds**, below the stated 200-minute ceiling. Account billing/free balance was not available. Only standard runners were used. All runs have ended.

## Actual application evidence

![Apple Silicon saved project reopened](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/macos-arm-final/native-ui/project-reopened.png>)

![Intel saved project reopened](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/macos-intel-final/native-ui/project-reopened.png>)

[Apple Silicon native checks](macos-arm-final/native-ui/results.json), [Intel native checks](macos-intel-final/native-ui/results.json), [Windows native checks](windows-native-final/results.json), [delivery manifest](delivery-manifest.json), [runner-time evidence](mac-runner-time.json).

## Next

Read `M2_FINAL_REPORT.md` and review the two ZIPs. Stop for the user's approval. Do not begin M3 or publish customer downloads.
