
# Change to script directory
Set-Location $PSScriptRoot

Write-Host "=== Installing dependencies in venv ===" -ForegroundColor Cyan
& .\.venv\Scripts\pip.exe install --upgrade pip
& .\.venv\Scripts\pip.exe install flask flask-cors flask-jwt-extended sqlalchemy numpy pandas scikit-learn boto3 watchtower

Write-Host "`n=== Starting MediScan Backend ===" -ForegroundColor Green
& .\.venv\Scripts\python.exe main.py
