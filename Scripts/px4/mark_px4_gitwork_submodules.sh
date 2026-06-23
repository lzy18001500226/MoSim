#!/usr/bin/env bash
# Add local .git metadata to tarball-fallback dependency folders in the
# temporary PX4 gitwork. This is only for PX4/Ninja submodule stamp files.
set -euo pipefail

PX4_GITWORK_DIR="${PX4_GITWORK_DIR:-/mnt/c/Users/HP/Desktop/MoSim/Results/tmp/px4_gitwork/PX4}"

paths=(
  "src/drivers/gps/devices"
  "src/lib/heatshrink/heatshrink"
  "src/modules/simulation/gz_plugins/optical_flow/PX4-OpticalFlow"
  "src/modules/simulation/gz_plugins/optical_flow/PX4-OpticalFlow/external/klt_feature_tracker"
)

cd "${PX4_GITWORK_DIR}"
for dep_path in "${paths[@]}"; do
  if [[ -d "${dep_path}" && ! -e "${dep_path}/.git" ]]; then
    git -C "${dep_path}" init >/dev/null
    git -C "${dep_path}" config user.email "mosim-local@example.invalid"
    git -C "${dep_path}" config user.name "MoSim Local Gitwork"
    if [[ -f "${dep_path}/CMakeLists.txt" ]]; then
      git -C "${dep_path}" update-index --add -- CMakeLists.txt 2>/dev/null || true
    fi
  fi
done

for dep_path in "${paths[@]}"; do
  if [[ -e "${dep_path}/.git" ]]; then
    printf '%s git\n' "${dep_path}"
  else
    printf '%s nogit\n' "${dep_path}"
  fi
done

build_dir="${PX4_GITWORK_DIR}/build/px4_sitl_default"
if [[ -d "${build_dir}" ]]; then
  for dep_path in "${paths[@]}"; do
    if [[ -e "${PX4_GITWORK_DIR}/${dep_path}/.git" ]]; then
      mkdir -p "${build_dir}/${dep_path}"
      rm -f "${build_dir}/${dep_path}/.git"
      ln -s "${PX4_GITWORK_DIR}/${dep_path}/.git" "${build_dir}/${dep_path}/.git"
    fi
  done
fi
