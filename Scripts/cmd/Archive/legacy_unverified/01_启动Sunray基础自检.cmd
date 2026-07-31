@echo off
setlocal
title MoSim Sunray Basic Check (No UE)

for %%I in ("%~dp0..") do set "MOSIM_ROOT=%%~fI"
set "LAUNCHER=%MOSIM_ROOT%\Scripts\sunray\start_sunray_ros1_foundation.ps1"

echo.
echo [MoSim] Starting Sunray ROS1 basic check without UE or flight control.
echo [MoSim] This checks Gazebo, PX4, MAVROS, and the MID360 point cloud.
echo [MoSim] Keep this window open to read the result or any error excerpt.
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%LAUNCHER%"
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if "%EXIT_CODE%"=="0" (
    echo [MoSim] Basic check passed. The exact evidence directory was printed above.
) else (
    echo [MoSim] Basic check failed. Read the failure excerpt above, then open the printed Results\sunray_ros1 run directory.
)
echo [MoSim] Exit code: %EXIT_CODE%
pause
exit /b %EXIT_CODE%
