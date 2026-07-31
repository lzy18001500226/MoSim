@echo off
setlocal
title MoSim Factory Three-UAV Preflight

for %%I in ("%~dp0..") do set "PROJECT_ROOT=%%~fI"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PROJECT_ROOT%\Scripts\sunray\preflight_factory_l2_swarm_formation.ps1"
set "EXIT_CODE=%ERRORLEVEL%"
echo.
pause
exit /b %EXIT_CODE%
