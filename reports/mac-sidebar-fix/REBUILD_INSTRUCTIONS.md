# Rebuild the corrected Mac application

20 October 2026

The sidebar correction is committed in source commit `16554ec`, alongside the earlier Mac Stitches correction. Rebuild the latest `main` in the private `thomastt-cryoo/embroidery-aapp-` project.

## Codemagic selections

1. Click **Start new build**.
2. Select **Build branch**, then branch **main**.
3. Refresh the workflow list if needed and choose **Mac rebuild only - updated UI** (`macos-ui-rebuild`).
4. Leave **Enable SSH/VNC access** unchecked. No remote desktop or permission approvals are needed for this packaging run.
5. Click **Start new build** once.

The configured machine is `mac_mini_m2`. No automatic trigger, billing configuration or public publishing was added. The 40-minute setting is a maximum, not an expected duration. Actual running time consumes Codemagic minutes.

## What this run does

Reuses the existing build script, Tauri configuration, resource preservation checks and lossless package compression. Builds a complete universal Intel/Apple silicon application from current source, verifies its identity/signature, and validates the customer ZIP's contents, checksum and strict size limit below 20,000,000 bytes. Required runtime assets remain bundled.

It stops after packaging. It does not repeat Rust/browser/GUI functional tests, export tests, installation walkthroughs or VNC waits. It does not replace earlier native test gaps with a pass. Full build/testing and screenshots-only workflows remain available separately.

## Download after completion

- **Embroidery-Studio-macOS.zip**: the updated customer application package.
- **MACOS_REBUILD_REPORT.md**: exact package size, checksum and scope of this run.
- **Mac-QA-evidence.zip**: private build logs/evidence if troubleshooting is needed.

The standalone PKG and SHA256SUMS.txt are also artifacts. A green rebuild means compilation/package validation passed, not complete consumer installation approval. Native layout confirmation and clean consumer Gatekeeper verification remain outstanding; ad-hoc signing is unchanged.

## Local preparation checks

- Official Codemagic schema validation passed.
- Seven local package/report contract tests passed, including that a successful rebuild report cannot imply native functional tests passed.
- Bash syntax passed.
- Protected M1/engine, offline runtime and isolated identity checks passed.

No cloud run was started while preparing this configuration. The original `Kadwood/lilo` repository and installed Windows applications were not changed.
