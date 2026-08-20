#!/usr/bin/env bash
# Headless Goal4 Diff-Planner single-UAV 1-2-3 interactive-goal gate.
#
# This wrapper keeps the runner and the standalone goal-chain probe in one WSL
# process so bash status variables such as $! and $? are not mangled by Windows
# command quoting. It is intended for metrics/evidence runs, not RViz review.

set -uo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RUN_ID="${RUN_ID:-diff_single_auto123_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"

source "${PROJECT_ROOT}/Scripts/sunray/resolve_local_ros1_runtime.sh"
GOAL4_DIFF_PLANNER_WS="${GOAL4_DIFF_PLANNER_WS:-${PROJECT_ROOT}/build/ros1/diff_planner_ws_c99}"
# FAST-LIO is built in its own generated workspace.  The source-local
# controller workspace already owns perception/fast_lio and
# perception/livox_ros_driver_compat, so putting the legacy top-level aliases
# there creates duplicate Catkin package names during rosmsg lookup.
FASTLIO_WS="${DIFF_FASTLIO_WS:-${PROJECT_ROOT}/build/ros1/fastlio_c99_ws}"
FASTLIO_SRC="${FASTLIO_SRC:-${PROJECT_ROOT}/src/perception/fast_lio}"
LIVOX_COMPAT_SRC="${LIVOX_COMPAT_SRC:-${PROJECT_ROOT}/src/perception/livox_ros_driver_compat}"
PX4CTRL_CORE_PROFILE="${PX4CTRL_CORE_PROFILE:-graphical_c99}"
PX4CTRL_EXPECTED_BUILD_BACKEND="${PX4CTRL_EXPECTED_BUILD_BACKEND:-graphical_px4ctrl_c99}"
PX4CTRL_HOVER_PERCENTAGE="${PX4CTRL_HOVER_PERCENTAGE:-0.456}"
FACTORY_WORLD_MODE="${FACTORY_WORLD_MODE:-}"
WORLD_FILE="${WORLD_FILE:-}"
FACTORY_MODEL_PATH="${FACTORY_MODEL_PATH:-}"
SUNRAY_GAZEBO_LAUNCH_FILE="${SUNRAY_GAZEBO_LAUNCH_FILE:-}"
SUNRAY_UAV_INIT_X="${SUNRAY_UAV_INIT_X:-}"
SUNRAY_UAV_INIT_Y="${SUNRAY_UAV_INIT_Y:-}"
SUNRAY_UAV_INIT_Z="${SUNRAY_UAV_INIT_Z:-}"
SUNRAY_UAV_INIT_YAW="${SUNRAY_UAV_INIT_YAW:-}"
PX4CTRL_EKF2_EV_CTRL_OVERRIDE="${PX4CTRL_EKF2_EV_CTRL_OVERRIDE:-15}"
PX4CTRL_EKF2_HGT_REF_OVERRIDE="${PX4CTRL_EKF2_HGT_REF_OVERRIDE:-3}"
PX4CTRL_BOOT_PARAM_OVERRIDES="${PX4CTRL_BOOT_PARAM_OVERRIDES:-EKF2_GPS_CTRL=0,EKF2_BARO_CTRL=0,EKF2_RNG_CTRL=0,EKF2_OF_CTRL=0,EKF2_EV_CTRL=15,EKF2_HGT_REF=3,EKF2_EV_DELAY=0,EKF2_EV_NOISE_MD=1,EKF2_EVP_NOISE=0.03,EKF2_EVA_NOISE=0.03}"
# Keep the accepted source-local FAST-LIO baseline resolution.  These values
# are localization inputs, not a planner-speed tuning knob.
FASTLIO_FILTER_SIZE_SURF="${FASTLIO_FILTER_SIZE_SURF:-0.02}"
FASTLIO_FILTER_SIZE_MAP="${FASTLIO_FILTER_SIZE_MAP:-0.02}"

if [[ "${PX4CTRL_CORE_PROFILE}" != "graphical_c99" ]]; then
  echo "This Diff C99 gate requires PX4CTRL_CORE_PROFILE=graphical_c99." >&2
  exit 2
fi

