# M2 checkpoint 1 — Identity and private build plan

19 October 2026. Approved M1 source: `6334c8b`. Working name: **Embroidery Studio**.

## Completed

- Confirmed the destination `thomastt-cryoo/embroidery-aapp-` is **private**, empty and accessible. No public release will be created.
- Audited installer metadata, app profile, project folder, protocol handler, bridge port, updater and branding boundaries.
- Prepared a temporary monochrome hoop/stitch icon, product/window titles, separate identifier `io.github.thomasttcryoo.embroiderystudio`, binary `embroidery-studio`, Documents/Embroidery Studio and local port **17842**. Lilo keeps port 17841 and its own folders.
- Disabled update endpoints and the native updater-enabled flag. This distribution cannot follow Lilo's update feed.
- Windows uses a per-user NSIS installer with the WebView2 offline installer included. It adds Open With choices without replacing current extension defaults. macOS declares alternate file handlers and retains compatible `.lilo` projects.
- Captured installed Lilo's executable checksum and existing per-user extension defaults before installation in `evidence/baseline.json`.

## Tests

- TypeScript checks passed after branding changes; desktop icons generated successfully with the Tauri icon tool.
- Private repository read/write access and Actions availability confirmed. The billing API does not expose remaining allowance through the available credentials, so no claim is made that a specific balance was verified.
- Windows installer build started. Engine, editing state, project format and M1 layout/style are unchanged.

## Limits and next

Use one standard macOS runner with an 80-minute timeout, within the user's 200-minute ceiling, and private artifacts with short retention. No paid larger runner or billing-setting changes. Build and actual native launch/screenshot checks will be reported separately from browser tests on macOS. No Developer ID/signing certificate has been supplied, so Mac artifacts are review builds with ad-hoc signing, not notarized public installers.

Next: finish the installer, execute package-isolation checks, upload the source privately and run the macOS workflow, then test the installed Windows application.

Sources: [Tauri Windows installer and offline WebView2 options](https://v2.tauri.app/distribute/windows-installer/), [Tauri DMG packaging](https://v2.tauri.app/distribute/dmg/), [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions).
