@echo off
setlocal
title MoSim Factory Three-UAV Formation Stop

for %%I in ("%~dp0..") do set "PROJECT_ROOT=%%~fI"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PROJECT_ROOT%\Scripts\sunray\stop_factory_l2_swarm_formation_runtime.ps1"
set "EXIT_CODE=%ERRORLEVEL%"
echo.
pause
exit /b %EXIT_CODE%
