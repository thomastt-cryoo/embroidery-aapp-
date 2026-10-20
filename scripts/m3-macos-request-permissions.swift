// Owner-initiated desktop helper. Requests normal OS dialogs; never grants access.
// This file is never included in the customer application or installer.
import AppKit
import ApplicationServices
import Foundation
if !AXIsProcessTrusted() {
    let options = [kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: true] as CFDictionary
    _ = AXIsProcessTrustedWithOptions(options)
}
if !CGPreflightScreenCaptureAccess() {
    _ = CGRequestScreenCaptureAccess()
}
print("Permission requests shown if needed. Only the owner can approve them in macOS Settings.")
