@echo off
setlocal

echo Closing all RViz windows...
wsl -d Ubuntu-20.04 --exec bash -lc "pkill -f '^rviz($| )' >/dev/null 2>&1 || pkill -f 'rviz.*\.rviz' >/dev/null 2>&1 || true"
powershell.exe -NoProfile -Command "Get-Process rviz -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue"
echo Done. Only RViz processes were targeted.
pause
