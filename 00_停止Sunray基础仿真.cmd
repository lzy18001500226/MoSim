@echo off
setlocal
title Stop MoSim Sunray Basic Runtime

set "MOSIM_ROOT=%~dp0"
set "STOPPER=%MOSIM_ROOT%Scripts\sunray\stop_sunray_ros1_foundation.ps1"

echo.
echo [MoSim] Stopping only the managed Sunray basic runtime.
echo [MoSim] A non-foundation task is intentionally not stopped by this command.
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%STOPPER%"
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if "%EXIT_CODE%"=="0" (
    echo [MoSim] Stop request finished.
) else (
    echo [MoSim] Stop request was refused or failed. Read the message above.
)
echo [MoSim] Exit code: %EXIT_CODE%
pause
exit /b %EXIT_CODE%
