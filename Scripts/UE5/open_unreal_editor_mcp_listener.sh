#!/usr/bin/env bash
set -euo pipefail

# Open the project-owned Unreal Editor and wait briefly for the editor-side
# UnrealMCP listener. This is for interactive editor automation, not the
# standalone rendered review window.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
PORT="${UNREAL_PORT:-55557}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-60}"
DRY_RUN="${DRY_RUN:-0}"

cd "${PROJECT_ROOT}"

if [[ "${DRY_RUN}" == "1" ]]; then
  python3 - <<PY
import json
payload = {
    "schema": "mosim.unreal_editor_mcp_listener_open_dryrun.v1",
    "project": "UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject",
    "port": int("${PORT}"),
    "timeout_seconds": float("${TIMEOUT_SECONDS}"),
    "claim": "dry-run only; Unreal Editor was not opened",
}
print(json.dumps(payload, indent=2))
PY
  exit 0
fi

Scripts/UE5/open_unreal_renderer.sh editor

deadline=$((SECONDS + ${TIMEOUT_SECONDS%.*}))
while (( SECONDS < deadline )); do
  if python3 Scripts/UE5/probe_unreal_mcp_listener.py \
      --port "${PORT}" \
      --timeout 1 \
      --wrapper-route-only \
      --no-process-diagnostics >/dev/null 2>&1; then
    python3 Scripts/UE5/probe_unreal_mcp_listener.py \
      --port "${PORT}" \
      --timeout 1 \
      --wrapper-route-only
    exit 0
  fi
  sleep 2
done

python3 Scripts/UE5/probe_unreal_mcp_listener.py --port "${PORT}" --timeout 1 || true
echo "Unreal Editor was opened or already running, but the MCP listener did not become reachable within ${TIMEOUT_SECONDS}s." >&2
exit 6
