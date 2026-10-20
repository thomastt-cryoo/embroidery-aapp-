> **Embrova update — 20 October 2026:** The current branded Windows download is [Embrova-Windows.zip](<C:/Users/mazin/Downloads/embroidry app/dist/Embrova-Updated-20261020/Embrova-Windows.zip>), **17,037,065 bytes**. This exact ZIP passed installation and launch on GitHub Windows; the installed product and window title are Embrova. Its new native icon was read back at all six ICO resolutions. The sidebar logo is 32 px, rounded and fitted without cropping. See [branding checkpoint](reports/embrova-branding/CHECKPOINT_2_WINDOWS.md) for checksums and evidence. The final branded Mac build is still being verified; the old Mac downloads below do **not** have the final Embrova branding. Do not mistake them for the new delivery.

> **Historical pre-Embrova Mac verification:** The UI-corrected Mac ZIP at `dist/Mac-Verified-Latest/Embroidery-Studio-macOS.zip` is **19,866,936 bytes**, SHA-256 `3381ddb207a0e535b780752c58957c3f95d68465921022ab90d306ea54d5e33d`. Its installed native conversion, rendering, playback, hoop selection, stitch editing, project save/reopen and PES export passed on both ARM and Intel GitHub Macs. See [M3 report](M3_INSTALLATION_REPORT.md) for actual screenshots and remaining installation/Gatekeeper limitations. The owner has since made the repository public; the private-repository and pre-M3 statements below are historical. The original delivery files below remain archived unchanged.

# M2 — Embroidery Studio packaging and compatibility report

20 October 2026. **Both complete ZIPs are below 20,000,000 bytes. The Mac preview issue is fixed, and native workflows passed on Windows, Apple Silicon Mac and Intel Mac.** Commercial signing remains unfinished, so these are private review builds. Nothing was published publicly. Work stops at M2 for approval; M3 has not started.

## Finished downloads

| Platform | Complete download | Exact ZIP bytes | Below 20,000,000 bytes |
|---|---|---:|---|
| Windows x64 | [Windows ZIP](<C:/Users/mazin/Downloads/embroidry app/dist/M2-Etsy/Embroidery-Studio-Windows.zip>) | **16,955,299** | Yes; 3,044,701 bytes spare |
| macOS, Intel and Apple Silicon | [Mac ZIP](<C:/Users/mazin/Downloads/embroidry app/dist/M2-Etsy/Embroidery-Studio-macOS.zip>) | **19,870,862** | Yes; 129,138 bytes spare |

The delivery folder contains exactly these two ZIPs. Each includes one complete installer, short instructions, the licence and notices. No extra parts, reconstruction scripts or technical setup are required by the packages. Working name: **Embroidery Studio 1.4.0**.

Windows customers extract and run **Install Embroidery Studio.exe**, which is **16,948,891 bytes**. Tauri's standard bootstrapper downloads Microsoft WebView2 only when it is missing. No other application components are downloaded. Embroidery processing works offline after installation.

Mac customers extract and open **Install Embroidery Studio.pkg**, which is **19,855,347 bytes**, then launch the app from Applications. The standard Apple installer includes both processor architectures and all runtime assets. A PKG replaces the larger DMG for this Etsy delivery. The configured minimum OS is macOS 13; actual native tests ran on macOS 14 Apple Silicon and macOS 15 Intel.

## Optimizations and preservation

- Removed the Windows offline WebView2 installer and retained the normal bootstrapper.
- Optimized native release settings, stripped debug symbols, and used solid LZMA compression for Windows. Required runtime dependencies remain.
- Losslessly optimized 137 preview images, saving **2,111,315 bytes**, with identical pixels and colour profiles. Two other previews were retained unchanged when metadata equivalence could not be proven.
- Compared complete Mac app ZIPs, disk images and native installers. The final build compresses across the duplicated architecture assets using a longer compression window. Every decoded installer payload byte remained identical; Apple's native extraction verified identical files, permissions and signatures. Customers run only a normal PKG.
- Kept development dependencies, source maps, test tools, screenshots and reports outside customer packages.

