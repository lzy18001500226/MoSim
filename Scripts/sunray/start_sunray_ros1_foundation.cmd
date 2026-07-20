@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_sunray_ros1_foundation.ps1"
set EXIT_CODE=%ERRORLEVEL%
echo.
echo Sunray ROS1 foundation launcher exited with code %EXIT_CODE%.
pause
exit /b %EXIT_CODE%
