#!/usr/bin/env bash
set -euo pipefail

# Legacy wrapper for the open-source Flopperam Unreal MCP server.
# Keep this for rollback while MoSim's own `unreal_engine` MCP is being built.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
MCP_DIR="${PROJECT_ROOT}/Docs/Skills/Unreal/unreal-engine-mcp/Python"
UV_BIN="${UV_BIN:-/home/linux/.local/bin/uv}"

if [[ ! -x "${UV_BIN}" ]]; then
  UV_BIN="$(command -v uv || true)"
fi

if [[ -z "${UV_BIN}" || ! -x "${UV_BIN}" ]]; then
  echo "uv not found. Install uv in WSL or set UV_BIN." >&2
  exit 127
fi

cd "${MCP_DIR}"
export UV_LINK_MODE="${UV_LINK_MODE:-copy}"

if [[ -z "${UNREAL_HOST:-}" ]]; then
  UNREAL_HOST="$(ip route | awk '/^default / {print $3; exit}')"
  export UNREAL_HOST
fi

export UNREAL_PORT="${UNREAL_PORT:-55557}"
exec "${UV_BIN}" run unreal_mcp_server_advanced.py "$@"
