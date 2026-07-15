@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
wsl -d Ubuntu-20.04 --exec bash -lc "cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/stop_diff_interactive_review.sh"
exit /b %ERRORLEVEL%
