@echo off
setlocal
cd /d "%~dp0\.."
set "port=%~1"
if "%port%"=="" set "port=COM3"

if not exist ".venv\Scripts\python.exe" (
  echo Run scripts\setup.bat first.
  exit /b 1
)
if not exist "dist\firmware.bin" (
  echo Build images first: scripts\build.bat
  exit /b 1
)
if not exist "dist\littlefs.bin" (
  echo Build images first: scripts\build.bat
  exit /b 1
)

echo Flashing %port%. Put the board into bootloader mode first:
echo USB2UART, hold FLSH while connecting USB, then release FLSH.
.venv\Scripts\python.exe -m esptool --port "%port%" --chip esp8266 --baud 460800 --before no-reset --after hard-reset ^
  write-flash --flash-mode dout --flash-freq 40m --flash-size 2MB ^
  0x0 dist\firmware.bin 0x1C0000 dist\littlefs.bin
if errorlevel 1 exit /b %errorlevel%
echo Done. Press RST without FLSH.
