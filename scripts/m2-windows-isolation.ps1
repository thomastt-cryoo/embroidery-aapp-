param([string]$InstallDir = (Join-Path $env:LOCALAPPDATA 'Embroidery Studio'))
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$baseline = Get-Content -LiteralPath (Join-Path $repoRoot 'reports/M2/evidence/baseline.json') -Raw | ConvertFrom-Json
$appDir = $InstallDir
$exe = Join-Path $appDir 'embroidery-studio.exe'
if (-not (Test-Path -LiteralPath $exe)) { throw 'Embroidery Studio is not installed at its own location.' }
$originalHash = (Get-FileHash -LiteralPath $baseline.originalInstalledExe -Algorithm SHA256).Hash
if ($originalHash -ne $baseline.originalSha256) { throw 'Installed Lilo executable changed.' }
$defaults = @{}
foreach ($property in $baseline.extensionDefaults.PSObject.Properties) {
    $key = 'HKCU:\Software\Classes\.' + $property.Name
    $value = if (Test-Path -LiteralPath $key) { (Get-Item -LiteralPath $key).GetValue('') } else { $null }
    if ($value -ne $property.Value) { throw ('Extension default changed: .' + $property.Name) }
    $defaults[$property.Name] = $value
}
$uninstallKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Embroidery Studio'
$entry = Get-ItemProperty -LiteralPath $uninstallKey
if ($entry.DisplayName -ne 'Embroidery Studio') { throw 'Wrong uninstall identity.' }
$openWith = (Get-ItemProperty -LiteralPath 'HKCU:\Software\Classes\.lilo\OpenWithProgids').'EmbroideryStudio.Project'
if ($null -eq $openWith) { throw 'The compatible project Open With entry is missing.' }
$projectCommand = (Get-Item -LiteralPath 'HKCU:\Software\Classes\EmbroideryStudio.Project\shell\open\command').GetValue('')
if ($projectCommand -ne ('"' + $exe + '" "%1"')) { throw 'Open With points to the wrong executable.' }
$files = @(Get-ChildItem -LiteralPath $appDir -Recurse -File | ForEach-Object { $_.FullName.Substring($appDir.Length + 1) })
if ($files | Where-Object { $_ -match 'node_modules|\.git\\|reports\\|test\\|\.map$' }) { throw 'Development files present in customer install.' }
$shell = New-Object -ComObject WScript.Shell
$startMenu = Join-Path $env:APPDATA 'Microsoft/Windows/Start Menu/Programs/Embroidery Studio/Embroidery Studio.lnk'
if (-not (Test-Path -LiteralPath $startMenu)) { throw 'Separate Start Menu shortcut is missing.' }
$shortcutTarget = $shell.CreateShortcut($startMenu).TargetPath
if ($shortcutTarget -ne $exe) { throw 'Shortcut target is not the new app.' }
$result = [ordered]@{
    result = 'pass'
    installedExe = $exe
    installedSha256 = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash
    originalLiloUnchanged = $true
    originalLiloSha256 = $originalHash
    extensionDefaultsPreserved = $defaults
    openWithCommand = $projectCommand
    uninstallDisplayName = $entry.DisplayName
    uninstallVersion = $entry.DisplayVersion
    startMenuShortcutTarget = $shortcutTarget
    customerFiles = $files
    signatureStatus = (Get-AuthenticodeSignature -LiteralPath $exe).Status.ToString()
}
$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $repoRoot 'reports/M2/evidence/windows-isolation.json')
'PASS: separate install, shortcut and uninstall identity; Lilo bytes and extension defaults unchanged; no development files in customer install.'
