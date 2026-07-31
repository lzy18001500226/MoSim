@echo off
setlocal

for %%I in ("%~dp0..") do cd /d "%%~fI"
call "Scripts\sunray\stop_diff_interactive_review.cmd" %*
if not "%~1"=="--no-pause" pause
exit /b %ERRORLEVEL%
