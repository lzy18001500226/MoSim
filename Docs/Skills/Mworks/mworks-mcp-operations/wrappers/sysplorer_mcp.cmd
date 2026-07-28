@echo off
setlocal
set "MOSIM_ROOT=%~dp0..\..\..\..\.."
set "MCP_WORKSPACE_DIR=%MOSIM_ROOT%"
set "MWORKS_PYTHON=D:\Program Files\MWORKS\Sysplorer 2026a\External\python64\python.exe"
"%MWORKS_PYTHON%" "%MOSIM_ROOT%\Scripts\mworks\sysplorer_mcp_wsl_entry.py" %*
