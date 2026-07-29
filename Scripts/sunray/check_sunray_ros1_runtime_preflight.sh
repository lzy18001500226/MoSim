#!/usr/bin/env bash
# Verify the current MoSim Sunray ROS1 runtime lane before launching live runs.

set -u

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
source "${PROJECT_ROOT}/Scripts/sunray/resolve_local_ros1_runtime.sh"
FASTLIO_SRC="${FASTLIO_SRC:-${PROJECT_ROOT}/src/perception/fast_lio}"
LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS:-${LOCAL_ROS1_WS}}"
LIVOX_PLUGIN_SO="${LIVOX_PLUGIN_WS}/devel/lib/liblivox_laser_simulation.so"
LIVOX_PLUGIN_SRC="${LIVOX_PLUGIN_SRC:-${PROJECT_ROOT}/src/simulation/gazebo/plugins/sunray/livox_laser_simulation}"
BUILD_LIVOX=false

for arg in "$@"; do
  case "${arg}" in
    --build-livox)
      BUILD_LIVOX=true
      ;;
    -h|--help)
      cat <<'EOF'
Usage: bash Scripts/sunray/check_sunray_ros1_runtime_preflight.sh [--build-livox]

Checks Ubuntu-20.04, ROS1 Noetic, Gazebo Classic, Sunray/PX4 paths, local
FAST-LIO source, and the project-local Livox Gazebo Classic plugin overlay.
EOF
      exit 0
      ;;
    *)
      echo "BLOCKER unknown argument: ${arg}" >&2
      exit 2
      ;;
  esac
done

STATUS=0

pass() {
  echo "PASS $*"
}

warn() {
  echo "WARN $*" >&2
}

blocker() {
  echo "BLOCKER $*" >&2
  STATUS=1
}

check_file() {
  local path="$1"
  local label="$2"
  if [[ -f "${path}" ]]; then
    pass "${label}: ${path}"
  else
    blocker "${label} missing: ${path}"
  fi
}

check_dir() {
  local path="$1"
  local label="$2"
  if [[ -d "${path}" ]]; then
    pass "${label}: ${path}"
  else
    blocker "${label} missing: ${path}"
  fi
}

check_command() {
  local cmd="$1"
  local label="$2"
  if command -v "${cmd}" >/dev/null 2>&1; then
    pass "${label}: $(command -v "${cmd}")"
  else
    blocker "${label} command missing: ${cmd}"
  fi
}

if command -v lsb_release >/dev/null 2>&1; then
  UBUNTU_RELEASE="$(lsb_release -rs 2>/dev/null || true)"
else
  UBUNTU_RELEASE=""
fi

if [[ "${UBUNTU_RELEASE}" == "20.04" ]]; then
  pass "Ubuntu release: ${UBUNTU_RELEASE}"
else
  blocker "wrong Ubuntu release '${UBUNTU_RELEASE:-unknown}'. Current P0 must run in Ubuntu-20.04. From Windows use: wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/check_sunray_ros1_runtime_preflight.sh'"
fi

if [[ -n "${WSL_DISTRO_NAME:-}" && "${WSL_DISTRO_NAME}" != "Ubuntu-20.04" ]]; then
  blocker "wrong WSL distro '${WSL_DISTRO_NAME}'. Do not use bare default wsl for Sunray ROS1 runs."
elif [[ -n "${WSL_DISTRO_NAME:-}" ]]; then
  pass "WSL distro: ${WSL_DISTRO_NAME}"
else
  warn "WSL_DISTRO_NAME is not set; verify this shell was entered with wsl -d Ubuntu-20.04."
fi

check_file "/opt/ros/noetic/setup.bash" "ROS Noetic setup"
check_file "/usr/share/gazebo/setup.sh" "Gazebo Classic setup"
check_command "gzserver" "Gazebo Classic server"

