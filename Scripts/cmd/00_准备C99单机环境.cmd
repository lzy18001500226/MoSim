@echo off
setlocal
title MoSim C99 Runtime Preparation

set "MOSIM_WSL_ROOT=/mnt/c/Users/HP/Desktop/MoSim"

echo.
echo [MoSim] Preparing the source-local C99 single-aircraft runtime.
echo [MoSim] Keep this terminal open. Build and preflight output is the first error surface.
echo.

wsl -d Ubuntu-20.04 --exec bash -lc "cd %MOSIM_WSL_ROOT% && bash Scripts/sunray/build_local_px4_sitl.sh --build --jobs 2"
if errorlevel 1 goto :failed
wsl -d Ubuntu-20.04 --exec bash -lc "cd %MOSIM_WSL_ROOT% && bash Scripts/sunray/prepare_local_ros1_workspace.sh --profile foundation --build --verify --jobs 1"
if errorlevel 1 goto :failed
wsl -d Ubuntu-20.04 --exec bash -lc "cd %MOSIM_WSL_ROOT% && bash Scripts/sunray/prepare_local_ros1_workspace.sh --profile flight_adapter --build --verify --jobs 1"
if errorlevel 1 goto :failed
wsl -d Ubuntu-20.04 --exec bash -lc "cd %MOSIM_WSL_ROOT% && bash Scripts/sunray/prepare_local_ros1_workspace.sh --profile perception --build --verify --jobs 1"
if errorlevel 1 goto :failed
wsl -d Ubuntu-20.04 --exec bash -lc "cd %MOSIM_WSL_ROOT% && bash Scripts/sunray/prepare_local_ros1_workspace.sh --profile controller --build --verify --jobs 1 --px4ctrl-backend graphical_px4ctrl_c99"
if errorlevel 1 goto :failed
wsl -d Ubuntu-20.04 --exec bash -lc "cd %MOSIM_WSL_ROOT% && bash Scripts/sunray/check_sunray_ros1_runtime_preflight.sh"
if errorlevel 1 goto :failed

echo.
echo [MoSim] C99 runtime preparation completed. Run one C99 demonstration next.
pause
exit /b 0

:failed
set "EXIT_CODE=%ERRORLEVEL%"
echo.
echo [MoSim] Preparation failed. Read the first failure above before retrying.
echo [MoSim] Exit code: %EXIT_CODE%
pause
exit /b %EXIT_CODE%
