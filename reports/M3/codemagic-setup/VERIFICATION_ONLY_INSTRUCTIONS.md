# Next run: screenshots and native verification only

> **20 October 2026, build 3 update:** this workflow now reuses the corrected Mac ZIP from commit `bb6271b`, with the Stitches UI fix included. Build and ordinary CI installation already passed. Only native GUI testing/screenshots remain blocked by macOS permissions. Do not run another full build for that blocker.

Use workflow **Mac screenshots only - NO REBUILD**, branch **main**. The full-build workflow remains available but is not needed for this task.

The supplied ZIP was checked locally: **19,871,801 bytes**, SHA-256 `9d5bd61cb8531d67cf5b3990b659d3713accd792e08065371340717235f3e481`. It is retained on the dedicated **private** branch `codex/m3-macos-verification-package`, outside main and customer packages. The verification run fetches this exact file through the repository's existing authenticated Git access. There is no public upload, API-token setup, rebuild, engine/UI change, or customer reconstruction step.

## What you do

1. In Codemagic, select **main**, refresh its configuration, and choose **Mac screenshots only - NO REBUILD**.
2. Select **Mac mini M2** and **Enable SSH/VNC access** when starting the one manual run. Do not enable billing or choose another machine.
3. Open **Explore build machine via SSH or VNC client** and connect to that Mac with the displayed VNC details. They are temporary credentials; keep them private.
4. On the **Mac desktop**, double-click **START MAC SCREENSHOT TEST.command**. It appears after the ZIP and small test dependency are ready. This opens Terminal and requests standard macOS permissions for the test host.
5. In the Mac's **System Settings → Privacy & Security**, approve **Accessibility** and **Screen Recording** for the requesting test host, normally **Terminal**. Use the actual name shown by macOS. Only you approve these settings. If asked to quit/reopen Terminal, do that and double-click the same desktop launcher again.
6. The test continues automatically when permission checks pass. Stay connected: if the installer shows an authentication/security screen, automation pauses for you to inspect and handle it. Do not disable Gatekeeper or any system protection.
7. Download **Mac-QA-evidence.zip** after the run and attach it here. It contains the numbered original PNGs, draft illustrated guide and native test results.

Connect and approve within **five minutes after the READY message**; otherwise the run stops to conserve minutes. The entire run has a **20-minute maximum**. No automatic retry or new build is scheduled. Mac time is consumed while waiting, so have your VNC client ready before starting. Do not start this workflow until you can connect to the remote Mac.

## What is and is not verified

- The existing universal package is reused; no Rust, Node frontend compilation, fonts or browser regression is repeated.
- The original run's 96 Rust tests and browser results remain historical evidence and are labelled accordingly.
- Finder/Archive Utility/Installer screens and installed-app native tests run on the real Mac once approved.
- For efficiency, the sealed ZIP is transferred through private Git and copied into Downloads. This is **not a Safari/Etsy download or a clean consumer Gatekeeper test**. Quarantine is neither created nor removed.
- Installer authentication/security screens are never automatically approved. Native screenshot capture may still stop at an unfamiliar or inaccessible OS dialog; partial results remain available rather than being reported as a pass.
- Running the test from an owner-opened Terminal is intended to let macOS attribute permission requests to an interactive host. This behavior has not yet been verified on Codemagic; actual permission probe results determine whether the test can proceed.
- No screenshots are fabricated. Original QA screenshots require privacy review before customer use.

Local checks: official Codemagic schema validation, shell/Python syntax and six package/report contract tests. A new native Mac test run has **not** been executed during this preparation.
