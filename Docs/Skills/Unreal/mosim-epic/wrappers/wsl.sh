#!/usr/bin/env bash
set -euo pipefail

# Project-local WSL wrapper for MoSim's Epic/Fab/scene-source MCP.
# It does not launch Epic Launcher, log in, download assets, or operate UE.

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
exec "${UV_BIN}" run --with mcp python \
  Docs/Skills/Unreal/mosim-epic/mcp/server.py serve "$@"
