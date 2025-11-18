# FairStake AI - Frontend Startup Script (PowerShell)

Write-Host "Starting FairStake AI Frontend..." -ForegroundColor Green

cd frontend

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Start dev server
Write-Host "Starting Vite dev server..." -ForegroundColor Green
Write-Host "Frontend will be available at http://localhost:5173" -ForegroundColor Cyan
npm run dev

