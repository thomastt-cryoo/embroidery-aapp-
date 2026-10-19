---
id: "install"
title: "Install Embroidery Studio on Mac or Windows"
summary: "Use the private review package for your computer and keep your existing Lilo installation."
section: "getting-started"
order: 2
keywords: ["install", "download", "mac", "macos", "windows", "smartscreen", "linux", "appimage", "deb", "update", "dmg"]
appContext: ["view.home"]
status: "ready"
---

# Install Embroidery Studio on Mac or Windows

Use the **Embroidery Studio** package supplied for this private review. The package folder includes checksums, licence text and third-party notices. Lilo downloads from the original project install Lilo, not Embroidery Studio.

## Mac

You need macOS 13 or newer. The universal package contains Apple Silicon and Intel binaries. The M2 native launch was tested on Apple Silicon; Intel hardware has not been tested.

1. Open `Embroidery Studio_1.4.0_universal.dmg`.
2. Copy **Embroidery Studio** to **Applications**.
3. Open Embroidery Studio.

This review build uses ad-hoc signing. It has no Apple Developer ID or notarization, so macOS may prevent it from opening. A signed and notarized package is needed for general distribution. No claim of Gatekeeper approval is made.

The first time you look for machines, macOS may request **Local Network** access. This is used for machines on your own network.

## Windows

You need 64-bit Windows. Run `Embroidery Studio_1.4.0_x64-setup.exe`. The installer works for your user only, uses its own folder and Start menu entry, and uses Microsoft’s standard WebView2 bootstrapper if the runtime is missing. That step needs internet access; the installed application processes designs offline.

The review installer is unsigned. Windows may show an unknown-publisher or SmartScreen prompt. A trusted signing certificate has not been supplied.

Your original Lilo installation and default file associations stay in place. Use **Open With** to choose Embroidery Studio for a compatible `.lilo` project or stitch file.

## Linux

M2 provides Windows and macOS review packages. No Linux package was produced or tested in this milestone.

## Updates

Automatic updates are disabled in this review build. It does not check Lilo's release feed. Install only a new Embroidery Studio package supplied for review.

## Next step

Follow [Your first design in five minutes](first-design.md).
