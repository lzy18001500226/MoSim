#!/usr/bin/env bash
# Materialize mutable Gazebo/launch assets from project src into build/ros1.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
WORKSPACE="${SUNRAY_WS:-}"

usage() {
  cat <<'EOF'
Usage: bash Scripts/sunray/prepare_local_ros1_runtime_overlay.sh --workspace <path>

Creates one generated runtime overlay below build/ros1/runtime_overlays from
the project-owned src/simulation/gazebo/sunray and
src/flight_stack/mavros/sunray_uav_control trees. It never reads References,
Results, or an old WSL runtime workspace as a source input.
EOF
}

die() {
  printf 'BLOCKER %s\n' "$*" >&2
  exit 2
}

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --workspace)
      [[ "$#" -ge 2 ]] || die "--workspace requires a value"
      WORKSPACE="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown argument: $1"
      ;;
  esac
done

[[ -n "${WORKSPACE}" ]] || die "--workspace is required"
PROJECT_ROOT="$(realpath "${PROJECT_ROOT}")"
OVERLAY_ROOT="${PROJECT_ROOT}/build/ros1/runtime_overlays"
if [[ "${WORKSPACE}" != /* ]]; then
  WORKSPACE="${PROJECT_ROOT}/${WORKSPACE}"
fi
WORKSPACE="$(realpath -m "${WORKSPACE}")"
case "${WORKSPACE}" in
  "${OVERLAY_ROOT}"/*) ;;
  *) die "runtime overlay must remain below ${OVERLAY_ROOT}: ${WORKSPACE}" ;;
esac

SOURCE_SIMULATOR="${PROJECT_ROOT}/src/simulation/gazebo/sunray"
SOURCE_CONTROL="${PROJECT_ROOT}/src/flight_stack/mavros/sunray_uav_control"
for path in "${SOURCE_SIMULATOR}" "${SOURCE_CONTROL}"; do
  [[ -d "${path}" ]] || die "project source directory missing: ${path}"
done

target_simulator="${WORKSPACE}/simulation/sunray_simulator"
target_control="${WORKSPACE}/General_Module/sunray_uav_control"
manifest="${WORKSPACE}/runtime_overlay_manifest.json"

if [[ -e "${WORKSPACE}" ]]; then
  [[ -f "${manifest}" ]] || die "existing runtime overlay is unmanaged: ${WORKSPACE}"
  [[ -d "${target_simulator}" && -d "${target_control}" ]] || die "existing runtime overlay is incomplete: ${WORKSPACE}"
  python3 - "${manifest}" "${PROJECT_ROOT}" "${SOURCE_SIMULATOR}" "${SOURCE_CONTROL}" <<'PY'
import json
import pathlib
import sys

manifest_path = pathlib.Path(sys.argv[1])
project_root = pathlib.Path(sys.argv[2]).resolve()
expected = [pathlib.Path(value).resolve() for value in sys.argv[3:]]
payload = json.loads(manifest_path.read_text(encoding="utf-8"))
if payload.get("schema") != "mosim.ros1_local_runtime_overlay.v1":
    raise SystemExit(f"unsupported runtime overlay manifest: {manifest_path}")
if pathlib.Path(payload.get("project_root", "")).resolve() != project_root:
    raise SystemExit(f"runtime overlay project root differs: {manifest_path}")
actual = [pathlib.Path(value).resolve() for value in payload.get("source_inputs", [])]
if actual != expected:
    raise SystemExit(f"runtime overlay source inputs differ: {manifest_path}")
PY
else
  mkdir -p "${WORKSPACE}/simulation" "${WORKSPACE}/General_Module"
  cp -a "${SOURCE_SIMULATOR}" "${target_simulator}"
  cp -a "${SOURCE_CONTROL}" "${target_control}"
  python3 - "${manifest}" "${PROJECT_ROOT}" "${WORKSPACE}" "${SOURCE_SIMULATOR}" "${SOURCE_CONTROL}" <<'PY'
import json
import pathlib
import sys
from datetime import datetime, timezone

output = pathlib.Path(sys.argv[1])
payload = {
    "schema": "mosim.ros1_local_runtime_overlay.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "project_root": str(pathlib.Path(sys.argv[2]).resolve()),
    "workspace": str(pathlib.Path(sys.argv[3]).resolve()),
    "source_input_root": "src",
    "source_inputs": [str(pathlib.Path(value).resolve()) for value in sys.argv[4:]],
    "generated_paths": [
        "simulation/sunray_simulator",
        "General_Module/sunray_uav_control",
    ],
}
output.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
PY
fi

printf 'LOCAL_ROS1_RUNTIME_OVERLAY=%s\n' "${WORKSPACE}"
printf 'LOCAL_ROS1_RUNTIME_OVERLAY_MANIFEST=%s\n' "${manifest}"
