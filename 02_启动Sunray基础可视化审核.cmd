@echo off
setlocal
title MoSim Sunray Basic Visual Review (No UE)

set "MOSIM_ROOT=%~dp0"
set "LAUNCHER=%MOSIM_ROOT%Scripts\sunray\start_sunray_ros1_foundation.ps1"

echo.
echo [MoSim] Starting Gazebo visual review without UE or flight control.
echo [MoSim] The aircraft remains on the ground and unarmed.
echo [MoSim] When READY appears, inspect Gazebo. Press Ctrl+C in this terminal to stop the review.
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%LAUNCHER%" -Gui -Review
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if "%EXIT_CODE%"=="0" (
    echo [MoSim] Visual review ended normally.
) else (
    echo [MoSim] Visual review failed. Read the failure excerpt above, then open the printed Results\sunray_ros1 run directory.
)
echo [MoSim] Exit code: %EXIT_CODE%
pause
exit /b %EXIT_CODE%
