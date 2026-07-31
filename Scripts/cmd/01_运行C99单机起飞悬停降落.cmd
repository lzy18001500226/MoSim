@echo off
setlocal
title MoSim C99 Takeoff Hover Land

for %%I in ("%~dp0\..\..") do set "MOSIM_ROOT=%%~fI"
for /f "usebackq delims=" %%I in (`wsl.exe -d Ubuntu-20.04 --exec wslpath -a -u "%MOSIM_ROOT%"`) do set "MOSIM_WSL_ROOT=%%I"
if not defined MOSIM_WSL_ROOT goto :wsl_path_failed

echo.
echo [MoSim] Running graphical C99: arm, take off, hover, land, and disarm.
echo [MoSim] The new Results\sunray_ros1 run directory contains the evidence and logs.
echo.

wsl.exe -d Ubuntu-20.04 --exec bash -lc "cd '%MOSIM_WSL_ROOT%' && PROJECT_ROOT='%MOSIM_WSL_ROOT%' PX4CTRL_CORE_PROFILE=graphical_c99 bash Scripts/sunray/run_px4ctrl_fastlio_hover_gate.sh"
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if "%EXIT_CODE%"=="0" (
    echo [MoSim] C99 nominal lifecycle passed. Inspect PX4CTRL_BASIC_MISSION_METRICS.json in the printed run directory.
) else (
    echo [MoSim] C99 nominal lifecycle did not pass. Read the terminal and the printed Results\sunray_ros1 directory.
)
echo [MoSim] Exit code: %EXIT_CODE%
pause
exit /b %EXIT_CODE%

:wsl_path_failed
echo.
echo [MoSim] Unable to map this project directory into Ubuntu-20.04.
echo [MoSim] Run 00_准备C99单机环境.cmd after fixing the WSL installation or project location.
pause
exit /b 2
