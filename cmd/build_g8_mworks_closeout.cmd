@echo off
setlocal
for %%I in ("%~dp0..") do cd /d "%%~fI"
python Scripts\sunray\px4ctrl_golden_slice\build_g8_mworks_full_loop_closeout.py
set EXIT_CODE=%ERRORLEVEL%
echo.
echo G8 closeout exit code: %EXIT_CODE%
pause
exit /b %EXIT_CODE%
