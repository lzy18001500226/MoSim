@echo off
setlocal
title MoSim C99 Wind Demonstration

for %%I in ("%~dp0\..\..") do set "MOSIM_ROOT=%%~fI"
for /f "usebackq delims=" %%I in (`wsl.exe -d Ubuntu-20.04 --exec wslpath -a -u "%MOSIM_ROOT%"`) do set "MOSIM_WSL_ROOT=%%I"
if not defined MOSIM_WSL_ROOT goto :wsl_path_failed

echo.
echo [MoSim] Running graphical C99 with a bounded Gazebo wind injection.
echo [MoSim] The runner waits for the source-local mission before applying the wind wrench.
echo.

wsl.exe -d Ubuntu-20.04 --exec bash -lc "cd '%MOSIM_WSL_ROOT%' && PROJECT_ROOT='%MOSIM_WSL_ROOT%' bash Scripts/sunray/run_px4ctrl_fastlio_wind_demo_gate.sh"
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

:wsl_path_failed
echo.
echo [MoSim] Unable to map this project directory into Ubuntu-20.04.
echo [MoSim] Run 00_准备C99单机环境.cmd after fixing the WSL installation or project location.
pause
exit /b 2
