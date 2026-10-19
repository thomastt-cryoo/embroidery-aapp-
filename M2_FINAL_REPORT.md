# M2 — Etsy packaging results

**Windows meets the size requirement. macOS remains above it.** Native Mac canvas preview also remains unverified: the Intel virtual runner reports WebGL unavailable. Each platform has one complete ZIP. M3 has not started. Working name: **Embroidery Studio 1.4.0**. Updated 20 October 2026. Nothing was published publicly.

## Finished downloads

| Platform | Complete ZIP | Exact bytes | Below 20,000,000? |
|---|---|---:|---|
| Windows x64 | [Windows ZIP](<C:/Users/mazin/Downloads/embroidry app/dist/M2-Etsy/Embroidery-Studio-Windows.zip>) | **16,962,744** | **Yes**, 3,037,256 bytes to spare |
| macOS 13+, Intel and Apple Silicon | [macOS ZIP](<C:/Users/mazin/Downloads/embroidry app/dist/M2-Etsy/Embroidery-Studio-macOS.zip>) | **38,675,724** | **No**, 18,675,724 bytes over |

Both files are retained on this computer. The delivery folder contains exactly these two ZIPs. Each includes an installer, plain instructions, licence and notices. No package parts or reconstruction scripts are required.

Windows customers extract the ZIP and run **Install Embroidery Studio.exe**. The complete application is included. If WebView2 is missing, Tauri's standard bootstrapper downloads it from Microsoft during installation. No other application components are downloaded. Embroidery processing works offline after installation.

Mac customers extract the ZIP and open **Install Embroidery Studio.pkg**. Apple's standard installer places the complete universal application in Applications. Both processor architectures, all fonts and runtime assets are included; no component downloads are required.

## Optimizations performed

- Removed the bundled Windows offline WebView2 installer and enabled the standard download bootstrapper.
- Optimized native release builds for size with whole-program optimization, stripped symbols and no debug information. Preserved panic unwinding and existing runtime capabilities.
- Used solid LZMA with a 64 MB dictionary for Windows. Compared raw embedded assets against Tauri's internal storage compression for Mac.
- Losslessly optimized 137 PNG previews, saving **2,111,315 bytes**. Verified identical decoded pixels and colour profiles. Restored two original previews when exact metadata equivalence could not be proven.
- Compared complete Mac app ZIP, UDZO/UDBZ/ULMO disk-image ZIPs and native PKG compression. The best uses raw assets and Apple's latest PKG compression, targeting the existing minimum macOS 13.
- Kept development dependencies, source maps, test tooling and reports outside customer packages. Required runtime assets, fonts, WebAssembly and thread data remain included.

All **458 frontend files** remain. The installed Windows application served all 458: **457 matched exact final-build SHA-256 hashes**; the HTML wrapper had identical elements and attributes after Tauri's normal HTML serialization. Source checks confirm the embroidery engine, editing/project logic and approved M1 interface were preserved.

## Mac size limitation and recommendation

The smallest complete Mac package built and installation-tested is **38,675,724 bytes**. Its PKG alone is **38,647,922 bytes**, already above the ZIP ceiling before instructions and archive overhead. The earlier M2 application ZIP was 53,515,689 bytes.

The complete frontend includes roughly **52.9 MB of essential font/data JSON**, plus JavaScript, previews and WebAssembly before compression. Tauri embeds frontend assets in each architecture's executable; the universal Mac application retains both Intel and Apple Silicon slices. Standard Mac package compression preserving that full application did not reach 20,000,000 bytes.

| Complete universal Mac delivery tested | ZIP bytes |
|---|---:|
| Raw assets, application ZIP | 53,441,507 |
| Internally compressed assets, application ZIP | 43,702,214 |
| Raw assets, UDZO disk image | 59,926,947 |
| Raw assets, UDBZ disk image | 47,458,369 |
| Raw assets, ULMO disk image | 41,479,399 |
| Internally compressed assets, best disk image | 42,204,065 |
| **Raw assets, native PKG** | **38,675,724** |

These are measured candidates, not a mathematical minimum for every possible future implementation. Further reductions would require a different asset-packaging design or compatibility changes beyond the verified compression work. No fonts, architectures or features were removed to force compliance.

