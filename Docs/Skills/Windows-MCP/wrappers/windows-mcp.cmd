@echo off
setlocal
set ANONYMIZED_TELEMETRY=false
set WINDOWS_MCP_DEBUG=false
set WINDOWS_MCP_SCREENSHOT_BACKEND=auto
"C:\Users\HP\Desktop\MoSim\Docs\Skills\Windows-MCP\.venv\Scripts\windows-mcp.exe" serve --transport stdio
