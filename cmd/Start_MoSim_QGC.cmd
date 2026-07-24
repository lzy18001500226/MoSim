@echo off
setlocal

echo [MoSim] Compatibility launcher. Use the MoSim ground station launcher.
call "%~dp0启动MoSim地面站.cmd"
exit /b %ERRORLEVEL%
