@echo off
setlocal
cd /d "%~dp0\.."

where py >nul 2>nul
if errorlevel 1 (
  echo Python Launcher ^(py.exe^) was not found. Install Python 3.9 or newer.
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv
if errorlevel 1 exit /b %errorlevel%

call .venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 exit /b %errorlevel%
call .venv\Scripts\python.exe -m pip install -r requirements.txt platformio esptool
if errorlevel 1 exit /b %errorlevel%

echo Environment is ready: %CD%\.venv
