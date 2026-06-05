@echo off
setlocal
set UV_PROJECT_ENVIRONMENT=.venv-win
set BLENDER_HOST=127.0.0.1
set BLENDER_PORT=9876
set DISABLE_TELEMETRY=true
cd /d C:\Users\HP\Desktop\MoSim\Docs\Skills\Blender-MCP
"C:\Users\HP\.local\bin\uv.exe" run blender-mcp
