# Mac packaging recovery checkpoint

20 October 2026 (Dubai time)

## Completed

The final Embrova source, including the small rounded sidebar logo and losslessly encoded native icon, compiled into a complete universal Mac app in [build 39383934688](https://github.com/thomastt-cryoo/embroidery-aapp-/actions/runs/39383934688). Source: `1a524f3c0609f8d8e647968ad4ac2cc23ed58fd9`.

The packaging step failed. Its optional compression helper exceeded 900 seconds and discarded the intermediate compressed result. The remaining complete ZIP was **39,446,740 bytes**, with a **39,420,706-byte** installer. The strict Etsy size gate correctly rejected it. Native installation, branding screenshots, folder tests and functional checks were skipped in that failed run. This is not a customer-ready package.

Exact build evidence is saved in `mac-build-39383934688/`, including source environment, timeout, candidate sizes, checksum and size-gate failure.

## Repair and tests

- The compressor now verifies and saves each smaller complete package immediately. A timeout during later optional tuning can reuse a verified checkpoint instead of losing all progress.
- Every accepted checkpoint must preserve every decoded payload byte, match native extraction files/permissions, pass strict signature verification for both architectures, and match its recorded size/checksum.
- Three local packaging-control tests passed: recover a valid checkpoint after timeout; reject an altered checkpoint; retain the complete original when no checkpoint exists. These use fixtures and do not claim native Mac validation.
- Seven existing package/report contract tests passed; Python syntax and workflow YAML checks passed.
- Added a manual-only recovery workflow on a standard GitHub Intel Mac. It downloads the completed build, verifies both architectures and the exact current native icon, repackages without compilation or application edits, and attempts actual installation/native functionality even if the Etsy size gate still fails. The final success gate remains strictly below 20,000,000 bytes.

## Next and limitations

[Recovery run 39387699731](https://github.com/thomastt-cryoo/embroidery-aapp-/actions/runs/39387699731) was started from workflow source `63dcf94acd8765c6da45dcd1f352c09a6d318df8`. Its result and smallest verified ZIP size are pending. The already compiled application is reused; no additional full build was started.

The Windows delivery is separately verified and available. No owner Windows application was opened or changed during these checks. No engine or M1 redesign was performed. Consumer Gatekeeper/security-warning testing remains uncompleted and is not implied by ordinary CI installation.
