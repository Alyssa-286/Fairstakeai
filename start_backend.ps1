# FairStake AI - Backend Startup Script (PowerShell)

Write-Host "Starting FairStake AI Backend..." -ForegroundColor Green

cd backend

# Check if venv exists at project root
if (-not (Test-Path "..\\.venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    cd ..
    python -m venv .venv
    cd backend
}

# Activate venv from project root
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ..\.venv\Scripts\Activate.ps1

# Install dependencies if needed
if (-not (Test-Path "..\\.venv\\Lib\\site-packages\\fastapi")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Check if model exists
if (-not (Test-Path "app\models\fairscore_model.pkl")) {
    Write-Host "Training FairScore model (first time only)..." -ForegroundColor Yellow
    python app\models\train_fairscore.py
}

# Start server
Write-Host "Starting FastAPI server on http://localhost:8000" -ForegroundColor Green
Write-Host "API docs available at http://localhost:8000/docs" -ForegroundColor Cyan
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000



