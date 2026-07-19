@echo off
setlocal
title MoSim Ground Station Launcher

set "MOSIM_ROOT=%~dp0"
set "LAUNCHER=%MOSIM_ROOT%Scripts\ui\run_qgc_with_ue.ps1"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%LAUNCHER%"
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
    echo.
    echo [MoSim] Ground station failed. Review the error above and the startup logs.
    echo [MoSim] Exit code: %EXIT_CODE%
    pause
)
exit /b %EXIT_CODE%
