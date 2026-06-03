# Start webhook server (only one instance)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$listeners = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
if ($listeners) {
    Write-Host "ERROR: Port 3000 is already in use."
    Write-Host "Run this first: .\stop_webhook.ps1"
    exit 1
}

Write-Host "Starting webhook server. Keep this terminal open."
python webhook_server.py
