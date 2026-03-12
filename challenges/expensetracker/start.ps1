<#
.SYNOPSIS
    Sets up virtual environments and starts both the backend and frontend.
#>

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

# ── Backend setup ─────────────────────────────────────────────────────────────
$backendDir = Join-Path $root "backend"
$backendVenv = Join-Path $backendDir ".venv"

if (-not (Test-Path (Join-Path $backendVenv "Scripts\python.exe"))) {
    Write-Host "Creating backend virtual environment..." -ForegroundColor Cyan
    python -m venv $backendVenv
}

Write-Host "Installing backend dependencies..." -ForegroundColor Cyan
& (Join-Path $backendVenv "Scripts\pip.exe") install -q -r (Join-Path $backendDir "requirements.txt")

# ── Frontend setup ────────────────────────────────────────────────────────────
$frontendDir = Join-Path $root "frontend"
$frontendVenv = Join-Path $frontendDir ".venv"

if (-not (Test-Path (Join-Path $frontendVenv "Scripts\python.exe"))) {
    Write-Host "Creating frontend virtual environment..." -ForegroundColor Cyan
    python -m venv $frontendVenv
}

Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
& (Join-Path $frontendVenv "Scripts\pip.exe") install -q -r (Join-Path $frontendDir "requirements.txt")

# ── Start both servers ────────────────────────────────────────────────────────
Write-Host ""
Write-Host "Starting backend (Flask) on http://localhost:5000 ..." -ForegroundColor Green
$backendJob = Start-Process -FilePath (Join-Path $backendVenv "Scripts\python.exe") `
    -ArgumentList (Join-Path $backendDir "app.py") `
    -WorkingDirectory $backendDir `
    -PassThru -NoNewWindow

# Give the backend a moment to bind the port
Start-Sleep -Seconds 2

Write-Host "Starting frontend (static server) on http://localhost:8501 ..." -ForegroundColor Green
$frontendJob = Start-Process -FilePath (Join-Path $frontendVenv "Scripts\python.exe") `
    -ArgumentList (Join-Path $frontendDir "app.py") `
    -WorkingDirectory $frontendDir `
    -PassThru -NoNewWindow

Write-Host ""
Write-Host "Both services are running. Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host "  Backend  -> http://localhost:5000" -ForegroundColor Gray
Write-Host "  Frontend -> http://localhost:8501" -ForegroundColor Gray

try {
    # Wait for either process to exit
    while (-not $backendJob.HasExited -and -not $frontendJob.HasExited) {
        Start-Sleep -Seconds 1
    }
} finally {
    # Clean up both processes on exit
    Write-Host "`nShutting down..." -ForegroundColor Red
    if (-not $backendJob.HasExited)  { Stop-Process -Id $backendJob.Id  -Force -ErrorAction SilentlyContinue }
    if (-not $frontendJob.HasExited) { Stop-Process -Id $frontendJob.Id -Force -ErrorAction SilentlyContinue }
    Write-Host "Done." -ForegroundColor Red
}
