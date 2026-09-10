$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $ProjectRoot "backend"
$Frontend = Join-Path $ProjectRoot "frontend"

Push-Location $ProjectRoot
docker compose up -d postgres
Pop-Location

Start-Process powershell -WorkingDirectory $Backend -ArgumentList @(
    "-NoExit",
    "-Command",
    ".\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"
)

Start-Process powershell -WorkingDirectory $Frontend -ArgumentList @(
    "-NoExit",
    "-Command",
    "npm run dev"
)

Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"
Write-Host "Misconception MRI is starting at http://localhost:3000" -ForegroundColor Green

