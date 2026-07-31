@echo off
setlocal
title MoSim Ground Station Launcher

for %%I in ("%~dp0..") do set "MOSIM_ROOT=%%~fI"
set "LAUNCHER=%MOSIM_ROOT%\Scripts\ui\run_flight_console.ps1"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%LAUNCHER%"
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
    echo.
    echo [MoSim] Ground station failed. Review the error above and the startup logs.
    echo [MoSim] Exit code: %EXIT_CODE%
    pause
)
exit /b %EXIT_CODE%