All **458 frontend runtime files**, including fonts, WebAssembly and thread data, remain. The embroidery engine, stitch geometry, editing/project logic and approved M1 layout were preserved. Final application source is `2204598af6c3bfcd9667d68d91958e21cd8d1fc5`; later commits repair test drivers and document evidence.

## Mac preview fix

The virtual Mac's WebGL contexts were immediately lost, even in an independent native WebKit application containing no embroidery code. Embroidery Studio now automatically draws through Canvas 2D when WebGL is unavailable or already lost at startup. It draws the **existing stitch geometry and colours**; it does not change embroidery processing. Healthy graphics retain the existing WebGL renderer.

The fallback preserves pictures, layers, selection, hoop graphics, pan/zoom and simulation. Cached paths and drawing on demand avoid continuous idle rendering. Native screenshots on both Mac architectures prove visible stitches with the imported reference picture hidden.

## Actual ZIP installation and native tests

| Native application check | Windows | Apple Silicon Mac | Intel Mac |
|---|---|---|---|
| Install actual ZIP contents and launch | Passed | Passed | Passed |
| Visible stitches | Passed, healthy GPU and lost-WebGL fallback | Passed | Passed |
| PNG conversion to 1,374 stitches / six objects | Passed | Passed | Passed |
| Stitch editing | Passed, with Undo | Passed | Passed |
| 100 × 100 mm hoop selection | Passed | Passed | Passed |
| Simulation from zero to completion at 50× | Passed | Passed | Passed |
| Save editable project through native dialog | Passed | Passed | Passed |
| PES export through native dialog | Passed | Passed | Passed |
| Reopen saved project | Passed | Passed | Passed |

Windows completed **11 native checks** against the final ZIP and relaunched normally without debugging. Its installed runtime served all 458 files: 457 exact hashes plus equivalent Tauri-normalized HTML. At the user's latest request, its computer-use session was reset. Windows testing is finished.

Both Mac architectures completed **eight native workflow checks**, in addition to installation, signatures, launch and existing project/PES loading. These are actual installed native applications on GitHub Mac runners, not browser substitutes. Their native runs both succeeded:

