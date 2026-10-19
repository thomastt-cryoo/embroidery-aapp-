# M2 Etsy packaging — checkpoint 1

The requirement is **strictly fewer than 20,000,000 bytes for each complete platform ZIP**. No parts, reconstruction scripts, missing fonts or downloaded application assets are acceptable. Only Windows WebView2 may be obtained during installation.

## Audit and changes

The previous Windows installer was 241,316,900 bytes and included the offline WebView2 runtime. The previous universal Mac app ZIP was 53,515,689 bytes. The Mac executable contained both CPU architectures and their embedded assets.

The production frontend contains **458 files**, approximately 75.4 MB before native compression. Essential embroidery font JSON accounts for approximately 52.8 MB, font previews for 8.2 MB, and JavaScript for 14.1 MB. All remain included.

Changed Windows to Tauri's standard `downloadBootstrapper` mode. Added native release size optimization (`opt-level=z`, LTO, one codegen unit, stripped symbols, no debug information), retaining panic unwinding and every runtime feature. Added an optional asset-storage compression feature so the private build can compare internal Brotli compression against outer solid installer/disk-image compression.

Lossless PNG optimization saved **2,111,315 bytes** in the verified frontend. Every preview's decoded RGBA pixels, ICC profile, gamma and sRGB metadata are checked. Two uncertain metadata conversions were rejected and those originals restored. All other files, including fonts, JavaScript, CSS, WebAssembly and thread data, remain byte-identical before/after this compression step.

## Tests so far

- Source guard confirms the embroidery engine and approved M1 stylesheet are unchanged, with no new editing-state, project or platform logic changes.
- TypeScript and frontend production build passed. All 458 runtime files survived the optimizer checks.
- The first strict image checks rejected metadata changes and prevented release builds. The optimizer now restores any preview for which exact equivalence cannot be proven.
- Preliminary compression alone was insufficient for the original native executables: LZMA9 produced 24,055,608 Windows bytes and 28,371,492 universal Mac bytes. These are measurements of earlier binaries, not final customer ZIP sizes or proofs of a lower bound.

## Next

Complete the Windows installer and compare universal Mac app ZIP, disk-image and native installer compression on the actual Mac runner. Select one complete ZIP per platform, then install from those exact ZIP contents and verify core functionality. Final results will report whether each package actually meets the decimal-byte limit.

References: [Tauri size guidance](https://v2.tauri.app/concept/size/), [standard WebView2 bootstrapper](https://v2.tauri.app/distribute/windows-installer/), [OxiPNG lossless optimizer](https://github.com/oxipng/oxipng).
