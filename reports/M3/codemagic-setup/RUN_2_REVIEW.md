# Codemagic run 2 review

The application built and its package installed successfully. Overall M3 remains incomplete because the Mac runner denied Accessibility and Screen Recording permission, so neither native UI testing nor customer installation screenshots could run.

- Build: `6ad6d5e57550aed810905b59`, commit `74c0fd0`.
- Complete universal ZIP: **19,861,169 bytes**, below the Etsy limit by **138,831 bytes**.
- Installer: **19,845,240 bytes**.
- ZIP SHA-256: `cf594cb3c34373aee45a150aca7cb2f9326fff9c19fa41fe5a4f4bdd2012b426`.
- Ordinary CI installation: pass; all files and modes match the built universal application.
- Native Rust tests: **96 passed**, zero failures.
- Separate production browser checks: **9 passed**; all 13 exports checked, including 11 machine-file rereads; project save/reopen, hoop selection, simulation and offline processing passed.
- Native GUI execution/screenshots: **blocked**; Accessibility false and screen capture false. **Zero** new native screenshots.
- Customer Gatekeeper approval: **not tested**.

The preserved artifact contents are in `run-2/`, including original logs, manifests, test results and clearly identified browser screenshots. `run-2/provenance.json` records the supplied QA archive hash. The customer ZIP itself was not included in the supplied QA archive; its size/hash and installation are evidenced by the runner's size gate and installation manifest.

The remaining step requires owner approval of desktop permissions for the actual test host on a Mac. No repeated build, security permission change, application change or billing action was performed. Preserve the already-built customer ZIP and reuse it for verification once suitable Mac access is available.