GOALS="${GOALS:-1.0,0.0,1.0;2.0,0.0,1.0;3.0,0.5,1.0}"
# The interactive probe and the outer mission manifest must describe the same
# first fixed target. Keep the first GOALS entry authoritative for this gate.
FIRST_GOAL="${GOALS%%;*}"
IFS=',' read -r GOAL_TARGET_X GOAL_TARGET_Y GOAL_TARGET_Z <<< "${FIRST_GOAL}"
if [[ -z "${GOAL_TARGET_X}" || -z "${GOAL_TARGET_Y}" || -z "${GOAL_TARGET_Z}" ]]; then
  echo "Invalid first Diff goal '${FIRST_GOAL}'; expected x,y,z." >&2
  exit 2
fi
TARGET_X="${TARGET_X:-${GOAL_TARGET_X}}"
TARGET_Y="${TARGET_Y:-${GOAL_TARGET_Y}}"
TARGET_Z="${TARGET_Z:-${GOAL_TARGET_Z}}"
python3 - "${TARGET_X}" "${TARGET_Y}" "${TARGET_Z}" "${GOAL_TARGET_X}" "${GOAL_TARGET_Y}" "${GOAL_TARGET_Z}" <<'PY'
import sys

target = tuple(float(value) for value in sys.argv[1:4])
goal = tuple(float(value) for value in sys.argv[4:7])
if any(abs(a - b) > 1e-9 for a, b in zip(target, goal)):
    raise SystemExit(
        "TARGET_X/Y/Z must match the first GOALS entry: "
        f"target={target}, first_goal={goal}"
    )
PY
export TARGET_X TARGET_Y TARGET_Z
GOAL_COUNT="${DIFF_INTERACTIVE_AUTO_PASS_GOAL_COUNT:-$(printf '%s\n' "${GOALS}" | awk -F';' '{count=0; for (i=1; i<=NF; i++) if ($i != "") count++; print count}')}"
TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S:-320}"
DIFF_INTERACTIVE_GOAL_TIMEOUT_S="${DIFF_INTERACTIVE_GOAL_TIMEOUT_S:-120}"
DIFF_INTERACTIVE_REVIEW_HOLD_S="${DIFF_INTERACTIVE_REVIEW_HOLD_S:-$((GOAL_COUNT * DIFF_INTERACTIVE_GOAL_TIMEOUT_S + 180))}"
DIFF_INTERACTIVE_FINAL_HOVER_HOLD_S="${DIFF_INTERACTIVE_FINAL_HOVER_HOLD_S:-5.0}"
DIFF_INTERACTIVE_TARGET_HOLD_S="${DIFF_INTERACTIVE_TARGET_HOLD_S:-5.0}"
# Feed the intended absolute hold setpoint as soon as px4ctrl leaves
# AUTO_TAKEOFF. Without this, its first AUTO_HOVER cycle captures the
# transient measured height instead of the Factory gate's 1 m target.
DIFF_PUBLISH_HOVER_DURING_TAKEOFF="${DIFF_PUBLISH_HOVER_DURING_TAKEOFF:-true}"
DIFF_PUBLISH_HOVER_DURING_TAKEOFF_DELAY_S="${DIFF_PUBLISH_HOVER_DURING_TAKEOFF_DELAY_S:-0.0}"
# A clean source-local FAST-LIO workspace may need more than the historical
# 120 s probe window for its first Catkin build.  This waits only for the
# already-running runtime to become ready; it does not alter planner behavior.
DIFF_INTERACTIVE_READY_TIMEOUT_S="${DIFF_INTERACTIVE_READY_TIMEOUT_S:-300}"
# The outer goal probe starts while Gazebo, FAST-LIO and the mission adapter
# initialize. Keep this bounded wait explicit so a cold source-local run cannot
# reject a target before the mission node has announced readiness.
DIFF_INTERACTIVE_PRE_GOAL_STABLE_TIMEOUT_S="${DIFF_INTERACTIVE_PRE_GOAL_STABLE_TIMEOUT_S:-540}"

mkdir -p "${RESULT_DIR}"
date --iso-8601=seconds > "${RESULT_DIR}/auto123_gate_start.txt"