**Recommendation:** retain the complete Mac ZIP and deliver it through a private download service or storefront accepting at least 39 MB. Customers still download one ZIP, extract and install. This requires a delivery decision; it is not an Etsy-sized attachment. Etsy's [official digital-listing help](https://help.etsy.com/hc/en-us/articles/115015628347-How-to-Manage-Your-Digital-Listings) confirms its 20 MB per-file limit. No customer-facing upload or publication has been performed.

## Tests and results

| Check | Windows | macOS |
|---|---|---|
| ZIP integrity and hashes | Passed | Passed |
| Installation from actual final ZIP | Passed, extracted installer exit code 0 | Passed, Apple's PKG installer reported success |
| Normal native launch | Passed, debugger removed | Passed on Apple Silicon and Intel runners; native canvas has a separate graphics blocker |
| Native project/PES loading | Passed | Passed; names and 1,374 stitches checked in real screenshots |
| Detailed native workflows | Nine checks passed | **Five passed:** PNG conversion, hoop, project save, PES export and reopening. **Canvas preview blocked** on the VM |
| Production image/hoop/simulation/project/export workflows | Nine passed | Nine passed in Chromium on actual macOS |
| Native Rust tests | 92 library + 18 API passed | 96 library passed |
| Runtime assets | All 458 retained and served | All 458 retained in both builds; PNG equivalence passed |
| Original Lilo isolation | Executable, handler and 12 file defaults unchanged | Separate application identity verified |

The native Windows application converted the PNG into **1,374 stitches** and six editable objects. Pull compensation changed **0.15 → 0.33 mm**, then Undo restored **0.15 mm**. A **100 × 100 mm** hoop was selected. Native Save wrote a valid `.lilo` project; reopening preserved it. Native PES Save As wrote **4,072 bytes** with the expected header. Simulation completed at 50×. A final normal launch reopened the saved design without a debugger or development server.

Production browser checks on **both operating systems** blocked external HTTP(S) and used the real engine, file inputs and downloads. All **13 exports**, **11 readable machine-format round-trips**, PNG/G-code validation, editable project save/reopen, hoop, simulation and three window sizes passed. Browser and native desktop results are kept distinct.

On **macOS 15.7.9 Intel**, the actual installed ZIP also passed native PNG conversion to 1,374 stitches, 100 × 100 mm hoop selection, project saving through the native sheet, a **4,072-byte PES export**, and reopening that saved six-object project. That native run is deliberately recorded as **partial**, with a failing overall workflow status, because canvas graphics remained blocked. Native visual editing and simulation are not signed off. macOS 14.8.9 Apple Silicon separately passed installation, launch and saved-project/PES loading.

Earlier approved regression evidence remains applicable: 650 editor tests and 32 script tests passed in M2; the unchanged engine's M1 baseline was 899 passed with 22 upstream skips. The full engine/editor suites were not rerun solely for compression. Packaging protection, production build, TypeScript, guide and version checks passed.

## Actual application screenshots

Installed Windows application, normal launch from this final ZIP build:

![Windows normal launch](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/windows-native/normal-launch.jpg>)

Native Windows PES export:

![Native Windows export](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/windows-native/export-pes.png>)

Actual Intel Mac application installed from the ZIP: PNG conversion and hoop selection worked, but native graphics failed on the VM. This screenshot shows the limitation directly:

![Native Mac graphics limitation](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/macos-intel-first/native-ui/converted.png>)

Separate production browser editing/hoop check on that Mac runner:

![Mac browser editing and hoop](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/macos/acceptance/editing-and-hoop.png>)

## Issues, limits and isolation

