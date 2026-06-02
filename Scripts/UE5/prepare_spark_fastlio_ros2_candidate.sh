#!/usr/bin/env bash
set -euo pipefail

# Prepare and optionally build a ROS2 FAST-LIO2-family candidate for the
# Ubuntu 22.04 / ROS2 Humble MoSim mapping route. This script never installs
# apt packages and never writes outside the project tree.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
REPO_URL="${REPO_URL:-https://github.com/MIT-SPARK/spark-fast-lio.git}"
REPO_REF="${REPO_REF:-main}"
CANDIDATE_ROOT="${CANDIDATE_ROOT:-${PROJECT_ROOT}/Results/tmp/fastlio_ros2_candidates}"
CANDIDATE_DIR="${CANDIDATE_DIR:-${CANDIDATE_ROOT}/spark-fast-lio}"
PACKAGE_DIR="${PACKAGE_DIR:-${CANDIDATE_DIR}/spark_fast_lio}"
WORKSPACE="${WORKSPACE:-${PROJECT_ROOT}/Results/tmp/spark_fast_lio_ros2_ws}"
STATUS_JSON="${STATUS_JSON:-${PROJECT_ROOT}/Results/unreal_scene_mapping/SPARK_FASTLIO_ROS2_CANDIDATE.json}"
STATUS_MD="${STATUS_MD:-${PROJECT_ROOT}/Results/unreal_scene_mapping/SPARK_FASTLIO_ROS2_CANDIDATE.md}"
APT_DEB_DIR="${APT_DEB_DIR:-${PROJECT_ROOT}/Results/tmp/apt_debs}"
APT_OVERLAY_DIR="${APT_OVERLAY_DIR:-${PROJECT_ROOT}/Results/tmp/ros2_overlay_pcl_ros}"
AUTO_APT_OVERLAY="${AUTO_APT_OVERLAY:-1}"
BUILD="${BUILD:-0}"
UPDATE="${UPDATE:-1}"
CLEAN_BUILD="${CLEAN_BUILD:-0}"
DRY_RUN="${DRY_RUN:-0}"
OVERLAY_USED="${OVERLAY_USED:-0}"

cd "${PROJECT_ROOT}"

ROS2_DEPS=(
  rclcpp
  rclcpp_components
  geometry_msgs
  nav_msgs
  std_msgs
  sensor_msgs
  visualization_msgs
  tf2_ros
  tf2_eigen
  tf2_geometry_msgs
  tf2_sensor_msgs
  pcl_ros
  pcl_conversions
  ros2launch
)

json_bool() {
  case "$1" in
    1|true|TRUE|yes|YES|on|ON) printf "true" ;;
    *) printf "false" ;;
  esac
}

join_by_comma() {
  local IFS=","
  printf "%s" "$*"
}

apt_package_for_ros2_package() {
  case "$1" in
    pcl_ros) printf "ros-humble-pcl-ros" ;;
    pcl_conversions) printf "ros-humble-pcl-conversions" ;;
    tf2_eigen) printf "ros-humble-tf2-eigen" ;;
    tf2_geometry_msgs) printf "ros-humble-tf2-geometry-msgs" ;;
    tf2_sensor_msgs) printf "ros-humble-tf2-sensor-msgs" ;;
    *) return 1 ;;
  esac
}

activate_apt_overlay() {
  local prefix="${APT_OVERLAY_DIR}/opt/ros/humble"
  if [[ -d "${prefix}" ]]; then
    export AMENT_PREFIX_PATH="${prefix}:${AMENT_PREFIX_PATH:-}"
    export CMAKE_PREFIX_PATH="${prefix}:${CMAKE_PREFIX_PATH:-${AMENT_PREFIX_PATH:-}}"
    export LD_LIBRARY_PATH="${prefix}/lib:${LD_LIBRARY_PATH:-}"
    export PYTHONPATH="${prefix}/lib/python3.10/site-packages:${PYTHONPATH:-}"
    OVERLAY_USED="1"
    export OVERLAY_USED
  fi
}

