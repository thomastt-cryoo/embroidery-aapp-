# M2 Etsy package reproduction

Application packaging source: `544c3837c0a9d8343626639aac10ea0d5a87b715`. The Windows NSIS dictionary setting was recorded in `5241aca`. Subsequent commits add private verification tooling and reports, not application processing changes. `git diff 91e9d9b -- engine editor/src app/src-tauri/src` is empty.

## Build prerequisites

Use the repository's pinned pnpm dependencies and fonts (`pnpm install --frozen-lockfile`, `pnpm fonts`). Python with Pillow **12.3.0** is a build-only dependency. The PNG optimizer downloads the pinned OxiPNG tool and verifies its SHA-256. No build tool is included in customer packages.

## Windows

1. `pnpm tauri build --bundles nsis` builds the raw embedded-asset version with the Cargo release profile and standard WebView2 bootstrapper.
2. Preserve the complete build log in `reports/M2/etsy/windows-build.txt`.
3. `python scripts/m2-windows-etsy.py` creates the single customer ZIP, verifies/extracts it and records its exact path/hash. ZIP timestamps mean a later reproduction may have a different archive hash even with the same installer.
4. Install the **extracted** installer from the path in `windows-package.json`. Preserve the original Lilo location and existing defaults.
5. `scripts/m2-windows-isolation.ps1 -InstallDir <own-install-dir>` checks executable equality, the known Tauri bundle marker, shortcuts, uninstall identity and original Lilo preservation.
6. Native UI tests must leave Tauri IPC untouched. Do not intercept `http://ipc.localhost` or enable broad CDP request routing. A full WebView reload is needed after an intercepted native transport fails.

All Windows functional checks were repeated after removing interception, then the app was closed and relaunched normally without remote debugging. The local preview server was stopped. The installed final review app is `C:\Users\mazin\Applications\Embroidery Studio\embroidery-studio.exe`.

## macOS

The private `release.yml` workflow compares complete universal builds with raw assets and `--features asset-compression`. `m2-macos-etsy.py` compares standard app/disk-image/PKG packaging. Both architectures and all runtime files stay present.

The selected PKG uses `pkgbuild --min-os-version 13.0 --compression latest`. The private `mac-zip-verification.yml` downloads the finished ZIP, installs its actual contents and checks the native app. Swift/Python native Accessibility and Vision helpers execute only outside the app bundle on the runner. They do not rebuild the application, add app test hooks, change privacy settings or request new permissions.

Keep final artifacts local before the private GitHub artifact's two-day retention expires. Downloaded GitHub archives have their published SHA-256 checked before extraction; the final customer ZIP has its own separately recorded hash.

## Final delivery validation

`python scripts/m2-verify-delivery.py` verifies exactly two ZIPs in `dist/M2-Etsy`, expected installers/instructions/legal text, CRC checks, headers, native Windows result counts and the previously verified Mac ZIP hash. It writes `delivery-manifest.json` and Windows build evidence. It deliberately reports the Mac size failure rather than rejecting or silently truncating that complete package.

`node scripts/m2-package-check.mjs` checks isolated branding/updates and protected sources. Reports and test assets belong outside the two customer archives. No M3 work is authorized.
