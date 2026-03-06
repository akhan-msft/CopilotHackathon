# ─────────────────────────────────────────────────────────────────────────────
# start.ps1 – Launch the Expense Tracker backend + frontend in isolated venvs
# Usage (from PowerShell):  .\start.ps1
# ─────────────────────────────────────────────────────────────────────────────

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir  = Join-Path $ScriptDir "backend"
$FrontendDir = Join-Path $ScriptDir "frontend"

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  💰  Expense Tracker – Startup Script" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# ── Backend ──────────────────────────────────────────────────────────────────
Write-Host "📦 Setting up backend virtual environment..." -ForegroundColor Yellow
Set-Location $BackendDir
if (-Not (Test-Path ".venv")) {
    python -m venv .venv
}
& ".\.venv\Scripts\Activate.ps1"
pip install -q -r requirements.txt
deactivate

Write-Host "🚀 Starting Flask backend on http://localhost:5000 ..." -ForegroundColor Green
$BackendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    & ".\.venv\Scripts\python.exe" app.py
} -ArgumentList $BackendDir

Write-Host "   Backend Job ID: $($BackendJob.Id)"

# Give Flask a moment to start
Start-Sleep -Seconds 2

# ── Frontend ─────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "📦 Setting up frontend virtual environment..." -ForegroundColor Yellow
Set-Location $FrontendDir
if (-Not (Test-Path ".venv")) {
    python -m venv .venv
}
& ".\.venv\Scripts\Activate.ps1"
pip install -q -r requirements.txt
deactivate

Write-Host "🚀 Starting Streamlit frontend on http://localhost:8501 ..." -ForegroundColor Green
$FrontendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    & ".\.venv\Scripts\streamlit.exe" run app.py --server.port 8501 --server.headless true
} -ArgumentList $FrontendDir

Write-Host "   Frontend Job ID: $($FrontendJob.Id)"

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  ✅  Both services are running!" -ForegroundColor Green
Write-Host "  🔗  Frontend:  http://localhost:8501" -ForegroundColor White
Write-Host "  🔗  Backend:   http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "  Press Ctrl+C to stop both services." -ForegroundColor Gray
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

try {
    # Keep running and stream output
    while ($true) {
        $BackendJob  | Receive-Job
        $FrontendJob | Receive-Job
        Start-Sleep -Seconds 2
    }
} finally {
    Write-Host "🛑 Stopping services..." -ForegroundColor Red
    Stop-Job  $BackendJob, $FrontendJob
    Remove-Job $BackendJob, $FrontendJob
}
