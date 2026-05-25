#!/usr/bin/env bash
set -euo pipefail

# Stable wrapper for the configured `unreal_engine` MCP server name.
# It points to MoSim's project-specific Unreal MCP surface.  The previous
# Flopperam wrapper is kept in this project for rollback while the MoSim-native
# toolset is expanded.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/wsl.sh" "$@"
