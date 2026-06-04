@echo off
REM MediScan Local Development Script
REM This script runs the MediScan application locally without Docker

echo ========================================
echo   MediScan Local Development
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.11 or higher from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists and is valid
if not exist backend\.venv\Scripts\activate.bat (
    echo [1/5] Creating virtual environment...
    if exist backend\.venv (
        echo Removing broken virtual environment...
        rmdir /s /q backend\.venv
    )
    cd backend
    python -m venv .venv --include-pip
    cd ..
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo [2/5] Activating virtual environment and installing dependencies...
call backend\.venv\Scripts\activate.bat
cd backend
python -m ensurepip --upgrade
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)
cd ..

echo [3/5] Starting backend server...
start "MediScan Backend" cmd /k "cd backend && call .venv\Scripts\activate.bat && python main.py"
timeout /t 5 /nobreak >nul

echo [4/5] Starting frontend server...
start "MediScan Frontend" cmd /k "cd frontend && python -m http.server 8080"
timeout /t 3 /nobreak >nul

echo [5/5] Waiting for services to start...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   Local Development Started!
echo ========================================
echo.
echo Frontend: http://localhost:8080
echo Backend API: http://localhost:8000
echo Health Check: http://localhost:8000/health
echo.
echo Press any key to open the application in your browser...
pause >nul

start http://localhost:8080

echo.
echo Application is running locally.
echo Close the backend and frontend command windows to stop the servers.
echo.
pause
