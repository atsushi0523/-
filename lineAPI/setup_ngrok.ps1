# Register ngrok authtoken from .env (run once)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$ngrok = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe"

if (-not (Test-Path $ngrok)) {
    throw "ngrok not found. Run: winget install ngrok.ngrok"
}

$token = $null
foreach ($line in Get-Content ".env" -Encoding UTF8) {
    $text = $line.Trim()
    if ($text.StartsWith("NGROK_AUTHTOKEN=")) {
        $token = $text.Substring(16).Trim()
        break
    }
}

if (-not $token -or $token -eq "your_ngrok_authtoken_here") {
    throw "Set NGROK_AUTHTOKEN in .env"
}

& $ngrok "config" "add-authtoken" $token
if ($LASTEXITCODE -ne 0) {
    throw "Failed to save authtoken"
}

Write-Host "OK: authtoken saved. Next run: .\start_ngrok.ps1"
