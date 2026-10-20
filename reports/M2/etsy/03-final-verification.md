# M2 Etsy packaging — checkpoint 3

**Historical checkpoint, superseded.** The Mac size and preview blockers below were resolved in checkpoint 5. This earlier verification remains as evidence of what passed and failed at that time. Use the root `M2_FINAL_REPORT.md` for current delivery files.

## Completed

Final delivery contains exactly one complete Windows ZIP and one complete universal Mac ZIP. Windows: **16,962,744 bytes**, below the required 20,000,000-byte ceiling. Mac: **38,675,724 bytes**, above it. Both archives passed CRC checks, expected-file checks, installer-header checks and legal-text preservation. Exact SHA-256 hashes are in [delivery-manifest.json](delivery-manifest.json).

No engine, editing/project logic or approved M1 layout change was made for this optimization. Source protection passed. The original Lilo executable remains SHA-256 `2FE59440A3441F001B88835B0620FF67B2FB8C7AF47E36D6864FD11920D1811C`; its protocol and 12 file defaults remain intact. Only the user's private distribution repository received pushes.

## Tests

Windows actual ZIP installer installed successfully. All nine native checks passed, including a normal release launch without a debugger or development server. The installed app served every runtime asset. Browser production tests passed separately on both operating systems with external HTTP(S) blocked, including all export formats and project round-trips. Native Rust results: 110 Windows tests, 96 Mac tests passed.

Mac final PKG installed successfully using Apple's native installer on macOS 14.8.9 ARM. Both `x86_64` and `arm64` were verified in its executable, and the ad-hoc signature passed verification. Actual native saved-project and PES loads showed 1,374 stitches and the correct names; screenshots were inspected and Apple Vision independently confirmed them. The first-run welcome is visibly present in those screenshots and obscures much of the canvas.

Final native Mac Accessibility testing ran on a standard Intel runner using the exact ZIP. **Five checks passed:** PNG conversion to 1,374 stitches, 100 × 100 mm hoop selection, native project saving with six objects, 4,072-byte PES export and saved-project reopening. Its result is explicitly **partial**, and the workflow is red because native preview remains blocked. See [final results](macos-intel/native-ui/results.json). Native visual editing/simulation are not signed off.

The first Save driver could not locate an XPC-hosted native field; a later attempt scanned too broadly for the saved fixture and was cancelled. The final driver preserves dialog focus, confirms the observed default filename, searches only expected test output folders, and has a three-minute step limit. All five recorded native functional checks passed with that corrected driver. These were test-tool repairs, not application changes.

The native canvas reports WebGL unavailable on the virtual runner. A separate default WebKit probe reproduced immediate context loss without loading any app code, as described in [checkpoint 4](04-mac-graphics-diagnosis.md). Consumer Mac preview remains unverified, and browser software rendering is not a substitute.

## Limits and next

The smallest complete Mac ZIP tested exceeds Etsy's ceiling by **18,675,724 bytes**. Delivering this unchanged ZIP through a channel accepting at least 39 MB preserves one application download per platform. No features, font assets or architectures were removed, and no application-component downloads were introduced. No customer-facing delivery was published.

Windows lacks a signing certificate, and Mac lacks Developer ID/notarization. Clean consumer trust prompts, native Mac canvas rendering, absent-WebView2 installation and physical sew-out remain untested. Intel execution is verified for launch, project/PES loading, image conversion, hoop, save, export and reopening. Reports and the two ZIPs are retained locally. Stop at M2 for approval; do not begin M3.

![Actual final Windows normal launch](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/windows-native/normal-launch.jpg>)

![Actual Mac ZIP installation and native project load](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/macos/native-macos-desktop.png>)
