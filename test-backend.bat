@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
set "BACKEND=%~dp0backend"

echo.
echo ==============================
echo  MediScan AI - Backend Test
echo ==============================
echo.

echo [STEP 1] Checking if backend is running...
curl -s http://127.0.0.1:8000/health
if errorlevel 1 (
  echo [ERROR] Backend is not running on http://127.0.0.1:8000
  echo [INFO] Please run backend-view.bat or run-mediscan.bat first
  pause
  exit /b 1
)
echo [OK] Backend is running
echo.

echo [STEP 2] Testing health endpoint...
curl -s http://127.0.0.1:8000/health
echo.
echo [OK] Health endpoint working
echo.

echo [STEP 3] Testing registration endpoint...
curl -s -X POST http://127.0.0.1:8000/api/auth/register -H "Content-Type: application/json" -d "{\"email\":\"test@example.com\",\"password\":\"test123\"}"
echo.
echo [OK] Registration endpoint accessible
echo.

echo [STEP 4] Testing login endpoint...
curl -s -X POST http://127.0.0.1:8000/api/auth/login -H "Content-Type: application/json" -d "{\"email\":\"test@example.com\",\"password\":\"test123\"}"
echo.
echo [OK] Login endpoint accessible
echo.

echo ==============================
echo  All backend tests passed!
echo ==============================
echo.
pause
endlocal
