@echo off
REM MediScan Docker Run Script
REM This script builds and runs the MediScan application using Docker Compose

echo ========================================
echo   MediScan Docker Deployment
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [1/4] Checking environment file...
if not exist .env (
    echo Creating .env from .env.example...
    copy .env.example .env >nul
    echo WARNING: Please edit .env and set your production values before running in production!
    echo.
) else (
    echo Environment file found.
)

echo [2/4] Building Docker images...
docker-compose build
if %errorlevel% neq 0 (
    echo ERROR: Docker build failed. Check the error messages above.
    pause
    exit /b 1
)

echo [3/4] Starting Docker containers...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Failed to start containers. Check the error messages above.
    pause
    exit /b 1
)

echo [4/4] Waiting for services to be healthy...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo   Deployment Successful!
echo ========================================
echo.
echo Frontend: http://localhost
echo Backend API: http://localhost:8000
echo Health Check: http://localhost:8000/health
echo.
echo To view logs: docker-compose logs -f
echo To stop: docker-compose down
echo.
echo Press any key to open the application in your browser...
pause >nul

start http://localhost

echo.
echo Application is running. Press Ctrl+C in this window to stop viewing logs.
echo To stop the containers, run: docker-compose down
echo.
docker-compose logs -f