if command -v gzserver >/dev/null 2>&1; then
  GZ_VERSION="$(gzserver --version 2>&1 | head -n 1 || true)"
  if echo "${GZ_VERSION}" | grep -qi "Gazebo"; then
    pass "Gazebo Classic version: ${GZ_VERSION}"
  else
    blocker "gzserver did not report Gazebo Classic version: ${GZ_VERSION}"
  fi
fi

if [[ -f /opt/ros/noetic/setup.bash ]]; then
  set +u
  # shellcheck disable=SC1091
  source /opt/ros/noetic/setup.bash
  set -u
  if command -v rosversion >/dev/null 2>&1; then
    ROS_DISTRO_CHECK="$(rosversion -d 2>/dev/null || true)"
    if [[ "${ROS_DISTRO_CHECK}" == "noetic" ]]; then
      pass "ROS distro: ${ROS_DISTRO_CHECK}"
    else
      blocker "ROS distro is '${ROS_DISTRO_CHECK:-unknown}', expected noetic."
    fi
  else
    blocker "rosversion command missing after sourcing Noetic."
  fi
fi

check_dir "${PROJECT_ROOT}" "MoSim project root"
check_dir "${PROJECT_ROOT}/src/simulation/gazebo/sunray" "project Sunray simulator source"
check_dir "${PROJECT_ROOT}/src/flight_stack/mavros/sunray_uav_control" "project Sunray control source"
check_dir "${FASTLIO_SRC}" "project FAST-LIO source"
check_file "${PROJECT_ROOT}/Config/gazebo/models/gps/gps.sdf" "project-local PX4 GPS model"
check_dir "${LOCAL_ROS1_WS}" "local ROS1 build workspace"
check_file "${LOCAL_ROS1_WS}/devel/setup.bash" "local ROS1 devel setup"
check_file "${SUNRAY_PX4_DIR}/Tools/simulation/gazebo-classic/setup_gazebo.bash" "PX4 Gazebo Classic setup"
check_dir "${PX4_BUILD_DIR}" "PX4 SITL build"

if [[ -d "${LIVOX_PLUGIN_SRC}" ]]; then
  pass "repo-local Livox plugin source: ${LIVOX_PLUGIN_SRC}"
else
  blocker "repo-local Livox plugin source missing: ${LIVOX_PLUGIN_SRC}"
fi

if [[ -f "${LIVOX_PLUGIN_SO}" ]]; then
  pass "project-local Livox plugin: ${LIVOX_PLUGIN_SO}"
elif [[ "${BUILD_LIVOX}" == "true" ]]; then
  if [[ -f "${PROJECT_ROOT}/Scripts/sunray/prepare_local_ros1_workspace.sh" ]]; then
    echo "INFO building the source-local Livox plugin profile..."
    PROJECT_ROOT="${PROJECT_ROOT}" \
      bash "${PROJECT_ROOT}/Scripts/sunray/prepare_local_ros1_workspace.sh" \
        --profile foundation \
        --workspace "${LOCAL_ROS1_WS#${PROJECT_ROOT}/}" \
        --build \
        --verify
    if [[ -f "${LIVOX_PLUGIN_SO}" ]]; then
      pass "source-local Livox plugin built: ${LIVOX_PLUGIN_SO}"
    else
      blocker "Livox plugin build finished without expected library: ${LIVOX_PLUGIN_SO}"
    fi
  else
    blocker "local ROS1 workspace build script missing: ${PROJECT_ROOT}/Scripts/sunray/prepare_local_ros1_workspace.sh"
  fi
else
  blocker "source-local Livox plugin missing: ${LIVOX_PLUGIN_SO}. Build explicitly with: PROJECT_ROOT=${PROJECT_ROOT} bash ${PROJECT_ROOT}/Scripts/sunray/check_sunray_ros1_runtime_preflight.sh --build-livox"
fi

if [[ "${STATUS}" -eq 0 ]]; then
  echo "SUNRAY_ROS1_PREFLIGHT=PASS"
else
  echo "SUNRAY_ROS1_PREFLIGHT=BLOCKER" >&2
fi

exit "${STATUS}"