prepare_source_local_fastlio_workspace() {
  local local_src="${LOCAL_ROS1_WS}/src"
  local catkin_toplevel="/opt/ros/noetic/share/catkin/cmake/toplevel.cmake"
  local catkin_link="${FASTLIO_WS}/src/CMakeLists.txt"
  local legacy_link

  [[ -f "${FASTLIO_SRC}/package.xml" ]] || {
    echo "Source-local FAST-LIO package is missing: ${FASTLIO_SRC}" >&2
    return 2
  }
  [[ -f "${LIVOX_COMPAT_SRC}/package.xml" ]] || {
    echo "Source-local Livox compatibility package is missing: ${LIVOX_COMPAT_SRC}" >&2
    return 2
  }
  [[ -f "${catkin_toplevel}" ]] || {
    echo "ROS Noetic Catkin toplevel is missing: ${catkin_toplevel}" >&2
    return 2
  }

  {
    echo "LOCAL_ROS1_WS=${LOCAL_ROS1_WS}"
    echo "FASTLIO_WS=${FASTLIO_WS}"
    echo "FASTLIO_SRC=${FASTLIO_SRC}"
    echo "LIVOX_COMPAT_SRC=${LIVOX_COMPAT_SRC}"
    # These aliases are a known generated-workspace residue from the old
    # reference layout.  The source-local manifest owns only the nested
    # perception paths, so remove exactly these generated links before ROS
    # package discovery.
    for legacy_link in FAST_LIO livox_ros_driver_compat; do
      local legacy_path="${local_src}/${legacy_link}"
      if [[ -L "${legacy_path}" ]]; then
        echo "removed_stale_generated_link=${legacy_path}->$(readlink -f "${legacy_path}")"
        rm -f "${legacy_path}"
      elif [[ -e "${legacy_path}" ]]; then
        echo "unexpected_nonlink=${legacy_path}"
        return 2
      else
        echo "no_stale_generated_link=${legacy_path}"
      fi
    done

    mkdir -p "${FASTLIO_WS}/src"
    if [[ -L "${catkin_link}" ]]; then
      if [[ "$(readlink -f "${catkin_link}")" != "$(readlink -f "${catkin_toplevel}")" ]]; then
        echo "unexpected_fastlio_catkin_link=${catkin_link}->$(readlink -f "${catkin_link}")"
        return 2
      fi
      echo "reused_fastlio_catkin_link=${catkin_link}"
    elif [[ -e "${catkin_link}" ]]; then
      echo "unexpected_fastlio_catkin_file=${catkin_link}"
      return 2
    else
      ln -s "${catkin_toplevel}" "${catkin_link}"
      echo "created_fastlio_catkin_link=${catkin_link}"
    fi
  } > "${RESULT_DIR}/fastlio_workspace_source_guard.txt"
}

prepare_source_local_fastlio_workspace || exit $?

if [[ ! -f "${GOAL4_DIFF_PLANNER_WS}/devel/setup.bash" ]]; then
  echo "Source-local Diff workspace is missing: ${GOAL4_DIFF_PLANNER_WS}/devel/setup.bash" >&2
  exit 2
fi

bash "${PROJECT_ROOT}/Scripts/sunray/prepare_local_ros1_runtime_overlay.sh" \
  --workspace "${SUNRAY_WS}" \
  > "${RESULT_DIR}/local_runtime_overlay.log" 2>&1

if [[ -L "${SUNRAY_WS}/devel" ]]; then
  [[ "$(readlink -f "${SUNRAY_WS}/devel")" == "$(readlink -f "${LOCAL_ROS1_WS}/devel")" ]] || {
    echo "Runtime overlay devel link targets another workspace: ${SUNRAY_WS}/devel" >&2
    exit 2
  }
elif [[ ! -e "${SUNRAY_WS}/devel" ]]; then
  ln -s "${LOCAL_ROS1_WS}/devel" "${SUNRAY_WS}/devel"
else
  echo "Runtime overlay devel path is not a generated link: ${SUNRAY_WS}/devel" >&2
  exit 2
fi

