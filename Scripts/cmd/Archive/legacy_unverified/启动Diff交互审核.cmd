@echo off
setlocal

for %%I in ("%~dp0..") do cd /d "%%~fI"
call "Scripts\sunray\start_diff_interactive_review.cmd" %*
exit /b %ERRORLEVEL%
