# M3 — Codemagic macOS setup

20 October 2026

The repository now contains a manual Codemagic workflow for building and testing the existing Embroidery Studio Mac application. **Configuration validation passed locally. No Codemagic Mac build has run during this setup; no new Mac package size or installation success is claimed.**

## What is configured

- Workflow: **Embroidery Studio — Mac build, native tests and M3 screenshots** (`macos-m2-build-test`).
- Machine: **`mac_mini_m2`**, Xcode 16.4/macOS 15.5 image, Node 24; **80-minute maximum**. There are no push, pull-request, tag or schedule triggers. A script also rejects webhook/schedule execution.
- No paid machine, billing setting, app-store publishing, public release, distribution service or email publishing was enabled. Free-minute availability must still be checked in your account before starting.
- The existing Tauri 2 app, universal Intel/Apple silicon build, ad-hoc signing and M2 lossless installer compression are reused. The engine, runtime resources and approved application UI were not edited for this setup.
- Cargo/font caches reduce repeat setup costs. The workflow builds one selected delivery format rather than repeating the old packaging comparison.
- The customer receives **one complete Mac ZIP containing one PKG installer**. An exact size gate rejects a ZIP at or above **20,000,000 bytes**; an oversized complete package remains available for inspection. Nothing is split or removed to force a pass.
- M3 now takes the ZIP produced in the same run, verifies its SHA-256, and uses real Safari/Finder/Archive Utility/Installer screens where permissions permit. It no longer needs an old GitHub Actions artifact or GitHub artifact-download token.
- Read-only desktop-permission checks run before capture. Missing Accessibility or screen-capture access is reported as blocked; the workflow does not grant permissions, change TCC, remove quarantine or disable Gatekeeper.
- Ordinary CI installation from the actual ZIP is separately logged. Installed application files, permissions, identity and both binary architectures must match the built app.
- Existing native Mac tests cover actual image import/conversion, rendered stitches, simulation, hoop selection, stitch editing, save, reopen and PES export. A separate production Chromium regression tests all 13 formats, project round-trip and offline operation. Browser success cannot substitute for native success.

## Downloadable artifacts after a run

| Artifact | Purpose |
|---|---|
| `Embroidery-Studio-macOS.zip` | The single customer download, subject to the exact size gate |
| `Install Embroidery Studio.pkg` | Standalone installer for owner inspection/testing |
| `M3_MACOS_RUN_REPORT.md` | Actual package sizes, architecture scope, test results and limitations |
| `MACOS_ILLUSTRATED_GUIDE_DRAFT.md` | Illustrated draft using only screenshots captured in that run |
| `Mac-QA-evidence.zip` | Owner-only logs, test results, reports, numbered screenshots and screenshot indexes |
| `02-macOS/installation/originals/` | Numbered real installer/customer-flow PNGs, when available |
| `02-macOS/functional/originals/` | Numbered real application/test PNGs, when available |

The QA ZIP is for you, not an additional customer ZIP part. Original screenshots remain separate PNGs inside it. Screenshot candidates require privacy review before use in customer instructions or an Etsy listing; diagnostic path-entry and failure screens are excluded from the draft guide.

## What was verified here

- YAML validated against the **official Codemagic JSON schema** downloaded from `https://codemagic.io/codemagic-schema.json`.
- Five local tests passed: package readback; changed-ZIP rejection; rejection at the exact 20,000,000-byte boundary; incomplete-run reporting; and prevention of a browser pass disguising blocked native testing. These are configuration/report tests, not Mac application tests.
- Bash syntax and Python compilation passed.
- Existing identity/source-preservation checks passed. No engine, frontend, Tauri configuration or packaging algorithm changed in this setup.
- Existing GitHub credential access verified that the destination repository is private. Push destination is **`thomastt-cryoo/embroidery-aapp-`**, branch **`main`**. The original `Kadwood/lilo` repository remains reference-only.
- Local validation evidence is in `reports/M3/codemagic-setup/`. The existing M2 customer ZIPs were not replaced.

## Your next action

1. Open your connected project in **Codemagic**.
2. Select branch **main** and use **Check for configuration file** if Codemagic has not refreshed it.
3. Choose **Embroidery Studio — Mac build, native tests and M3 screenshots**.
4. Confirm the selected machine is **Mac mini M2**, that free minutes remain, and that billing is not being requested. Start **one** manual build. Do not choose a paid machine or turn on billing.
5. When it finishes, download **M3_MACOS_RUN_REPORT.md** and **Mac-QA-evidence.zip** from its build page. A failed run can still contain the complete installer and useful partial evidence.

