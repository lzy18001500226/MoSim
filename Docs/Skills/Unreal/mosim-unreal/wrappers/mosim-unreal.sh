#!/usr/bin/env bash
set -euo pipefail

# Project-local WSL wrapper for MoSim's live Unreal Editor MCP boundary.
# This wrapper does not launch Epic Launcher or download Fab assets.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/wsl.sh" "$@"
