param(
    [string]$Version = "2.0.0",
    [string]$Manufacturer = "Dameon J Wendtland"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$distDir = Join-Path $repoRoot "dist"
$bundleDir = Join-Path $distDir "LanguageRandomizer"
$wixSource = Join-Path $repoRoot "installer\windows\LanguageRandomizer.wxs"
$licensePath = Join-Path $repoRoot "installer\windows\installer-notice.rtf"
$iconPath = Join-Path $repoRoot "language_randomizer\assets\translating.ico"
$wixBuildRoot = Join-Path $repoRoot "build\wix"
$msiPath = Join-Path $distDir ("LanguageRandomizer-" + $Version + "-x64.msi")
$wixPath = "C:\Program Files\WiX Toolset v6.0\bin\wix.exe"
$productUrl = "https://github.com/DameonJWendtland/language-randomizer"
$extensionRef = "WixToolset.UI.wixext/6.0.2"

Push-Location $repoRoot
try {
    if (-not (Test-Path $wixPath)) {
        throw "WiX CLI not found. Install WiX Toolset Command-Line Tools first."
    }

    & (Join-Path $repoRoot "scripts\build_windows_exe.ps1")
    if ($LASTEXITCODE -ne 0) {
        throw "EXE bundle build failed with exit code $LASTEXITCODE."
    }

    $extensionList = & $wixPath extension list -g 2>$null
    if ($extensionList -notmatch "WixToolset\.UI\.wixext") {
        & $wixPath extension add -g $extensionRef
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install WiX UI extension."
        }
    }

    New-Item -ItemType Directory -Path $wixBuildRoot -Force | Out-Null

    if (Test-Path $msiPath) {
        Remove-Item -LiteralPath $msiPath -Force
    }

    & $wixPath build `
        -arch x64 `
        -culture en-us `
        -ext WixToolset.UI.wixext `
        -intermediatefolder $wixBuildRoot `
        -b AppBundle=$bundleDir `
        -d Version=$Version `
        -d Manufacturer="$Manufacturer" `
        -d ProductUrl="$productUrl" `
        -d AppIconPath="$iconPath" `
        -d LicenseRtfPath="$licensePath" `
        -o $msiPath `
        $wixSource

    if ($LASTEXITCODE -ne 0) {
        throw "MSI build failed with exit code $LASTEXITCODE."
    }

    Write-Host ""
    Write-Host "MSI build complete:"
    Write-Host "  MSI: $msiPath"
}
finally {
    Pop-Location
}
