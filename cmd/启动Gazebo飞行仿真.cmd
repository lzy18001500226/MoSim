@echo off
setlocal
title MoSim Flight Simulation Status

for %%I in ("%~dp0..") do set "MOSIM_ROOT=%%~fI"
set "LAUNCHER=%MOSIM_ROOT%\Scripts\ui\start_flight_simulation.ps1"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%LAUNCHER%"
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
    echo.
    echo [MoSim] Flight simulation failed. Exit code: %EXIT_CODE%
    pause
)
exit /b %EXIT_CODE%