export GOAL4_DIFF_PLANNER_WS
export PX4CTRL_CORE_PROFILE
export PX4CTRL_EXPECTED_BUILD_BACKEND
export PX4CTRL_HOVER_PERCENTAGE
export PX4CTRL_EKF2_EV_CTRL_OVERRIDE
export PX4CTRL_EKF2_HGT_REF_OVERRIDE
export PX4CTRL_BOOT_PARAM_OVERRIDES
export FASTLIO_FILTER_SIZE_SURF
export FASTLIO_FILTER_SIZE_MAP
export FASTLIO_WS
export FASTLIO_SRC
export LIVOX_COMPAT_SRC
export MAVROS_PLUGIN_CONFIG_SOURCE="${PROJECT_ROOT}/Config/gazebo/mavros/px4_pluginlists.yaml"
export SUNRAY_GPS_SENSOR_MODE=removed
# Keep the validated C99 runtime localization path: external fusion supplies
# the PX4 local state while FAST-LIO remains the planner's point-cloud source.
export PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=false
export PX4CTRL_START_EXTERNAL_FUSION=true
export PX4CTRL_ODOM_SOURCE=mavros_local
export PX4CTRL_ODOM_TOPIC=/uav1/mavros/local_position/odom
export FASTLIO_ALIGNMENT_Z_SOURCE=truth
export FASTLIO_ALIGNMENT_REFERENCE=config
export FASTLIO_ALIGNMENT_REQUIRED=true

cat > "${RESULT_DIR}/auto123_gate_command.env" <<EOF
RUN_ID=${RUN_ID}
RESULT_DIR=${RESULT_DIR}
GOALS=${GOALS}
TARGET_X=${TARGET_X}
TARGET_Y=${TARGET_Y}
TARGET_Z=${TARGET_Z}
TOTAL_TIMEOUT_S=${TOTAL_TIMEOUT_S}
DIFF_INTERACTIVE_REVIEW_HOLD_S=${DIFF_INTERACTIVE_REVIEW_HOLD_S}
DIFF_INTERACTIVE_FINAL_HOVER_HOLD_S=${DIFF_INTERACTIVE_FINAL_HOVER_HOLD_S}
DIFF_INTERACTIVE_TARGET_HOLD_S=${DIFF_INTERACTIVE_TARGET_HOLD_S}
DIFF_PUBLISH_HOVER_DURING_TAKEOFF=${DIFF_PUBLISH_HOVER_DURING_TAKEOFF}
DIFF_PUBLISH_HOVER_DURING_TAKEOFF_DELAY_S=${DIFF_PUBLISH_HOVER_DURING_TAKEOFF_DELAY_S}
DIFF_INTERACTIVE_READY_TIMEOUT_S=${DIFF_INTERACTIVE_READY_TIMEOUT_S}
DIFF_INTERACTIVE_PRE_GOAL_STABLE_TIMEOUT_S=${DIFF_INTERACTIVE_PRE_GOAL_STABLE_TIMEOUT_S}
DIFF_INTERACTIVE_AUTO_PASS_GOAL_COUNT=${GOAL_COUNT}
SUNRAY_WS=${SUNRAY_WS}
LOCAL_ROS1_WS=${LOCAL_ROS1_WS}
GOAL4_DIFF_PLANNER_WS=${GOAL4_DIFF_PLANNER_WS}
PX4CTRL_CORE_PROFILE=${PX4CTRL_CORE_PROFILE}
PX4CTRL_EXPECTED_BUILD_BACKEND=${PX4CTRL_EXPECTED_BUILD_BACKEND}
PX4CTRL_HOVER_PERCENTAGE=${PX4CTRL_HOVER_PERCENTAGE}
FACTORY_WORLD_MODE=${FACTORY_WORLD_MODE}
WORLD_FILE=${WORLD_FILE}
FACTORY_MODEL_PATH=${FACTORY_MODEL_PATH}
SUNRAY_GAZEBO_LAUNCH_FILE=${SUNRAY_GAZEBO_LAUNCH_FILE}
SUNRAY_UAV_INIT_X=${SUNRAY_UAV_INIT_X}
SUNRAY_UAV_INIT_Y=${SUNRAY_UAV_INIT_Y}
SUNRAY_UAV_INIT_Z=${SUNRAY_UAV_INIT_Z}
SUNRAY_UAV_INIT_YAW=${SUNRAY_UAV_INIT_YAW}
PX4CTRL_EKF2_EV_CTRL_OVERRIDE=${PX4CTRL_EKF2_EV_CTRL_OVERRIDE}
PX4CTRL_EKF2_HGT_REF_OVERRIDE=${PX4CTRL_EKF2_HGT_REF_OVERRIDE}
PX4CTRL_BOOT_PARAM_OVERRIDES=${PX4CTRL_BOOT_PARAM_OVERRIDES}
FASTLIO_FILTER_SIZE_SURF=${FASTLIO_FILTER_SIZE_SURF}
FASTLIO_FILTER_SIZE_MAP=${FASTLIO_FILTER_SIZE_MAP}
FASTLIO_WS=${FASTLIO_WS}
FASTLIO_SRC=${FASTLIO_SRC}
LIVOX_COMPAT_SRC=${LIVOX_COMPAT_SRC}
MAVROS_PLUGIN_CONFIG_SOURCE=${MAVROS_PLUGIN_CONFIG_SOURCE}
DIFF_CMD_INVALID_Z_POLICY=clamp
DIFF_CMD_MIN_Z=0.95
DIFF_CMD_MAX_Z=1.15
EGO_VIRTUAL_CEIL_HEIGHT=1.15
EGO_VISUALIZATION_TRUNCATE_HEIGHT=1.25
EOF

