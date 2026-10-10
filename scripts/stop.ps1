$ErrorActionPreference = "Stop"

$rootDir = Split-Path -Parent $PSScriptRoot
$pidFile = Join-Path $rootDir ".pm-server.pid"

if (-not (Test-Path $pidFile)) {
    Write-Host "No PM server PID file found."
    exit 0
}

$pid = Get-Content $pidFile
if ($pid) {
    $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $pid -Force
        Write-Host "PM server stopped."
    } else {
        Write-Host "PM server was not running."
    }
}

Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
