// Read-only permission probe. Never request access or change macOS security/TCC.
import AppKit
import ApplicationServices
import Foundation
let display = CGMainDisplayID()
let result: [String: Any] = [
    "accessibilityTrusted": AXIsProcessTrusted(),
    "screenCaptureAuthorized": CGPreflightScreenCaptureAccess(),
    "displayWidth": CGDisplayPixelsWide(display),
    "displayHeight": CGDisplayPixelsHigh(display),
    "securityPermissionsChanged": false
]
let data = try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys])
print(String(data: data, encoding: .utf8)!)
