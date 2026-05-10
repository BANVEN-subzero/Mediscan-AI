@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
set "BACKEND=%~dp0backend"

echo.
echo ==============================
echo  MediScan AI - Local Runner
echo ==============================
echo Root:     %ROOT%
echo Backend:  %BACKEND%
echo.

if not exist "%BACKEND%\main.py" (
  echo [ERROR] Backend not found at: %BACKEND%\main.py
  pause
  exit /b 1
)

if not exist "%BACKEND%\.env" (
  echo ALLOWED_ORIGINS=*> "%BACKEND%\.env"
  echo JWT_SECRET_KEY=dev-change-me>> "%BACKEND%\.env"
  echo [INFO] Created default .env
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

REM Write backend launcher script
echo @echo off > "%ROOT%\_start_backend.bat"
echo cd /d "%BACKEND%" >> "%ROOT%\_start_backend.bat"
echo "%BACKEND%\.venv\Scripts\python.exe" main.py >> "%ROOT%\_start_backend.bat"
echo pause >> "%ROOT%\_start_backend.bat"

REM Write frontend launcher script
echo @echo off > "%ROOT%\_start_frontend.bat"
echo cd /d "%ROOT%" >> "%ROOT%\_start_frontend.bat"
echo py -m http.server 5500 >> "%ROOT%\_start_frontend.bat"
echo pause >> "%ROOT%\_start_frontend.bat"

echo [INFO] Starting backend on http://127.0.0.1:8000 ...
start "MediScan Backend" "%ROOT%\_start_backend.bat"

echo [INFO] Starting frontend on http://127.0.0.1:5500 ...
start "MediScan Frontend" "%ROOT%\_start_frontend.bat"

echo [INFO] Waiting for servers to start...
ping 127.0.0.1 -n 5 >nul

echo [INFO] Opening app in browser...
start "" "http://127.0.0.1:5500/mediscan-ai.html"

echo.
echo [DONE] MediScan AI is running!
echo  Backend:  http://127.0.0.1:8000
echo  Frontend: http://127.0.0.1:5500/mediscan-ai.html
echo.
echo Close the two server windows to stop the app.
echo.
endlocal