# Publish the first goal during the takeoff/hold phase. The C99 backend
# needs the bounded absolute-height hold before the planner takes over;
# delaying it leaves the auto-takeoff controller above the 1 m gate.
(
  cd "${PROJECT_ROOT}" || exit 97
  RUN_ID="${RUN_ID}" \
  RESULT_DIR="${RESULT_DIR}" \
  SUNRAY_WS="${SUNRAY_WS}" \
  SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR}" \
  PX4_BUILD_DIR="${PX4_BUILD_DIR}" \
  PX4CTRL_WS="${PX4CTRL_WS}" \
  LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS}" \
  FASTLIO_WS="${FASTLIO_WS}" \
  FASTLIO_SRC="${FASTLIO_SRC}" \
  LIVOX_COMPAT_SRC="${LIVOX_COMPAT_SRC}" \
  GOAL4_DIFF_PLANNER_WS="${GOAL4_DIFF_PLANNER_WS}" \
  PX4CTRL_CORE_PROFILE="${PX4CTRL_CORE_PROFILE}" \
  PX4CTRL_EXPECTED_BUILD_BACKEND="${PX4CTRL_EXPECTED_BUILD_BACKEND}" \
  PX4CTRL_HOVER_PERCENTAGE="${PX4CTRL_HOVER_PERCENTAGE}" \
  FACTORY_WORLD_MODE="${FACTORY_WORLD_MODE}" \
  WORLD_FILE="${WORLD_FILE}" \
  FACTORY_MODEL_PATH="${FACTORY_MODEL_PATH}" \
  SUNRAY_GAZEBO_LAUNCH_FILE="${SUNRAY_GAZEBO_LAUNCH_FILE}" \
  SUNRAY_UAV_INIT_X="${SUNRAY_UAV_INIT_X}" \
  SUNRAY_UAV_INIT_Y="${SUNRAY_UAV_INIT_Y}" \
  SUNRAY_UAV_INIT_Z="${SUNRAY_UAV_INIT_Z}" \
  SUNRAY_UAV_INIT_YAW="${SUNRAY_UAV_INIT_YAW}" \
  PX4CTRL_EKF2_EV_CTRL_OVERRIDE="${PX4CTRL_EKF2_EV_CTRL_OVERRIDE}" \
  PX4CTRL_EKF2_HGT_REF_OVERRIDE="${PX4CTRL_EKF2_HGT_REF_OVERRIDE}" \
  PX4CTRL_BOOT_PARAM_OVERRIDES="${PX4CTRL_BOOT_PARAM_OVERRIDES}" \
  FASTLIO_FILTER_SIZE_SURF="${FASTLIO_FILTER_SIZE_SURF}" \
  FASTLIO_FILTER_SIZE_MAP="${FASTLIO_FILTER_SIZE_MAP}" \
  MAVROS_PLUGIN_CONFIG_SOURCE="${MAVROS_PLUGIN_CONFIG_SOURCE}" \
  PLANNER_VARIANT=diff_planner \
  GUI=false \
  OPEN_RVIZ=false \
  KEEP_ALIVE=false \
  DIFF_INTERACTIVE_CLICK_GOAL=true \
  DIFF_AUTO_GOAL_IN_INTERACTIVE_REVIEW=true \
  DIFF_INTERACTIVE_AUTO_PASS_GOAL_COUNT="${GOAL_COUNT}" \
  DIFF_INTERACTIVE_REVIEW_HOLD_S="${DIFF_INTERACTIVE_REVIEW_HOLD_S}" \
  DIFF_INTERACTIVE_FINAL_HOVER_HOLD_S="${DIFF_INTERACTIVE_FINAL_HOVER_HOLD_S}" \
  DIFF_INTERACTIVE_TARGET_REACHED_XY_M=0.35 \
  DIFF_INTERACTIVE_TARGET_REACHED_Z_M=0.12 \
  DIFF_INTERACTIVE_TARGET_HOLD_S="${DIFF_INTERACTIVE_TARGET_HOLD_S}" \
  DIFF_INTERACTIVE_TARGET_HOLD_MAX_SPEED_MPS=0.45 \
  DIFF_INTERACTIVE_TARGET_HOLD_MAX_VZ_MPS=0.25 \
  DIFF_PUBLISH_HOVER_DURING_TAKEOFF="${DIFF_PUBLISH_HOVER_DURING_TAKEOFF}" \
  DIFF_PUBLISH_HOVER_DURING_TAKEOFF_DELAY_S="${DIFF_PUBLISH_HOVER_DURING_TAKEOFF_DELAY_S}" \
  DIFF_INTERACTIVE_HANDOFF_MODE=adapter_hold \
  DIFF_ENABLE_CMD_SAFETY_ADAPTER=true \
  DIFF_CMD_INVALID_Z_POLICY=clamp \
  DIFF_CMD_MIN_Z=0.95 \
  DIFF_CMD_MAX_Z=1.15 \
  DIFF_CMD_SAFETY_MAX_POSITION_JUMP_M=0.50 \
  DIFF_CMD_SAFETY_MAX_POSITION_JUMP_SPEED_MPS=3.0 \
  EGO_VIRTUAL_CEIL_HEIGHT=1.15 \
  EGO_VISUALIZATION_TRUNCATE_HEIGHT=1.25 \
  EGO_MAX_VEL=0.4 \
  EGO_MAX_ACC=0.5 \
  TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S}" \
  POINTCLOUD_ROTATION_MODE=full \
  POINTCLOUD_MIN_WORLD_Z_M=0.50 \
  POINTCLOUD_REVIEW_VOXEL_SIZE_M=0.08 \
  bash Scripts/sunray/run_px4ctrl_ego_single_gate.sh
) > "${RESULT_DIR}/runner_outer.log" 2>&1 &
runner_pid=$!
echo "${runner_pid}" > "${RESULT_DIR}/runner_pid.txt"

