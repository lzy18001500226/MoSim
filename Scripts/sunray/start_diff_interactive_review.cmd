@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%start_diff_interactive_review.ps1" %*
exit /b %ERRORLEVEL%
