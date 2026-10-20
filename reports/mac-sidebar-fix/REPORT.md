# Mac sidebar correction — 20 October 2026

## Completed

Corrected the Mac sidebar spacing that clipped “Embroidery Studio,” hid navigation icons and wrapped navigation labels in the owner's native Mac screenshot. The older horizontal toolbar reserved 94 pixels on the left for Mac window buttons. Its CSS specificity overrode the newer vertical sidebar's 12-pixel padding.

Added a small Mac-only stylesheet, loaded after the existing styles. The normal rail now has 12-pixel side padding and the compact rail 8 pixels. Existing top spacing for Mac window buttons remains. The approved interface, embroidery engine, project state and export processing are unchanged. Windows styles are unchanged.

## Verification

- Reproduced the defect before changing CSS using the real frontend, its development Tauri adapter and the actual `data-titlebar="overlay"` attribute. Recorded 94-pixel left padding, brand overflow and wrapped labels.
- After correction, 34 frontend layout/navigation checks passed: Mac and Windows user agents, light and dark modes, six widths from 960 to 1440 pixels, compact editor rail, and Home/Pixel art/Converter navigation. All five navigation labels, including Studio Link, were checked for clipping/wrapping in the full rail.
- TypeScript checks passed.
- Package protection check passed, including separate identity, disabled updates, offline runtime and protected M1 sources.
- No export tests were repeated. No installed Windows app was opened. No cloud build or Mac session was started for this correction.

These are Chromium frontend checks performed on Windows with the Mac title-bar setting. They are **not native macOS screenshots or native installation tests**. Studio Link's backend was not tested; it needs native IPC unavailable in this development adapter.

## Evidence

- `baseline.json`: measurements reproducing the original defect.
- `before-mac-overlay-1024.png`: original layout reproduced in the frontend harness.
- `browser-results.json`: 34 successful layout/navigation checks, zero browser page errors.
- `mac-overlay-1024-light.png` and `mac-overlay-1024-dark.png`: corrected full navigation.
- `mac-overlay-960-light.png` and `mac-overlay-960-dark.png`: compact navigation.
- `mac-overlay-1440-light.png` and `mac-overlay-1440-dark.png`: larger window.
- `mac-editor-rail.png`: compact editor rail.
- Reproducible check: `node scripts/desktop-sidebar-check.mjs` with the development server running on port 5181. Set `NAV_URL` to use another local server. `NAV_BASELINE=1` reproduces the defect on the source before this correction.

## Remaining limitation / next step

The existing downloaded Mac ZIP has not changed. A new Mac build is needed to package this source correction. Native confirmation of the corrected rail remains pending that build; no new cloud run has been requested. The user asked not to repeat export checks. Prior successful Mac browser export results stand, while the installed app's native Save dialog remains unverified.

Original reference repository `Kadwood/lilo` was not changed or pushed to.
