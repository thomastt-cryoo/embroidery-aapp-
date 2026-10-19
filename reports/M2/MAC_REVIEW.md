# Embroidery Studio — macOS M2 review

This is a private review build. Mount the DMG and copy Embroidery Studio.app to Applications. It uses its own app profile, project folder, URL scheme and bridge port and can coexist with Lilo.

The app is ad-hoc signed. It has not been signed with an Apple Developer ID or notarized. Gatekeeper acceptance for general distribution is a remaining requirement; this package does not claim to be a notarized public release.

The evidence folder distinguishes a universal build, DMG verification, actual native macOS launch/screenshot and Rust tests from the separate Chromium conversion/editing/export checks on the same runner. Physical embroidery-machine testing is not included.

Updates are disabled in this review build. No Lilo update feed is configured. Projects remain compatible .lilo files; exports and the embroidery engine are unchanged.
