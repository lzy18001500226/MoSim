@echo off
setlocal
title MoSim C99 Motor Fault Recovery

for %%I in ("%~dp0\..\..") do set "MOSIM_ROOT=%%~fI"
for /f "usebackq delims=" %%I in (`wsl.exe -d Ubuntu-20.04 --exec wslpath -a -u "%MOSIM_ROOT%"`) do set "MOSIM_WSL_ROOT=%%I"
if not defined MOSIM_WSL_ROOT goto :wsl_path_failed

echo.
echo [MoSim] Running graphical C99 with rotor-1 effectiveness 0.85 and a nominal reset.
echo [MoSim] The runner owns the mission; the fault injector never replaces px4ctrl.
echo.

wsl.exe -d Ubuntu-20.04 --exec bash -lc "cd '%MOSIM_WSL_ROOT%' && PROJECT_ROOT='%MOSIM_WSL_ROOT%' PX4CTRL_CORE_PROFILE=graphical_c99 GUI=false REVIEW_OPEN_RVIZ=false REVIEW_START_CLOUD_NODE=false REVIEW_START_OCCUPANCY_NODE=false MOSIM_UE_STATE_STREAM=false RECORD_ROSBAG=false bash Scripts/sunray/run_px4ctrl_fastlio_fault_demo_gate.sh --factory-l2-fault-demo"
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if "%EXIT_CODE%"=="0" (
    echo [MoSim] C99 motor fault and recovery acknowledgement passed. Inspect DEMO_STATUS.json.
) else (
    echo [MoSim] C99 motor fault demonstration did not pass. Read the terminal and the printed Results\sunray_ros1 directory.
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
