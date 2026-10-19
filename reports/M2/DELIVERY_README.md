# Embroidery Studio — M2 private review

Embroidery Studio is the temporary name for the redesigned application. These packages are for private review. No public release has been published.

## Windows

Run **Embroidery Studio_1.4.0_x64-setup.exe** on 64-bit Windows. It installs for your user and includes the offline Microsoft WebView2 installer. The package is larger because that runtime is included.

Embroidery Studio has its own Start menu shortcut and uninstall entry. Your existing Lilo installation stays in place. Existing default file associations are preserved; **Open With → Embroidery Studio** is available for compatible projects and stitch files.

On the development computer, the tested application is already installed at `C:\Users\mazin\Applications\Embroidery Studio\embroidery-studio.exe`. The Start menu shortcut opens it.

The Windows installer is unsigned. A trusted signing certificate is still needed for general distribution without unknown-publisher warnings.

## macOS

Open **Embroidery Studio_1.4.0_universal.dmg** and copy **Embroidery Studio.app** to **Applications**. The app ZIP is an alternative download of the same universal application. Extract it on macOS to preserve the app bundle.

The universal binary contains Apple Silicon and Intel code. Actual native launch was verified on an Apple Silicon macOS runner. Intel hardware was not available for execution testing.

The app is ad-hoc signed. It has no Apple Developer ID or notarization, so Gatekeeper may prevent normal opening. Apple signing and notarization remain requirements for general distribution.

## Projects, exports and updates

New projects use **Documents/Embroidery Studio**. Existing `.lilo` projects can be opened from their existing location. The format and embroidery engine are preserved. The included **Studio-sample.lilo** is public test artwork for trying the editor.

The application processes designs locally. Automatic updates are disabled for this review, and no Lilo update feed is configured. Use only Embroidery Studio packages supplied for review.

## Files and evidence

**SHA256SUMS.txt** lists the checksums of the three desktop packages. **LICENSE.txt** and **NOTICE.txt** preserve the licence and third-party credits. Source and full test evidence are in the private `thomastt-cryoo/embroidery-aapp-` repository and the accompanying `M2_FINAL_REPORT.md` in the development folder.

macOS build success, native launch checks and the separate browser workflow tests are reported separately. Physical embroidery-machine sewing and Wi-Fi transfer were not tested in M2.