- [Apple Silicon test run](https://github.com/thomastt-cryoo/embroidery-aapp-/actions/runs/39346926486)
- [Intel test run](https://github.com/thomastt-cryoo/embroidery-aapp-/actions/runs/39346935897)

The sample PNG produced **1,374 stitches and six editable objects**. Pull compensation changed **0.15 → 0.35 mm**, then returned to **0.15 mm**; Windows used Undo. All three native applications exported a **4,072-byte PES file** with a valid header. Mac reopening was tested after starting an empty document, so an already visible stitch count could not accidentally satisfy that check. Saved projects and exports are retained with the evidence.

Earlier failed runs remain recorded as failures. Test-driver problems included Safari slider key differences, injected text timing, menu/focus handling and a saved-file location assumption. The native Mac dialog sometimes remembered the image folder; the test incorrectly searched only Documents. Fixing these tests did not rebuild or alter the sealed customer ZIP. One Intel OCR diagnostic also timed out; the final Intel run passed that check and the full workflow.

## Supporting regressions

Software rendering passed **13 integration checks**, and a genuinely created then lost WebGL context passed **14 checks**, including partial simulation/rewind, transparency, image ordering, pan/zoom, idle redraw and a 100,001-stitch fixture. **59 controller/geometry tests** passed. An initial overloaded parallel controller run timed out; its isolated rerun passed all 36 controller tests, with the other 23 tests passing separately.

Production browser fallback workflows passed all **13 export formats**, **11 machine-format readbacks**, PNG/G-code validation, editable project save/reopen, hoop, simulation and three window sizes, with external HTTP(S) blocked. These browser workflows preceded only the final additional startup guard; that guard has separate lost-context integration and final native testing.

Earlier M2 evidence remains applicable: **650 editor tests, 32 script tests, Windows native Rust 92 library + 18 API tests, and Mac native Rust 96 tests** passed. The unchanged engine's M1 baseline was **899 passed with 22 upstream skips**. Full engine suites were not repeated solely for compression. Source/identity protection and TypeScript checks passed. Final archive CRCs, contents, legal text, exact hashes, size limits and native evidence checks all passed.

## Real application screenshots

Final installed Windows application, launched normally:

![Windows normal launch](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/windows-native-final/normal-launch.jpg>)

Apple Silicon Mac after saving, exporting and reopening:

![Apple Silicon native application](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/macos-arm-final/native-ui/project-reopened.png>)

Intel Mac after saving, exporting and reopening:

![Intel native application](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/macos-intel-final/native-ui/project-reopened.png>)

## Remaining distribution limits

**Signing is the remaining customer-distribution blocker.** Windows is unsigned. Mac has an ad-hoc signature, without Apple Developer ID or notarization. Operating systems may block or warn about these builds. Clean consumer trust-prompt journeys were not certified. The archives meet the size and completeness requirements, but they are not yet certified for a frictionless commercial installation. Re-signing/repackaging will require renewed size checks, especially with the Mac archive's small margin.

Windows already has WebView2; the missing-runtime branch was checked in installer configuration without removing the shared runtime or using a clean VM. macOS 13 itself, physical Mac GPU behaviour, physical embroidery-machine sew-out and network machine transfer were not tested. Native virtual Mac testing is clearly distinguished from physical consumer Mac testing.

Application identity remains `io.github.thomasttcryoo.embroiderystudio`, with separate shortcuts, uninstall identity, protocol and application directories. Updates are disabled, with no original Lilo update channel configured. The installed Lilo executable, its protocol and all 12 file defaults remain unchanged. Upstream `Kadwood/lilo` is reference-only, with pushing disabled. Only the approved private repository received changes.

Measured Mac job elapsed time across M2 was **156 minutes 42 seconds**, including failed/superseded jobs that ran, below the stated 200-minute ceiling. This is measured elapsed time, not a verified billing balance. The account's remaining free allowance was unavailable. Only standard runners were used; no paid larger runner or billing setting was enabled. No Mac jobs remain running.

## Evidence and checkpoints

- [Checkpoint 1: audit](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/01-size-audit.md>), [checkpoint 2: earlier packages](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/02-optimized-packages.md>), [checkpoint 3: earlier verification](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/03-final-verification.md>), [checkpoint 4: graphics diagnosis](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/04-mac-graphics-diagnosis.md>), [checkpoint 5: preview/size fixes](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/05-native-preview-and-size-fix.md>), [checkpoint 6: final verification](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/06-final-native-verification.md>)
- [Exact sizes, installer contents and SHA-256 hashes](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/delivery-manifest.json>)
- [Windows final native results](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/windows-native-final/results.json>), [Apple Silicon results](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/macos-arm-final/native-ui/results.json>), [Intel results](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/macos-intel-final/native-ui/results.json>)
- [Lossless Mac installer verification](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/macos-fixed/mac-lossless-pkg-compression.json>), [source/runtime preservation](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/asset-preservation.json>), [installation isolation](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/windows-isolation.json>), [runner-time evidence](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/mac-runner-time.json>)
- [Private universal Mac build artifact](https://github.com/thomastt-cryoo/embroidery-aapp-/actions/runs/39332712597/artifacts/12225119001): compilation, 96 Rust tests, packaging and native installation passed; its original all-in-one job failed later in the UI driver. The two successful final native runs reused that exact ZIP.

The GitHub test artifacts have short retention. Both final customer ZIPs, screenshots, saved files and evidence have also been copied to this computer. Earlier larger packages are superseded. **M2 stops here for approval; M3 has not begun.**