find_missing_ros2_deps() {
  local missing=()
  local package_name
  for package_name in "${ROS2_DEPS[@]}"; do
    if ! ros2 pkg prefix "${package_name}" >/dev/null 2>&1; then
      missing+=("${package_name}")
    fi
  done
  join_by_comma "${missing[@]}"
}

prepare_apt_overlay_for_missing_deps() {
  local missing_joined="$1"
  local missing_packages=()
  local package_name apt_package
  IFS="," read -r -a missing_packages <<<"${missing_joined}"
  mkdir -p "${APT_DEB_DIR}" "${APT_OVERLAY_DIR}"
  for package_name in "${missing_packages[@]}"; do
    [[ -n "${package_name}" ]] || continue
    if apt_package="$(apt_package_for_ros2_package "${package_name}")"; then
      if ! compgen -G "${APT_DEB_DIR}/${apt_package}_*.deb" >/dev/null; then
        (cd "${APT_DEB_DIR}" && apt-get download "${apt_package}")
      fi
      dpkg-deb -x "${APT_DEB_DIR}/${apt_package}"_*.deb "${APT_OVERLAY_DIR}"
    fi
  done
  activate_apt_overlay
}

write_status() {
  local phase="$1"
  local result="$2"
  local missing_packages="$3"
  local note="${4:-}"
  export PHASE="${phase}"
  export RESULT="${result}"
  export MISSING_PACKAGES="${missing_packages}"
  export STATUS_NOTE="${note}"
  export PROJECT_ROOT ROS_SETUP REPO_URL REPO_REF CANDIDATE_DIR PACKAGE_DIR WORKSPACE STATUS_JSON STATUS_MD BUILD UPDATE CLEAN_BUILD DRY_RUN
  export APT_DEB_DIR APT_OVERLAY_DIR AUTO_APT_OVERLAY OVERLAY_USED
  python3 - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["PROJECT_ROOT"])
