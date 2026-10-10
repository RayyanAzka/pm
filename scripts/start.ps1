$ErrorActionPreference = "Stop"

$rootDir = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $rootDir "backend"
$logFile = Join-Path $rootDir ".pm-server.log"
$pidFile = Join-Path $rootDir ".pm-server.pid"

Set-Location $backendDir

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is required. Install it with: pip install uv"
}

if (-not (Test-Path ".venv")) {
    uv venv .venv --python 3.12
}

uv sync

$errorLogFile = Join-Path $rootDir ".pm-server-error.log"

$process = Start-Process -FilePath "uv" -ArgumentList "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" -WorkingDirectory $backendDir -RedirectStandardOutput $logFile -RedirectStandardError $errorLogFile -PassThru

$process.Id | Set-Content -Path $pidFile
Write-Host "PM server started on http://localhost:8000"
