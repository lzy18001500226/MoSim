@echo off
setlocal
title MoSim C99 Takeoff Hover Land

echo.
echo [MoSim] Running graphical C99: arm, take off, hover, land, and disarm.
echo [MoSim] The new Results\sunray_ros1 run directory contains the evidence and logs.
echo.

wsl -d Ubuntu-20.04 --exec bash -lc "cd /mnt/c/Users/HP/Desktop/MoSim && PX4CTRL_CORE_PROFILE=graphical_c99 bash Scripts/sunray/run_px4ctrl_fastlio_hover_gate.sh"
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