status_json = Path(os.environ["STATUS_JSON"])
status_md = Path(os.environ["STATUS_MD"])
missing = [item for item in os.environ.get("MISSING_PACKAGES", "").split(",") if item]
apt_map = {
    "pcl_ros": "ros-humble-pcl-ros",
    "pcl_conversions": "ros-humble-pcl-conversions",
    "tf2_eigen": "ros-humble-tf2-eigen",
    "tf2_geometry_msgs": "ros-humble-tf2-geometry-msgs",
    "tf2_sensor_msgs": "ros-humble-tf2-sensor-msgs",
}
manual_apt = [apt_map[item] for item in missing if item in apt_map]
payload = {
    "schema": "mosim.spark_fastlio_ros2_candidate.v1",
    "phase": os.environ["PHASE"],
    "result": os.environ["RESULT"],
    "repo_url": os.environ["REPO_URL"],
    "repo_ref": os.environ["REPO_REF"],
    "ros_setup": os.environ["ROS_SETUP"],
    "candidate_dir": str(Path(os.environ["CANDIDATE_DIR"]).relative_to(root)),
    "package_dir": str(Path(os.environ["PACKAGE_DIR"]).relative_to(root)),
    "workspace": str(Path(os.environ["WORKSPACE"]).relative_to(root)),
    "apt_deb_dir": str(Path(os.environ["APT_DEB_DIR"]).relative_to(root)),
    "apt_overlay_dir": str(Path(os.environ["APT_OVERLAY_DIR"]).relative_to(root)),
    "auto_apt_overlay": os.environ["AUTO_APT_OVERLAY"] in {"1", "true", "TRUE", "yes", "YES", "on", "ON"},
    "overlay_used": os.environ.get("OVERLAY_USED") in {"1", "true", "TRUE", "yes", "YES", "on", "ON"},
    "build_requested": os.environ["BUILD"] in {"1", "true", "TRUE", "yes", "YES", "on", "ON"},
    "clean_build": os.environ["CLEAN_BUILD"] in {"1", "true", "TRUE", "yes", "YES", "on", "ON"},
    "missing_ros2_packages": missing,
    "manual_apt_packages": manual_apt,
    "ready_to_build": not missing,
    "runtime_claimable": False,
    "note": os.environ.get("STATUS_NOTE", ""),
    "commands": {
        "dry_run": "DRY_RUN=1 Scripts/UE5/prepare_spark_fastlio_ros2_candidate.sh",
        "preflight": "Scripts/UE5/prepare_spark_fastlio_ros2_candidate.sh",
        "preflight_without_overlay": "AUTO_APT_OVERLAY=0 Scripts/UE5/prepare_spark_fastlio_ros2_candidate.sh",
        "build": "BUILD=1 Scripts/UE5/prepare_spark_fastlio_ros2_candidate.sh",
        "clean_build": "CLEAN_BUILD=1 BUILD=1 Scripts/UE5/prepare_spark_fastlio_ros2_candidate.sh",
        "source_overlay_after_download": (
            "export AMENT_PREFIX_PATH=Results/tmp/ros2_overlay_pcl_ros/opt/ros/humble:${AMENT_PREFIX_PATH}; "
            "export CMAKE_PREFIX_PATH=Results/tmp/ros2_overlay_pcl_ros/opt/ros/humble:${CMAKE_PREFIX_PATH:-${AMENT_PREFIX_PATH}}; "
            "export LD_LIBRARY_PATH=Results/tmp/ros2_overlay_pcl_ros/opt/ros/humble/lib:${LD_LIBRARY_PATH}"
        ),
        "launch_after_build": (
            "source Results/tmp/spark_fast_lio_ros2_ws/install/setup.bash && "
            "FASTLIO_ROS2_LAUNCH_CMD='ros2 launch spark_fast_lio mapping_mit_campus.launch.yaml "
            "start_rviz:=false scene_id:=mosim robot_name:=base_link "
            "base_frame:=base_link map_frame:=ue_world' "
            "START_FASTLIO=1 START_RVIZ=0 Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh factoryenvironmentcollect"
        ),
    },
    "claim_boundary": [
        "This prepares a ROS2 FAST-LIO2-family candidate only.",
        "It does not install apt packages into the system and does not store credentials.",
        "When AUTO_APT_OVERLAY=1, missing known ROS2 deb packages may be downloaded and extracted under Results/tmp only.",
        "runtime_claimable remains false until colcon build succeeds and live /cloud_registered plus odometry/path outputs are recorded.",
        "spark_fast_lio publishes odometry on relative topic odometry, so MoSim checks must account for /odometry or remap/namespace policy before claiming /Odometry.",
    ],
}
status_json.parent.mkdir(parents=True, exist_ok=True)
status_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
lines = [
    "# SPARK FAST-LIO ROS2 Candidate",
    "",
    f"- result: `{payload['result']}`",
    f"- phase: `{payload['phase']}`",
    f"- repo: `{payload['repo_url']}` @ `{payload['repo_ref']}`",
    f"- package_dir: `{payload['package_dir']}`",
    f"- workspace: `{payload['workspace']}`",
    f"- apt_overlay_dir: `{payload['apt_overlay_dir']}`",
    f"- overlay_used: `{str(payload['overlay_used']).lower()}`",
    f"- ready_to_build: `{str(payload['ready_to_build']).lower()}`",
    f"- runtime_claimable: `{str(payload['runtime_claimable']).lower()}`",
    f"- missing_ros2_packages: {', '.join(f'`{item}`' for item in missing) or 'none'}",
    f"- manual_apt_packages: {', '.join(f'`{item}`' for item in manual_apt) or 'none'}",
    "",
    "## Commands",
    "",
]
for name, command in payload["commands"].items():
    lines.append(f"- {name}: `{command}`")
lines.extend(["", "## Claim Boundary", ""])
for item in payload["claim_boundary"]:
    lines.append(f"- {item}")
if payload["note"]:
    lines.extend(["", "## Note", "", payload["note"]])
status_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps(payload, ensure_ascii=False, indent=2))
PY
}

