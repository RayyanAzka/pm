$ErrorActionPreference = "Stop"

$rootDir = Split-Path -Parent $PSScriptRoot
$pidFile = Join-Path $rootDir ".pm-server.pid"

if (-not (Test-Path $pidFile)) {
    Write-Host "No PM server PID file found."
    exit 0
}

$processId = Get-Content $pidFile
if ($processId) {
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $processId -Force
        Write-Host "PM server stopped."
    } else {
        Write-Host "PM server was not running."
    }
}

$listenerIds = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique
foreach ($listenerId in $listenerIds) {
    $listener = Get-CimInstance Win32_Process -Filter "ProcessId = $listenerId"
    if ($listener.CommandLine -match "uvicorn" -and $listener.CommandLine -match "app\.main:app" -and $listener.CommandLine -match "--port 8000") {
        Stop-Process -Id $listenerId -Force
        Write-Host "PM server listener stopped."
    }
}

Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
