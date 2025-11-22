# FairStake AI - Backend Startup Script (No Reload for Stability)

Write-Host "Starting FairStake AI Backend..." -ForegroundColor Green

cd backend

# Activate venv from project root
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ..\.venv\Scripts\Activate.ps1

# Start server WITHOUT reload
Write-Host "Starting FastAPI server on http://localhost:8000" -ForegroundColor Green
Write-Host "API docs available at http://localhost:8000/docs" -ForegroundColor Cyan
uvicorn app.main:app --host 0.0.0.0 --port 8000
