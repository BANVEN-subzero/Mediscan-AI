
Set-Location $PSScriptRoot

Write-Host "=== Starting MediScan Backend ===" -ForegroundColor Green

# Ensure .venv exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# Install dependencies
Write-Host "Installing/updating dependencies..." -ForegroundColor Yellow
& .\.venv\Scripts\pip.exe install --upgrade pip | Out-Null
& .\.venv\Scripts\pip.exe install flask flask-cors flask-jwt-extended sqlalchemy numpy pandas scikit-learn boto3 watchtower

# Run backend
Write-Host "Starting backend server on http://127.0.0.1:8000..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop"
& .\.venv\Scripts\python.exe main.py
