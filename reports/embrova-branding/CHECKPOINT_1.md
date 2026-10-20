# Embrova branding — source and layout checkpoint

20 October 2026

## Completed

- Renamed the Windows and Mac application, native window/menu titles, tray labels, installer/product metadata, shortcuts, current help pages, dialogs, export wording, sample lettering and customer package names to **Embrova**.
- Used the owner's complete supplied 2400 x 1792 JPEG. The original is preserved in `docs/brand/embrova-original.jpg`. Native icon formats are generated with the complete composition fitted inside the icon; no flower, leaves or wordmark are cropped. Rounded corners affect only the surrounding background.
- Following the owner's size correction, the sidebar uses a **32 x 32** rounded logo beside the name on both Windows and Mac. Its image fit is `contain`, not a crop.
- Updated application icons, Windows installer/executable icons, the Mac icon and monochrome menu-bar template, the first-launch logo and browser favicon.
- Retained the internal application identifier and existing settings keys for compatibility. New projects default to Documents/Embrova; existing projects in the previous temporary-name folder remain discoverable and accessible without moving, overwriting or deleting anything. The original Lilo folder is not scanned by that compatibility path.
- Engine files and approved M1 processing/state behavior remain unchanged except product wording. The native shell has a narrowly scoped old-folder compatibility addition.

## Tests

- 34 frontend layout/navigation checks passed with Windows and Mac user agents, both themes, six window widths and compact editor rails. Checks also confirm that the logo loads, remains small, has rounded corners and uses `contain`.
- 130 relevant UI, guide, project, hoop and update-interface tests passed.
- TypeScript checks passed.
- 16 native project tests passed, including a new test retaining old projects while rejecting unrelated/Lilo folders.
- Seven package/report contract tests passed; Codemagic schema and guide generation/checks passed.
- Source/identity/offline/update-channel preservation checks passed.

Screenshots in `frontend/` are local Chromium frontend checks, not native installation evidence. The prior native checks on both Mac architectures remain preserved in the M3 report and refer to the pre-Embrova package.

## Next

Build complete Windows and universal Mac customer ZIPs, measure their exact sizes, check branding from the installed packages, and record new-package test results. Strict size gates remain enabled; no features or required runtime assets will be removed to fit Etsy. No new package size or installation pass is claimed at this checkpoint.
