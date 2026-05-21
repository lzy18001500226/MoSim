echo off
set regpath="HKEY_CLASSES_ROOT\Installer\Dependencies\VC,redist.x64,amd64,14.30,bundle"
REG QUERY %regpath% /v Version
if %errorlevel% == 1 start "" "%~dp0\VC_redist.x64.exe" /quiet /norestart
echo on
