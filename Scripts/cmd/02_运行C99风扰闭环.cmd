@echo off
setlocal
title MoSim C99 Wind Demonstration

echo.
echo [MoSim] Running graphical C99 with a bounded Gazebo wind injection.
echo [MoSim] The runner waits for the source-local mission before applying the wind wrench.
echo.

wsl -d Ubuntu-20.04 --exec bash -lc "cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/run_px4ctrl_fastlio_wind_demo_gate.sh"
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if "%EXIT_CODE%"=="0" (
    echo [MoSim] C99 wind lifecycle and injection acknowledgement passed. Inspect DEMO_STATUS.json.
) else (
    echo [MoSim] C99 wind demonstration did not pass. Read the terminal and the printed Results\sunray_ros1 directory.
)
echo [MoSim] Exit code: %EXIT_CODE%
pause
exit /b %EXIT_CODE%