if [[ "${DRY_RUN}" == "1" ]]; then
  write_status "dry_run" "not_started" "" "Dry-run only; no repository clone, dependency query, or build was executed."
  exit 0
fi

if [[ ! -f "${ROS_SETUP}" ]]; then
  write_status "preflight" "blocked_missing_ros_setup" "" "Missing ROS2 setup file: ${ROS_SETUP}"
  echo "Missing ROS2 setup file: ${ROS_SETUP}" >&2
  exit 4
fi

set +u
# shellcheck disable=SC1090
source "${ROS_SETUP}"
set -u
activate_apt_overlay

for command_name in git ros2 colcon python3; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    write_status "preflight" "blocked_missing_command" "" "Missing command: ${command_name}"
    echo "Missing ${command_name}. Source/install ROS2 Humble tooling first." >&2
    exit 4
  fi
done

mkdir -p "${CANDIDATE_ROOT}"
if [[ ! -d "${CANDIDATE_DIR}/.git" ]]; then
  git clone --depth 1 --branch "${REPO_REF}" "${REPO_URL}" "${CANDIDATE_DIR}"
elif [[ "${UPDATE}" == "1" ]]; then
  git -C "${CANDIDATE_DIR}" fetch --depth 1 origin "${REPO_REF}"
  git -C "${CANDIDATE_DIR}" reset --hard "origin/${REPO_REF}"
fi

if [[ ! -f "${PACKAGE_DIR}/package.xml" ]]; then
  write_status "preflight" "blocked_missing_package_xml" "" "Expected package.xml at ${PACKAGE_DIR}/package.xml"
  echo "Missing spark_fast_lio package.xml under ${PACKAGE_DIR}" >&2
  exit 5
fi

missing_joined="$(find_missing_ros2_deps)"
missing=()
if [[ -n "${missing_joined}" ]]; then
  IFS="," read -r -a missing <<<"${missing_joined}"
fi

if [[ "${#missing[@]}" -gt 0 && "${AUTO_APT_OVERLAY}" == "1" ]]; then
  prepare_apt_overlay_for_missing_deps "${missing_joined}"
  missing_joined="$(find_missing_ros2_deps)"
  missing=()
  if [[ -n "${missing_joined}" ]]; then
    IFS="," read -r -a missing <<<"${missing_joined}"
  fi
fi

if [[ "${#missing[@]}" -gt 0 ]]; then
  write_status "preflight" "degraded_missing_ros2_packages" "${missing_joined}" "Install the listed ROS2 packages manually, then rerun with BUILD=1."
  if [[ "${BUILD}" == "1" ]]; then
    echo "Missing ROS2 packages required for spark_fast_lio:" >&2
    printf '  %s\n' "${missing[@]}" >&2
    exit 6
  fi
  exit 0
fi

if [[ "${BUILD}" != "1" ]]; then
  write_status "preflight" "ready_to_build" "" "All ROS2 package dependencies are visible. Rerun with BUILD=1 to build the candidate."
  exit 0
fi

write_status "build" "building" "" "colcon build has started. If the process is interrupted, inspect Results/tmp/spark_fast_lio_ros2_ws/log/latest_build."

mkdir -p "${WORKSPACE}/src"
ln -sfn "${PACKAGE_DIR}" "${WORKSPACE}/src/spark_fast_lio"
if [[ "${CLEAN_BUILD}" == "1" ]]; then
  rm -rf \
    "${WORKSPACE}/build/spark_fast_lio" \
    "${WORKSPACE}/install/spark_fast_lio" \
    "${WORKSPACE}/log/latest_build/spark_fast_lio" \
    "${WORKSPACE}/log/latest/spark_fast_lio"
fi

colcon --log-base "${WORKSPACE}/log" build \
  --base-paths "${WORKSPACE}/src/spark_fast_lio" \
  --build-base "${WORKSPACE}/build" \
  --install-base "${WORKSPACE}/install" \
  --packages-select spark_fast_lio

write_status "build" "built" "" "colcon build completed. Runtime still needs live topic recording before FAST-LIO localization can be claimed."
