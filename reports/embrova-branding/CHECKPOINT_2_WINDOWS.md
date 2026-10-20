# Embrova delivery checkpoint — Windows verified; Mac pending

20 October 2026 (Dubai time)

## Completed

The fresh Windows ZIP contains `Install Embrova.exe`, start instructions, licence and credits. It was rebuilt from source `1a524f3c0609f8d8e647968ad4ac2cc23ed58fd9`, including the Embrova name, supplied complete flower/wordmark, 32 px sidebar logo with rounded corners, and Windows colour tray icon. The engine and approved editing behavior are preserved.

Fresh delivery: `dist/Embrova-Updated-20261020/Embrova-Windows.zip`.

Exact ZIP size: **17,037,065 bytes**, below 20,000,000. SHA-256: `1c783fd2ddcd98519d09aefad023c9bf08774f170f809ae1c238b5372864f43b`.

## Tests and results

- ZIP integrity and byte-for-byte installer readback passed.
- Actual ZIP extraction, silent installation and native launch passed on GitHub Windows, run [39385165988](https://github.com/thomastt-cryoo/embroidery-aapp-/actions/runs/39385165988). The installed executable product name and observed window title were **Embrova**. Evidence: `windows-delivery-install/windows-install-results.json`; its checksum matches this exact ZIP.
- All 459 runtime assets were retained. Lossless PNG processing preserved pixels/profiles; remaining runtime files are unchanged by that optimization (`windows-runtime-assets.json`). WebView2 uses the standard conditional bootstrapper.
- Source/layout verification is recorded in CHECKPOINT_1.md. Frontend screenshots in `frontend/` show the small, rounded logo and are explicitly browser checks, not native Mac installation screenshots.

## Issues and limitations

The owner reported that an earlier delivered file showed old branding. The earlier link was reused during successive builds, and we cannot establish from that report alone which downloaded file or installed shortcut was opened. This delivery uses a fresh folder/link and an exact-checksum installation check; no assumption about the owner's actions is made.

The Windows check is ordinary CI installation/launch, not a clean customer SmartScreen walkthrough. The installer remains unsigned. No tests or application launches were performed on the owner's Windows desktop for this checkpoint.

The older Mac run 39380929838 compiled the universal app, but its lossless compression helper exceeded 900 seconds. The fallback complete ZIP was 37,853,853 bytes and correctly failed the strict Etsy size gate. It is **not approved customer delivery**. Functional/branding installation checks were skipped in that failed run.

The replacement Mac run 39383934688 uses the final name/logo source and losslessly optimized native icon on a standard Intel Mac runner. Its outcome is pending; no current Mac size or native branding pass is claimed here.

## Next

Inspect the replacement Mac result, preserve the smallest complete verified package, and collect actual Mac branding/functional evidence. If necessary, repair packaging without another application rebuild. Consumer Gatekeeper/authentication screenshots remain a separate uncompleted requirement; CI installation never proves that customer flow.
