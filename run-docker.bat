@echo off
title MediScan AI — Docker Launcher
color 0A

echo.
echo  =============================================
echo    MediScan AI — Docker Launcher
echo  =============================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Docker Desktop is not running.
    echo  Please start Docker Desktop and try again.
    echo.
    pause
    exit /b 1
)

echo  [OK] Docker Desktop is running.
echo.
echo  Building and starting MediScan AI...
echo  (This may take a few minutes on first run)
echo.

REM Navigate to the project folder
cd /d "%~dp0"

REM Build and start the containers
docker-compose up -d --build

if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Failed to start containers.
    echo  Run "docker-compose logs" to see what went wrong.
    echo.
    pause
    exit /b 1
)

echo.
echo  =============================================
echo    MediScan AI is starting up!
echo  =============================================
echo.
echo  Frontend: http://localhost
echo  Backend:  http://localhost:8000
echo.
echo  Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul

start "" http://localhost

echo.
echo  To stop the app, run:  docker-compose down
echo  To view logs, run:     docker-compose logs -f
echo.
pause
