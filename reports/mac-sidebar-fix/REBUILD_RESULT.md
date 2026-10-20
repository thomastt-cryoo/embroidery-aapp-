# Updated Mac UI package — build evidence reviewed

20 October 2026

The owner-supplied Mac-QA-evidence (3).zip passed ZIP integrity checks. Its logs show the corrected sidebar and previous Stitches fixes built from private main commit 471e1fc1a3544dda51048afcecc177844b7602f6 on macOS 15.5, Xcode 16.4.

- Complete customer ZIP: **19,866,936 bytes**, 133,064 bytes below Etsy's strict limit.
- Installer: **19,851,396 bytes**.
- ZIP SHA-256: `3381ddb207a0e535b780752c58957c3f95d68465921022ab90d306ea54d5e33d`.
- Universal Intel/Apple silicon binary identity and strict ad-hoc signature checks passed.
- Native package extraction matched the original payload after lossless compression.
- Engine/interface preservation, separate identity, offline runtime and disabled updates checks passed.
- No functional/export tests, installation walkthrough or screenshots were repeated, as requested.

These are reviewed build logs, not independent inspection of the customer ZIP: the customer ZIP was not included in the supplied QA archive. No native visual confirmation of the newly corrected sidebar is claimed. Consumer Gatekeeper testing remains incomplete and signing remains ad-hoc, without notarization.

Next: download Embroidery-Studio-macOS.zip from this successful rebuild's artifacts. That is the updated application; the supplied QA ZIP contains only build evidence.
