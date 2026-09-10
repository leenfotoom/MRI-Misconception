$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Running backend tests" -ForegroundColor Cyan
Push-Location (Join-Path $ProjectRoot "backend")
$env:DATABASE_URL = "sqlite+pysqlite:///:memory:"
$env:AUTO_CREATE_SCHEMA = "0"
.\.venv\Scripts\python.exe -m pytest -q
Pop-Location

Write-Host "Building typed production frontend" -ForegroundColor Cyan
Push-Location (Join-Path $ProjectRoot "frontend")
npm run build
Pop-Location

Write-Host "All checks passed" -ForegroundColor Green

