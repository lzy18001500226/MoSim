#!/usr/bin/env bash
set -euo pipefail

# Stable wrapper for the configured `mosim-epic` server name.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/wsl.sh" "$@"
