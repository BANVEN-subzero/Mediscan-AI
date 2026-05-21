@echo off
setlocal EnableExtensions
set "BACKEND=%~dp0backend"

echo ==========================================
echo  MediScan AI - Backend Viewer/Runner
echo ==========================================
echo.

if not exist "%BACKEND%\main.py" (
    echo [ERROR] Backend not found at: %BACKEND%\main.py
    pause
    exit /b 1
)

if not exist "%BACKEND%\.venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found. Please run run-mediscan.bat first.
    pause
    exit /b 1
)

echo [INFO] Checking if port 8000 is available...
netstat -ano | findstr :8000 >nul
if %errorlevel% == 0 (
    echo [WARN] Something is already running on port 8000.
    echo [WARN] If the app is already running, this window will show logs.
    echo [WARN] If you get a 'Bind Error', please close other backend windows.
    echo.
)

echo [INFO] Starting backend in debug mode...
echo [INFO] Press Ctrl+C to stop.
echo.

cd /d "%BACKEND%"
set FLASK_ENV=development
set FLASK_DEBUG=1
"%BACKEND%\.venv\Scripts\python.exe" main.py

echo.
echo [INFO] Backend stopped.
pause
