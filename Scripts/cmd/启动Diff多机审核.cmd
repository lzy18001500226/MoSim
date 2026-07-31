@echo off
setlocal

for %%I in ("%~dp0..") do cd /d "%%~fI"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%CD%\Scripts\sunray\start_diff_swarm_review.ps1" %*
exit /b %ERRORLEVEL%
