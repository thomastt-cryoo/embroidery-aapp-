# Windows Sew order correction — 20 October 2026

The supplied recording showed the right-hand Sew order panel. Hidden reorder buttons still occupied horizontal space, squeezing names to one or two letters. Help, layer actions, thread groups and individual shapes competed for the same space. Clicking the already-selected Stitches layer had no visible effect.

## Changes

- Shape names now have their own line. Stitch type, count, details and reorder actions sit underneath.
- Layers and colour blocks have distinct layouts. Reorder actions stay visible, with unavailable directions dimmed and explained by tooltips.
- Clicking the active Stitches heading, its larger disclosure button, or pressing Enter on its focused tree row expands/collapses its contents. Clicking a different layer selects it. These actions do not change the design.
- Help and advanced layer actions remain available under **Layer options & help**.
- The new presentation and heading behavior apply on Windows. No macOS build, runner or installation was requested or performed for this correction.
- The embroidery engine, project/state implementation, approved main interface stylesheet, formats and runtime resources remain unchanged.

## Verification

- **44 existing and new Sew order tests passed**, including keyboard navigation, rename, layer operations and a Windows heading-response regression. The initial parallel run exceeded the existing 20-second initialization limit in three first tests; the sequential rerun passed all tests without increasing timeouts.
- **TypeScript checks passed.** Identity and protected-source checks passed.
- Browser interaction checks passed for Stitches expansion, heading clicks, visibility, lock, shape/block/layer reordering, undo and details.
- At **960×600, 1280×800 and 1440×900**, the panel had no horizontal overflow. Names received 123–157 CSS pixels instead of collapsing to initials. Long names still use a tooltip and ellipsis when necessary.
- Production frontend checks passed: PNG conversion into **1,374 stitches**, hoop selection, playback, **13 exports**, project save/reopen with the same stitch count, and operation with external HTTP(S) blocked. Eleven machine formats were reread, G-code output checked, and PNG signature checked. No browser runtime errors were recorded.
- Build asset checks retained **458 runtime files**, including fonts, WebAssembly and thread data. All 137 preview images preserved their decoded pixels and colour interpretation after lossless compression.

Native installer/app verification and final package details are recorded in `FINAL_REPORT.md` when completed. This README alone is not a claim that installation has passed.

## Evidence

- `recording/`: frames extracted from the user's recording.
- `browser-ui-results.json` and `windows-*-light.png`, `windows-1440-dark.png`: interactive browser layout checks with the real engine; development adapter used only for storage/dialogs.
- `unit-tests.txt`, `typecheck.txt`, `preservation-check.txt`: checks and results.
- `production-regression/`: screenshots, 13 exports, saved project and production results.
- `asset-preservation.json`, `windows-build.txt`: build evidence.

The open design was saved separately as `Recovered-open-design.lilo` before restarting, preserving the original file. It is a recovery artifact, not part of the customer installer.
