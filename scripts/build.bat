@echo off
setlocal
cd /d "%~dp0\.."

if not exist ".venv\Scripts\python.exe" (
  echo Run scripts\setup.bat first.
  exit /b 1
)
if not exist ".venv\Scripts\pio.exe" (
  echo Run scripts\setup.bat first.
  exit /b 1
)

.venv\Scripts\python.exe scripts\build.py --platformio "%CD%\.venv\Scripts\pio.exe"
exit /b %errorlevel%
