$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $ProjectRoot "backend"
$Frontend = Join-Path $ProjectRoot "frontend"

Write-Host "[1/5] Preparing configuration" -ForegroundColor Cyan
if (-not (Test-Path (Join-Path $Backend ".env"))) {
    Copy-Item (Join-Path $Backend ".env.example") (Join-Path $Backend ".env")
}
if (-not (Test-Path (Join-Path $Frontend ".env.local"))) {
    Copy-Item (Join-Path $Frontend ".env.local.example") (Join-Path $Frontend ".env.local")
}

Write-Host "[2/5] Starting PostgreSQL" -ForegroundColor Cyan
Push-Location $ProjectRoot
docker compose up -d postgres
Pop-Location

Write-Host "[3/5] Preparing Python backend" -ForegroundColor Cyan
Push-Location $Backend
if (-not (Test-Path ".venv")) {
    py -3 -m venv .venv
}
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\alembic.exe upgrade head
Pop-Location

Write-Host "[4/5] Preparing Next.js frontend" -ForegroundColor Cyan
Push-Location $Frontend
npm ci
Pop-Location

Write-Host "[5/5] Setup complete" -ForegroundColor Green
Write-Host "Add CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN to backend/.env, then run .\start-dev.ps1"

