#!/usr/bin/env bash
set -euo pipefail

# Stable wrapper for the configured `unreal_engine` MCP server name.
# It now points to MoSim's project-specific Unreal MCP surface.  The previous
# Flopperam wrapper is kept as `unreal_mcp_legacy_flopperam_wsl_wrapper.sh` for
# rollback while the MoSim-native toolset is expanded.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/mosim_unreal_engine_mcp_wsl_wrapper.sh" "$@"
