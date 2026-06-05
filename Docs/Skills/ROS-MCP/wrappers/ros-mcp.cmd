@echo off
setlocal
set UV_PROJECT_ENVIRONMENT=.venv-win
cd /d C:\Users\HP\Desktop\MoSim\Docs\Skills\ROS-MCP
"C:\Users\HP\.local\bin\uv.exe" run ros-mcp --transport stdio