I could verify GitHub access and the configuration, but an authenticated Codemagic account session/API connection was not available to this task. The connected-browser tool failed to initialize before opening a page. I have therefore stopped before starting a build or changing account settings. No password or API token needs to be pasted into this chat. If Codemagic asks for account authorization, complete that yourself and stop if it requests payment.

If desktop permissions block the first run, review its report before spending more minutes. Codemagic offers optional SSH/VNC access when starting a build, which must be enabled manually in its UI; it was not enabled here. Any authentication or permission approval must be performed by the account owner. No repeated builds are scheduled.

## What CI cannot prove

This M2 runner executes the ARM version. It builds and verifies the Intel slice but **does not execute it on an Intel Mac**.

A localhost Safari download on a CI machine and `sudo installer` are different from installation on a clean consumer Mac downloaded from Etsy. **Clean consumer Gatekeeper testing remains outstanding.** The application remains ad-hoc signed, without Developer ID/notarization. Actual security or authentication screens stop the GUI walkthrough; warning screenshots are never invented. If a warning is not observed in an incomplete run, the result is unknown rather than proof that customers will see none.

## Official references

- [YAML structure, manual triggering, artifacts and schema validation](https://docs.codemagic.io/yaml-basic-configuration/yaml-getting-started/)
- [Mac machine types](https://docs.codemagic.io/knowledge-codemagic/machine-type/)
- [Pinned Xcode 16.4 machine image](https://docs.codemagic.io/specs-macos/xcode-16-4/)
- [Optional, manually enabled SSH/VNC access](https://docs.codemagic.io/troubleshooting/accessing-builder-machine-via-ssh/)

Setup is ready for the first manual account-authorized run. M3 installation screenshots and clean consumer testing are not marked complete.

## First-run correction

The first Codemagic run (`6ad6d39a7550aed810905add`, source `48349f4`) reached macOS 15.5/Xcode 16.4 and installed Pillow successfully, then stopped during pnpm setup: `EEXIST: file already exists, /usr/local/bin/pnpm`. No application compilation or installation tests ran.

The setup script now installs the pinned pnpm 10.0.0 inside the disposable workspace and places its local executable first on PATH. It does not replace Codemagic's existing pnpm/Corepack shim. The corrected installation was exercised locally, including a second installation into the same directory, and pnpm reported 10.0.0. Shell syntax and the existing package/report tests also passed. This local check is not a new Mac build result. One new manual build of the latest main commit is needed; do not retry the old commit.

## Second run — build and CI installation passed; native GUI permissions blocked

Run `6ad6d5e57550aed810905b59`, source `74c0fd0`, successfully built the complete universal application and installed its actual customer package on macOS. The owner supplied its QA artifact for inspection. Detailed evidence is preserved in `reports/M3/codemagic-setup/run-2/`.

| Check | Verified result |
|---|---|
| Complete customer ZIP | **19,861,169 bytes**; under 20,000,000 bytes by 138,831 bytes |
| Installer | **19,845,240 bytes** |
| Customer ZIP SHA-256 | `cf594cb3c34373aee45a150aca7cb2f9326fff9c19fa41fe5a4f4bdd2012b426` |
| Architectures built/installed | `x86_64 arm64` |
| CI installation | Passed; installed files and modes match the built app |
| Ad-hoc signature verification | Passed; still not Developer ID/notarized |
| Native Rust code tests | **96 passed**, zero failures |
| Production browser regression on Mac | **9 checks passed**, all 13 exports written; 11 machine formats reread; conversion, hoop selection, simulation, project save/reopen and offline processing passed |
| Native GUI tests and installation screenshots | **Blocked**, not failed application assertions |
| macOS Accessibility access | `false` |
| macOS screen-capture authorization | `false` |
| New native installation screenshots | **0** |

The overall red build status is intentional: blocked native UI coverage cannot become a passing result merely because compilation, ordinary CI installation and browser tests succeeded. Browser screenshots in this artifact are not substituted for native screenshots. No GUI security warning was tested, and no clean consumer Gatekeeper pass is claimed.

**Do not spend another full build on this blocker.** Preserve/download the already-produced customer ZIP. Completing native UI testing requires a remote or physical Mac session with Accessibility and Screen Recording permission approved by the account owner for the actual test host/process. The workflow never requests/grants those permissions or changes OS security itself. Any subsequent verification should reuse this exact ZIP/hash rather than rebuild it. Work stops here for that user-only permission/access step; no further runner or billing action has been taken.
