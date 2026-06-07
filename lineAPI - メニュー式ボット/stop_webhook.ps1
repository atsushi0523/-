# Free port 3000 (stop duplicate webhook servers)
$conns = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
if (-not $conns) {
    Write-Host "Port 3000 is free. Run: .\start_webhook.ps1"
    exit 0
}

foreach ($c in $conns) {
    $procId = $c.OwningProcess
    $name = (Get-Process -Id $procId -ErrorAction SilentlyContinue).ProcessName
    Write-Host "Stopping PID $procId ($name)..."
    Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 1
Write-Host "Done. Now run: .\start_webhook.ps1"
