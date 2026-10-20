param([string]$InstallDir = (Join-Path $env:LOCALAPPDATA 'Embrova'))
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$baseline = Get-Content -LiteralPath (Join-Path $repoRoot 'reports/M2/evidence/baseline.json') -Raw | ConvertFrom-Json
$appDir = $InstallDir
$exe = Join-Path $appDir 'embrova.exe'
if (-not (Test-Path -LiteralPath $exe)) { throw 'Embrova is not installed at its own location.' }
$installedHash = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash
$buildPath = Join-Path $repoRoot 'app/src-tauri/target/release/embrova.exe'
$builtHash = (Get-FileHash -LiteralPath $buildPath -Algorithm SHA256).Hash
# Tauri temporarily patches UNK -> NSS while bundling, then restores the raw
# build. Compare every byte after applying only that known three-byte marker.
$expectedBytes = [IO.File]::ReadAllBytes($buildPath)
$binaryText = [Text.Encoding]::ASCII.GetString($expectedBytes)
$marker = 'BUNDLE_TYPE_VAR_UNK'
$markerOffset = $binaryText.IndexOf($marker)
if ($markerOffset -lt 0 -or $markerOffset -ne $binaryText.LastIndexOf($marker)) { throw 'Expected one Tauri bundle marker.' }
[Array]::Copy([Text.Encoding]::ASCII.GetBytes('NSS'), 0, $expectedBytes, ($markerOffset + $marker.Length - 3), 3)
$expectedStream = [IO.MemoryStream]::new($expectedBytes)
try { $expectedHash = (Get-FileHash -InputStream $expectedStream -Algorithm SHA256).Hash } finally { $expectedStream.Dispose() }
if ($installedHash -ne $expectedHash) { throw 'Installed executable does not match the final NSIS build.' }
$originalHash = (Get-FileHash -LiteralPath $baseline.originalInstalledExe -Algorithm SHA256).Hash
if ($originalHash -ne $baseline.originalSha256) { throw 'Installed Lilo executable changed.' }
$defaults = @{}
foreach ($property in $baseline.extensionDefaults.PSObject.Properties) {
    $key = 'HKCU:\Software\Classes\.' + $property.Name
    $value = if (Test-Path -LiteralPath $key) { (Get-Item -LiteralPath $key).GetValue('') } else { $null }
    if ($value -ne $property.Value) { throw ('Extension default changed: .' + $property.Name) }
    $defaults[$property.Name] = $value
}
$uninstallKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Embrova'
$entry = Get-ItemProperty -LiteralPath $uninstallKey
if ($entry.DisplayName -ne 'Embrova') { throw 'Wrong uninstall identity.' }
$openWith = (Get-ItemProperty -LiteralPath 'HKCU:\Software\Classes\.lilo\OpenWithProgids').'Embrova.Project'
if ($null -eq $openWith) { throw 'The compatible project Open With entry is missing.' }
$projectCommand = (Get-Item -LiteralPath 'HKCU:\Software\Classes\Embrova.Project\shell\open\command').GetValue('')
if ($projectCommand -ne ('"' + $exe + '" "%1"')) { throw 'Open With points to the wrong executable.' }
$protocolCommand = (Get-Item -LiteralPath 'HKCU:\Software\Classes\embrova\shell\open\command').GetValue('')
if ($protocolCommand -ne ('"' + $exe + '" "%1"')) { throw 'The application URL handler points to the wrong executable.' }
$liloProtocol = (Get-Item -LiteralPath 'HKCU:\Software\Classes\lilo\shell\open\command').GetValue('')
if ($liloProtocol -ne ('"' + $baseline.originalInstalledExe + '" "%1"')) { throw 'The original Lilo URL handler was replaced.' }
$files = @(Get-ChildItem -LiteralPath $appDir -Recurse -File | ForEach-Object { $_.FullName.Substring($appDir.Length + 1) })
if ($files | Where-Object { $_ -match 'node_modules|\.git\\|reports\\|test\\|\.map$' }) { throw 'Development files present in customer install.' }
$shell = New-Object -ComObject WScript.Shell
$startMenu = Join-Path $env:APPDATA 'Microsoft/Windows/Start Menu/Programs/Embrova/Embrova.lnk'
if (-not (Test-Path -LiteralPath $startMenu)) { throw 'Separate Start Menu shortcut is missing.' }
$shortcutTarget = $shell.CreateShortcut($startMenu).TargetPath
if ($shortcutTarget -ne $exe) { throw 'Shortcut target is not the new app.' }
$result = [ordered]@{
    result = 'pass'
    installedExe = $exe
    installedSha256 = $installedHash
    matchesFinalBuild = $true
    unbundledBuildSha256 = $builtHash
    bundleMarker = 'Tauri NSIS packaging: UNK -> NSS; all other bytes identical'
    originalLiloUnchanged = $true
    originalLiloSha256 = $originalHash
    extensionDefaultsPreserved = $defaults
    openWithCommand = $projectCommand
    protocolCommand = $protocolCommand
    originalLiloProtocolCommand = $liloProtocol
    uninstallDisplayName = $entry.DisplayName
    uninstallVersion = $entry.DisplayVersion
    startMenuShortcutTarget = $shortcutTarget
    customerFiles = $files
    signatureStatus = (Get-AuthenticodeSignature -LiteralPath $exe).Status.ToString()
}
$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $repoRoot 'reports/M2/evidence/windows-isolation.json')
'PASS: separate install, shortcut and uninstall identity; Lilo bytes and extension defaults unchanged; no development files in customer install.'