- **Mac size remains unresolved.** Its verified ZIP cannot be one Etsy attachment. No splitting, reconstruction or application-component download workaround was used.
- **Native Mac preview is not validated.** After dismissing the welcome, the Intel runner's native WebView showed “The canvas needs WebGL” while the renderer read null shader-precision information. Native conversion still produced 1,374 stitches and six objects, and hoop selection worked. The independent diagnostic below reproduced graphics failure without loading the embroidery application. A consumer Mac preview test remains necessary. No graphics or engine change was made to bypass the failure. Browser software-rendered tests are not a substitute for native preview validation.
- **Signing remains unfinished.** Windows is unsigned; Mac is ad-hoc signed without Apple Developer ID/notarization. These are private review builds. Clean consumer trust-prompt journeys remain untested. Intel native launch and file loading are now verified.
- Windows already has WebView2. The missing-runtime branch was checked in installer configuration, not exercised by removing the shared runtime or using a clean VM.
- Early Windows test interception disrupted native IPC saving. Removing interception and fully reloading the WebView resolved it. All recorded native checks were repeated successfully without interception; no app patch was needed.
- The first PKG experiment omitted its minimum-OS argument. Specifying the existing macOS 13 target enabled stronger compression and successful installation.
- Physical machine sew-out and network machine transfer were not tested.

Identity remains `io.github.thomasttcryoo.embroiderystudio`, with separate shortcuts, uninstall entry, directories and protocol. Automatic updates are disabled; no Lilo update endpoint is configured. **Your installed Lilo and upstream `Kadwood/lilo` were not changed.** All pushes/artifacts remain in your approved private repository.

## WebGL investigation and fix plan

A separate, default native **WKWebView** on the Intel runner reproduced the failure with **no embroidery code or assets loaded**. WebGL 1 and WebGL 2 both created contexts that were immediately lost, returned no shader precision, and failed a simple green-pixel readback. Turning antialiasing off made no difference. The runner exposes an **Apple Paravirtual device**. This proves this graphics failure can occur independently of the packaged application; it does not establish that a physical Mac works.

The next validation step is the exact customer ZIP on a **physical Mac or a Mac runner with working native graphics**. Verify visible stitches, zoom/pan, realistic preview and simulation, then saving/reopening and exports. If a graphics-capable Mac reproduces an app-specific failure, investigate the Tauri window and renderer initialization and fix that layer while preserving the engine and M1 interface. Hiding the error or changing stitch processing is not a valid resolution.

[Standalone diagnostic results](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/graphics-probe/native-webkit-graphics.json>) · [private diagnostic run](https://github.com/thomastt-cryoo/embroidery-aapp-/actions/runs/39322724108). The [WebGL specification](https://registry.khronos.org/webgl/specs/latest/1.0/) documents null query results when a context is lost.

## Evidence and checkpoints

- [Checkpoint 1: audit/preservation](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/01-size-audit.md>)
- [Checkpoint 2: packages/installation](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/02-optimized-packages.md>)
- [Checkpoint 3: final verification](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/03-final-verification.md>)
- [Checkpoint 4: native Mac graphics diagnosis](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/04-mac-graphics-diagnosis.md>)
- [Windows native results](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/windows-native/results.json>) · [installation isolation](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/windows-isolation.json>)
- [Windows production checks](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/windows-acceptance/results.json>) · [Mac production checks](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/macos/acceptance/results.json>)
- [Mac ZIP installation](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/macos/mac-zip-install.json>) · [Mac native screenshot checks](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/macos/mac-native-core-from-zip.json>)
- [Final native Intel Mac results](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/macos-intel/native-ui/results.json>) · [native UI test run, partial](https://github.com/thomastt-cryoo/embroidery-aapp-/actions/runs/39323318021)
- [Exact delivery sizes, contents and SHA-256 hashes](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/delivery-manifest.json>)
- [Private Mac build/comparison](https://github.com/thomastt-cryoo/embroidery-aapp-/actions/runs/39313542113) · [PKG install verification](https://github.com/thomastt-cryoo/embroidery-aapp-/actions/runs/39318694545)

The earlier larger M2 packages are archived separately and superseded by these two ZIPs. **Work stops at M2 for approval. M3 has not begun.**

Recorded Mac job elapsed time across M2 is **52 minutes 51 seconds**, including superseded runs that actually started. Queue-only cancellations are excluded. This is below the stated 200-minute ceiling, but the account's remaining free/billing allowance could not be verified. No paid larger runner or billing setting was enabled. [Build time evidence](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/actions-build.json>) · [native verification time](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/actions-zip-verification.json>) · [graphics diagnostic time](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/actions-graphics-probe.json>).
