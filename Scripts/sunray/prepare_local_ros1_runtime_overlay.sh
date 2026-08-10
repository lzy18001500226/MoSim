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
src/flight_stack/mavros/sunray_uav_control trees. It also creates a minimal
px4 package wrapper that exposes the validated source-local PX4 SITL build to
ROS1 node resolution. It never reads References, Results, or an old WSL
runtime workspace as a source input.
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
PX4_SOURCE_DIR="${SUNRAY_PX4_DIR:-${PROJECT_ROOT}/src/flight_stack/px4/PX4-Autopilot}"
PX4_BUILD_DIR="${PX4_BUILD_DIR:-${PROJECT_ROOT}/build/px4/px4_sitl_default}"
for path in "${SOURCE_SIMULATOR}" "${SOURCE_CONTROL}" "${PX4_SOURCE_DIR}"; do
  [[ -d "${path}" ]] || die "project source directory missing: ${path}"
done
[[ -f "${PX4_SOURCE_DIR}/package.xml" ]] || die "PX4 package manifest missing: ${PX4_SOURCE_DIR}/package.xml"
[[ -x "${PX4_BUILD_DIR}/bin/px4" ]] || die "PX4 SITL executable missing: ${PX4_BUILD_DIR}/bin/px4"
[[ -d "${PX4_BUILD_DIR}/etc" ]] || die "PX4 SITL runtime configuration missing: ${PX4_BUILD_DIR}/etc"

target_simulator="${WORKSPACE}/simulation/sunray_simulator"
target_control="${WORKSPACE}/General_Module/sunray_uav_control"
target_px4="${WORKSPACE}/px4"
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
        "px4",
    ],
}
output.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
PY
fi

prepare_px4_package_overlay() {
  local px4_node="${target_px4}/px4"
  local px4_build_link="${target_px4}/build/px4_sitl_default"
  local resolved_binary
  local resolved_build

  resolved_binary="$(realpath "${PX4_BUILD_DIR}/bin/px4")"
  resolved_build="$(realpath "${PX4_BUILD_DIR}")"

  if [[ -e "${target_px4}" ]]; then
    [[ -d "${target_px4}" && ! -L "${target_px4}" ]] \
      || die "existing PX4 runtime package overlay is not a directory: ${target_px4}"
    [[ -f "${target_px4}/package.xml" && -L "${px4_node}" && -L "${px4_build_link}" ]] \
      || die "existing PX4 runtime package overlay is incomplete: ${target_px4}"
    [[ "$(realpath "${px4_node}")" == "${resolved_binary}" ]] \
      || die "existing PX4 runtime package binary differs from PX4_BUILD_DIR: ${target_px4}"
    [[ "$(realpath "${px4_build_link}")" == "${resolved_build}" ]] \
      || die "existing PX4 runtime package build differs from PX4_BUILD_DIR: ${target_px4}"
    return
  fi

  local temporary_px4="${WORKSPACE}/.px4_runtime_overlay_$$"
  mkdir -p "${temporary_px4}/build"
  cp "${PX4_SOURCE_DIR}/package.xml" "${temporary_px4}/package.xml"
  ln -s "${resolved_build}" "${temporary_px4}/build/px4_sitl_default"
  ln -s "${resolved_binary}" "${temporary_px4}/px4"
  mv "${temporary_px4}" "${target_px4}"
}

prepare_px4_package_overlay

python3 - "${manifest}" "${target_px4}" "${PX4_SOURCE_DIR}" "${PX4_BUILD_DIR}" <<'PY'
import json
import pathlib
import sys

manifest_path = pathlib.Path(sys.argv[1])
payload = json.loads(manifest_path.read_text(encoding="utf-8"))
generated_paths = payload.setdefault("generated_paths", [])
if "px4" not in generated_paths:
    generated_paths.append("px4")
payload["px4_ros1_package_overlay"] = {
    "package": str(pathlib.Path(sys.argv[2]).resolve()),
    "px4_source": str(pathlib.Path(sys.argv[3]).resolve()),
    "px4_build": str(pathlib.Path(sys.argv[4]).resolve()),
    "binary": str((pathlib.Path(sys.argv[4]) / "bin" / "px4").resolve()),
}
manifest_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
PY

printf 'LOCAL_ROS1_RUNTIME_OVERLAY=%s\n' "${WORKSPACE}"
printf 'LOCAL_ROS1_RUNTIME_OVERLAY_MANIFEST=%s\n' "${manifest}"
printf 'PX4_ROS1_OVERLAY_PKG=%s\n' "${target_px4}"
