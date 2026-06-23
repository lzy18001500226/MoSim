#!/usr/bin/env bash
# Shared WSL/Gazebo environment for MoSim runs.
# Keep Gazebo model lookup project-scoped by default; broad global lookup paths
# make missing-model resolution slow and can mask wrong assets.

if [[ -z "${PROJECT_ROOT:-}" ]]; then
  PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
fi

MOSIM_GAZEBO_USE_NVIDIA="${MOSIM_GAZEBO_USE_NVIDIA:-1}"
MOSIM_GAZEBO_INHERIT_RESOURCE_PATHS="${MOSIM_GAZEBO_INHERIT_RESOURCE_PATHS:-0}"
MOSIM_GAZEBO_SOFTWARE_RENDERING="${MOSIM_GAZEBO_SOFTWARE_RENDERING:-0}"

if [[ "${MOSIM_GAZEBO_USE_NVIDIA}" == "1" ]]; then
  export MESA_D3D12_DEFAULT_ADAPTER_NAME="${MESA_D3D12_DEFAULT_ADAPTER_NAME:-NVIDIA}"
  export __GLX_VENDOR_LIBRARY_NAME="${__GLX_VENDOR_LIBRARY_NAME:-mesa}"
fi

if [[ "${MOSIM_GAZEBO_SOFTWARE_RENDERING}" == "1" ]]; then
  export LIBGL_ALWAYS_SOFTWARE=1
else
  unset LIBGL_ALWAYS_SOFTWARE
fi

mosim_gazebo_join_paths() {
  python3 - "$@" <<'PY'
import os
import sys

seen = set()
items = []
for raw in sys.argv[1:]:
    for item in str(raw).split(":"):
        item = item.strip()
        if not item:
            continue
        norm = os.path.normpath(item)
        if norm not in seen:
            seen.add(norm)
            items.append(item)
print(":".join(items))
PY
}

mosim_gazebo_expand_project_paths() {
  python3 - "${PROJECT_ROOT}" "$@" <<'PY'
import os
import sys

root = sys.argv[1]
items = []
for raw in sys.argv[2:]:
    for item in str(raw).split(":"):
        item = item.strip()
        if not item:
            continue
        if not item.startswith("/"):
            item = os.path.join(root, item.lstrip("/"))
        items.append(item)
print(":".join(items))
PY
}

mosim_gazebo_resource_paths_default() {
  mosim_gazebo_expand_project_paths \
    "Config/gazebo/models"
}

mosim_gazebo_apply_resource_paths() {
  local explicit_paths="${1:-}"
  local base_paths
  if [[ -n "${explicit_paths}" ]]; then
    base_paths="$(mosim_gazebo_expand_project_paths "${explicit_paths}")"
  else
    base_paths="$(mosim_gazebo_resource_paths_default)"
  fi

  if [[ "${MOSIM_GAZEBO_INHERIT_RESOURCE_PATHS}" == "1" ]]; then
    base_paths="$(mosim_gazebo_join_paths "${base_paths}" "${GZ_SIM_RESOURCE_PATH:-}" "${IGN_GAZEBO_RESOURCE_PATH:-}")"
  else
    base_paths="$(mosim_gazebo_join_paths "${base_paths}")"
  fi

  export GZ_SIM_RESOURCE_PATH="${base_paths}"
  export IGN_GAZEBO_RESOURCE_PATH="${base_paths}"
}

if [[ "${MOSIM_GAZEBO_AUTO_APPLY_RESOURCE_PATHS:-1}" == "1" ]]; then
  mosim_gazebo_apply_resource_paths "${MOSIM_GAZEBO_RESOURCE_PATHS:-}"
fi
