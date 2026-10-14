@echo off
setlocal
cd /d "%~dp0"

where node >nul 2>&1
if errorlevel 1 (
  echo Node.js is not installed or is not available in PATH.
  echo Install the current Node.js LTS release, then run this file again.
  pause
  exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
  echo npm is not available. Reinstall Node.js LTS and try again.
  pause
  exit /b 1
)

if not exist "node_modules\expo" (
  echo Installing PetCare Mobile dependencies...
  call npm ci
  if errorlevel 1 goto failed
)

echo Starting PetCare Mobile...
echo Scan the Expo QR code with Expo Go, or choose an available emulator.
call npm start -- %*
if errorlevel 1 goto failed
exit /b 0

:failed
echo.
echo PetCare Mobile could not start. Check the error above and try again.
pause
exit /b 1
