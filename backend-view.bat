@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
set "BACKEND=%~dp0backend"

echo.
echo ==============================
echo  MediScan AI - Backend Viewer
echo ==============================
echo Backend: %BACKEND%
echo.

if not exist "%BACKEND%\main.py" (
  echo [ERROR] Backend not found at: %BACKEND%\main.py
  pause
  exit /b 1
)

if not exist "%BACKEND%\.venv\Scripts\python.exe" (
  echo [INFO] Creating virtual environment...
  py -m venv "%BACKEND%\.venv"
  if errorlevel 1 (
    echo [ERROR] Failed to create venv. Is Python installed?
    pause
    exit /b 1
  )
)

set "REQ=%BACKEND%\requirements.txt"
set "REQ_STAMP=%BACKEND%\.venv\requirements.stamp.txt"

if not exist "%REQ%" (
  echo [ERROR] requirements.txt not found.
  pause
  exit /b 1
)

for %%F in ("%REQ%") do set "REQ_TIME=%%~tF"
set "OLD_REQ_TIME="
if exist "%REQ_STAMP%" set /p OLD_REQ_TIME=<"%REQ_STAMP%"

if not exist "%REQ_STAMP%" goto :install_deps
if not "%OLD_REQ_TIME%"=="%REQ_TIME%" goto :install_deps
echo [INFO] Python dependencies already up-to-date.
goto :check_models

:install_deps
echo [INFO] Installing Python dependencies...
"%BACKEND%\.venv\Scripts\python.exe" -m pip install --upgrade pip
"%BACKEND%\.venv\Scripts\python.exe" -m pip install -r "%REQ%"
if errorlevel 1 (
  echo [WARN] Full requirements install failed.
  echo [WARN] Attempting minimal install to allow the app to run with existing models...
  "%BACKEND%\.venv\Scripts\python.exe" -m pip install flask==3.0.3 flask-cors==4.0.1 flask-jwt-extended==4.6.0 sqlalchemy==2.0.32
  if errorlevel 1 (
    echo [ERROR] Failed to install minimal backend requirements.
    pause
    exit /b 1
  )
)
echo %REQ_TIME%> "%REQ_STAMP%"

:check_models
if not exist "%BACKEND%\models\condition_model.pkl" (
  echo [INFO] Training ML models - this takes ~30 seconds...
  "%BACKEND%\.venv\Scripts\python.exe" "%BACKEND%\train_model.py"
  if errorlevel 1 (
    echo [WARN] Model training failed.
    echo [WARN] The app can still run if backend\models\*.pkl already exist.
  )
)

echo.
echo [INFO] Starting backend viewer...
echo [INFO] Backend will run on http://127.0.0.1:8000
echo [INFO] Press Ctrl+C to stop
echo.

cd /d "%BACKEND%"
"%BACKEND%\.venv\Scripts\python.exe" main.py

pause
endlocal
