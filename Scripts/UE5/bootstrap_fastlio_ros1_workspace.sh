#!/usr/bin/env bash
set -euo pipefail

# Bootstrap a project-local generated Catkin workspace for FAST-LIO replay.
# This script does not install ROS packages. It only wires the local
# References/Lab/localization_slam/FAST_LIO package into Results/tmp and builds it when ROS1 and
# Catkin are already available.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
FAST_LIO_SRC="${FAST_LIO_SRC:-${PROJECT_ROOT}/References/Lab/localization_slam/FAST_LIO}"
CATKIN_WS="${CATKIN_WS:-${PROJECT_ROOT}/Results/tmp/fastlio_ros1_ws}"
DRY_RUN="${DRY_RUN:-0}"
BUILD="${BUILD:-1}"

cd "${PROJECT_ROOT}"

if [[ ! -f "${FAST_LIO_SRC}/package.xml" ]]; then
  echo "Missing FAST-LIO package.xml: ${FAST_LIO_SRC}/package.xml" >&2
  exit 3
fi

if [[ "${DRY_RUN}" == "1" ]]; then
  python3 - <<PY
import json
payload = {
    "schema": "mosim.fastlio_ros1_workspace_bootstrap_dryrun.v1",
    "catkin_ws": "${CATKIN_WS}",
    "fast_lio_src": "${FAST_LIO_SRC}",
    "build": "${BUILD}" == "1",
    "claim": "dry-run only; no workspace files were created and no build was run",
}
print(json.dumps(payload, indent=2))
PY
  exit 0
fi

if [[ -z "${ROS_DISTRO:-}" ]]; then
  echo "ROS environment is not sourced. Run: source /opt/ros/noetic/setup.bash" >&2
  exit 4
fi

for command_name in catkin_make rospack; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Missing ${command_name}. Source/install ROS1 Catkin before bootstrapping FAST-LIO." >&2
    exit 4
  fi
done

mkdir -p "${CATKIN_WS}/src"
ln -sfn "${FAST_LIO_SRC}" "${CATKIN_WS}/src/fast_lio"

if [[ "${BUILD}" == "1" ]]; then
  catkin_make -C "${CATKIN_WS}"
fi

set +u
source "${CATKIN_WS}/devel/setup.bash"
set -u

if ! rospack find fast_lio >/dev/null 2>&1; then
  echo "FAST-LIO package is still not visible after sourcing ${CATKIN_WS}/devel/setup.bash" >&2
  exit 5
fi

python3 Scripts/UE5/check_ros_mapping_runtime_env.py --write
