@echo off
setlocal
title Stop All MoSim Simulation

for %%I in ("%~dp0..") do set "MOSIM_ROOT=%%~fI"
set "STOPPER=%MOSIM_ROOT%\Scripts\ui\stop_all_simulation.ps1"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%STOPPER%"
set "EXIT_CODE=%ERRORLEVEL%"
echo.
if "%EXIT_CODE%"=="0" (
    echo [MoSim] All managed simulation processes were stopped.
) else (
    echo [MoSim] Stop failed. Exit code: %EXIT_CODE%
)
pause
exit /b %EXIT_CODE%
