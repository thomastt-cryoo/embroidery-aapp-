# M2 build and verification handoff

M1 was approved at `6334c8b`. M2 uses branch `codex/m2-branding-packaging`. The original remote is retained as `origin` for fetching references only; its push URL is disabled. `remote.pushDefault` is set to `distribution`. Only the user-approved private `distribution` repository is used for M2 pushes and builds. GitHub confirms that the authenticated account has no push or admin access to `Kadwood/lilo`.

## Build

Use the pinned pnpm version from package.json, Node.js, Rust and the Tauri platform build prerequisites. From the repository root:

```powershell
pnpm install --frozen-lockfile
pnpm fonts
pnpm tauri build --bundles nsis
```

The Windows installer is generated under `app/src-tauri/target/release/bundle/nsis`. The embedded WebView2 offline installer accounts for most of the download size. Fonts and required runtime assets remain embedded; source trees, test evidence and development dependencies are excluded from the installed application.

The manual `.github/workflows/release.yml` builds the macOS universal application and DMG on `macos-14`, with an 80-minute timeout. It installs from the DMG, runs native checks and separately runs production browser acceptance. It uploads a private artifact with two-day retention. There is no public release job. The website publishing workflow is disabled.

No signing credentials are stored in the repository. Windows is unsigned; macOS uses ad-hoc signing. Developer ID, notarization, Windows signing and the final product name remain future distribution decisions.

## Verification

```powershell
node scripts/m2-package-check.mjs
pnpm check-versions
pnpm guide:check
pnpm typecheck
pnpm test:scripts
pnpm --filter editor test --maxWorkers=2
cargo test --release --manifest-path app/src-tauri/Cargo.toml --lib --test api
```

The package guard compares the embroidery engine and M1 interface stylesheet byte-for-byte against approved M1. Editing state, project management and platform source permit only the literal branding-word substitutions; their behavior must remain identical. A portable native test fixture now generates OS-correct file URLs on both platforms.

For production acceptance, serve `editor/dist` locally and run `scripts/m2-ui-check.mjs` with `LILO_PRODUCTION=1`, `LILO_URL` set to the local server and optionally `LILO_CHROMIUM` pointing to Chromium or Chrome. External HTTP(S) is blocked throughout. The legacy environment-variable names are build/test compatibility identifiers, not update channels or application identities.

For Windows installation isolation, run `scripts/m2-windows-isolation.ps1 -InstallDir <actual-installed-folder>`. It compares the original Lilo executable and extension defaults to the pre-install baseline, verifies both URL handlers, checks the separate shortcut/uninstaller/Open With command, and inventories customer files. The installed executable is compared against the final build after applying Tauri's documented-in-build-log three-byte bundle marker (`UNK` to `NSS`); every other byte must match.

The native Windows review checks used actual Windows Open/Save dialogs and the installed Tauri WebView. Browser acceptance uses real file inputs, downloads and the real embroidery engine. macOS native launch/rendering and Rust tests are distinguished from its detailed Chromium workflow checks; there is no claim that native macOS editing dialogs or Intel execution were fully automated.

## Compatibility boundaries

Compatible `.lilo` project files, stitch/export format IDs and existing internal engine/package names remain stable. New data lives in the application's own profile and `Documents/Embroidery Studio`. Native discovery uses port 17842, and deep links use `embroidery-studio://`. Windows adds Open With entries without replacing extension defaults. Updater endpoints are empty and both UI/backend availability checks disable automatic updates before any network request.

Raw build/test logs stay locally under `reports/M2/evidence`; compact JSON records, sample outputs and real screenshots are retained with the reports. Package hashes and exact byte sizes are recorded in the final manifest.