set +u
source /opt/ros/noetic/setup.bash
source "${LOCAL_ROS1_WS}/devel/setup.bash"
source "${GOAL4_DIFF_PLANNER_WS}/devel/setup.bash"
set -u

cd "${PROJECT_ROOT}" || exit 97
python3 Scripts/sunray/probe_diff_interactive_goal_switch_chain.py \
  --result-dir "${RESULT_DIR}" \
  --output-json DIFF_INTERACTIVE_GOAL_SWITCH_CHAIN_PROBE.json \
  --goals="${GOALS}" \
  --ready-timeout-s "${DIFF_INTERACTIVE_READY_TIMEOUT_S}" \
  --pre-goal-stable-timeout-s "${DIFF_INTERACTIVE_PRE_GOAL_STABLE_TIMEOUT_S}" \
  --pre-goal-stable-s 1.0 \
  --reach-xy-radius-m 0.35 \
  --reach-z-tol-m 0.12 \
  --reach-max-speed-mps 0.45 \
  --reach-max-vz-mps 0.25 \
  --reach-hold-s "${DIFF_INTERACTIVE_TARGET_HOLD_S}" \
  --min-cmd-z-m 0.95 \
  --max-cmd-z-m 1.15 \
  --cmd-end-z-tol-m 0.12 \
  --goal-timeout-s "${DIFF_INTERACTIVE_GOAL_TIMEOUT_S}" \
  > "${RESULT_DIR}/probe_stdout.txt" 2> "${RESULT_DIR}/probe_stderr.txt"
probe_exit=$?

echo "PROBE_EXIT=${probe_exit}" > "${RESULT_DIR}/outer_status.txt"
wait "${runner_pid}"
runner_exit=$?
echo "RUNNER_EXIT=${runner_exit}" >> "${RESULT_DIR}/outer_status.txt"
date --iso-8601=seconds > "${RESULT_DIR}/auto123_gate_end.txt"

if [[ "${probe_exit}" -ne 0 ]]; then
  exit "${probe_exit}"
fi
exit "${runner_exit}"
