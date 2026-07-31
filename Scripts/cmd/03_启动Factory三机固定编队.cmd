@echo off
setlocal
title MoSim Factory Three-UAV Formation Backend

for %%I in ("%~dp0..") do set "PROJECT_ROOT=%%~fI"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PROJECT_ROOT%\Scripts\sunray\start_factory_l2_swarm_formation_backend.ps1" -KeepAlive
set "EXIT_CODE=%ERRORLEVEL%"
echo.
pause
exit /b %EXIT_CODE%
