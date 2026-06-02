#!/usr/bin/env bash
set -euo pipefail

ROOT="/mnt/c/Users/HP/Desktop/MoSim/Docs/Skills/Blender-MCP"

export DISABLE_TELEMETRY="${DISABLE_TELEMETRY:-true}"
export BLENDER_HOST="${BLENDER_HOST:-127.0.0.1}"
export BLENDER_PORT="${BLENDER_PORT:-9876}"

exec "$ROOT/.venv/bin/python" -m blender_mcp.server
