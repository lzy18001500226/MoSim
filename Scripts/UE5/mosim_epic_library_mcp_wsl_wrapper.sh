#!/usr/bin/env bash
set -euo pipefail

# Project-local WSL wrapper for the read-only Epic/Fab/Launcher inventory MCP.
# This wrapper intentionally does not launch Epic Games Launcher or Unreal
# Editor. It only exposes sanitized local-cache inventory through MCP tools.

PROJECT_ROOT="${MOSIM_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
UV_BIN="${UV_BIN:-/home/linux/.local/bin/uv}"

if [[ ! -x "${UV_BIN}" ]]; then
  UV_BIN="$(command -v uv || true)"
fi

if [[ -z "${UV_BIN}" || ! -x "${UV_BIN}" ]]; then
  echo "uv not found. Install uv in WSL or set UV_BIN." >&2
  exit 127
fi

cd "${PROJECT_ROOT}"
export UV_LINK_MODE="${UV_LINK_MODE:-copy}"
exec "${UV_BIN}" run --with mcp python Scripts/UE5/mosim_epic_library_mcp.py serve "$@"
