# M2 Etsy packaging — checkpoint 2

**Historical checkpoint.** Sizes and graphics limitations below describe an earlier build. Checkpoint 5 supersedes them; use the root `M2_FINAL_REPORT.md` for current delivery files.

## Completed

Built the optimized Windows installer and compared complete universal Mac app ZIPs, three standard disk-image compression formats, and the native Mac installer. No engine, editing-state or M1 interface changes were needed.

Windows ZIP: **16,962,744 bytes**, containing the 16,956,277-byte installer and customer instructions/licence/notices. WebView2 uses Tauri's standard download bootstrapper when absent; its offline installer is no longer bundled.

Smallest complete Mac ZIP so far: **38,675,724 bytes**, containing a **38,647,922-byte native PKG** and instructions/licence/notices. The PKG contains the universal Intel/Apple Silicon application. Native `pkgbuild --compression latest` needed the explicit existing minimum macOS version, **13.0**. The first comparison omitted that argument; fixing it improved the best disk-image ZIP measurement of 41,479,399 bytes.

## Tests and evidence

- Windows ZIP integrity and exact extracted-installer hash passed. Installed **that extracted installer** successfully, then verified the installed executable against the build. Original Lilo bytes, protocol handler and all 12 file defaults remain unchanged.
- All **nine native Windows checks** passed: PNG upload/conversion, project saving, stitch editing/Undo, 100 × 100 mm hoop, native PES export, reopening, simulation, complete runtime assets and final normal launch. See [results](windows-native/results.json) and [screenshot](windows-native/normal-launch.jpg).
- Verified all **458 installed runtime files** through the native asset server: 457 exact SHA-256 matches plus semantically identical Tauri-normalized HTML. All fonts, previews, thread data, CSS, JavaScript and WASM survived.
- Windows native tests: **92 library + 18 API passed**. Mac native library: **96 passed**.
- Production browser acceptance: **nine checks on each OS**, including 13 exports, 11 readbacks, project save/reopen, hoop, simulation, layouts and blocked external HTTP(S).
- Actual Mac runner extracted the final Mac ZIP, installed its PKG with Apple's installer, verified the ad-hoc signature, launched the native app, and loaded a saved project and PES. Apple Vision confirmed both names and 1,374 stitches in real screenshots. See [native ZIP evidence](macos/mac-native-core-from-zip.json) and [installer evidence](macos/mac-package-install.txt).

## Issues and limitations

The Mac ZIP remains **18,675,724 bytes over** the requested ceiling. All compared complete packages exceeded 20,000,000 bytes; the compression table is in [candidate evidence](macos/mac-package-candidates.json), with the improved PKG measurement [here](macos/mac-pkg-comparison.json). Nothing was split or removed to force compliance.

An early Windows test intercepted native IPC while blocking external HTTP. This damaged its raw save request. Removing interception and fully reloading the WebView resolved the test failure. All recorded native checks were repeated successfully without interception; no application change was made. Offline network blocking remains separately verified by production browser acceptance.

Windows already has WebView2, so the missing-runtime download branch is configuration-verified, not tested on a clean VM. Windows is unsigned; Mac is ad-hoc signed without Developer ID/notarization. Consumer trust prompts and Intel execution remain untested.

## Next

Finish the additional native Mac accessibility check using permissions already present on the runner, preserve its honest results and actual screenshots, and publish the final local report and two ZIPs. Recommend one complete Mac ZIP through delivery that accepts its measured size. Do not begin M3.
