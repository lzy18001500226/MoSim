#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/unreal/unreal_mcp_wsl_wrapper.sh" "$@"
