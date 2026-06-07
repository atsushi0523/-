# Start ngrok tunnel to port 3000 (keep webhook_server.py running)
$ErrorActionPreference = "Stop"

$ngrok = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe"

if (-not (Test-Path $ngrok)) {
    throw "ngrok not found. Run: winget install ngrok.ngrok"
}

Write-Host "Starting ngrok on port 3000..."
Write-Host "Register in LINE: https://YOUR-URL.ngrok-free.app/webhook"
& $ngrok "http" "3000"
