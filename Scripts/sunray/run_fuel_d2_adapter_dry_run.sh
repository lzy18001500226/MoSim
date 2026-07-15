#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
FUEL_DEPS_ROOT="${FUEL_DEPS_ROOT:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/fuel_deps}"
NLOPT_VERSION="${NLOPT_VERSION:-v2.7.1}"
NLOPT_ROOT="${NLOPT_ROOT:-${FUEL_DEPS_ROOT}/install/nlopt-${NLOPT_VERSION}}"
FUEL_WS="${FUEL_WS:-/opt/mosim_work/sunray_ws/fuel_ws_planner_only_debug_20260701_003}"
ROS_MASTER_PORT="${ROS_MASTER_PORT:-11329}"
ROS_MASTER_URI="${ROS_MASTER_URI:-http://127.0.0.1:${ROS_MASTER_PORT}}"
RUN_ID="${RUN_ID:-fuel_d2_adapter_dry_run_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
STIMULUS_TIMEOUT_S="${STIMULUS_TIMEOUT_S:-70}"
STIMULUS_DURATION_S="${STIMULUS_DURATION_S:-45}"

export PROJECT_ROOT
export NLOPT_ROOT
export ROS_MASTER_URI

mkdir -p "${RESULT_DIR}"

fail() {
  local reason="$1"
  echo "FUEL_D2_ADAPTER_DRY_RUN=FAIL"
  echo "reason=${reason}"
  printf '{"status":"failed","reason":"%s"}\n' "${reason}" >"${RESULT_DIR}/RUN_MANIFEST.json"
  exit 1
}

cleanup() {
  set +e
  for pid in ${ROSLAUNCH_PID:-} ${ROSCORE_PID:-}; do
    if [[ -n "${pid}" ]] && kill -0 "${pid}" >/dev/null 2>&1; then
      kill "${pid}" >/dev/null 2>&1
      wait "${pid}" >/dev/null 2>&1
    fi
  done
}
trap cleanup EXIT

echo "FUEL_D2_ADAPTER_DRY_RUN=START"
echo "project_root=${PROJECT_ROOT}"
echo "fuel_ws=${FUEL_WS}"
echo "nlopt_root=${NLOPT_ROOT}"
echo "ros_master_uri=${ROS_MASTER_URI}"
echo "result_dir=${RESULT_DIR}"

[[ -d "${PROJECT_ROOT}" ]] || fail "project_root_missing"
[[ -d "${FUEL_WS}" ]] || fail "fuel_ws_missing_run_fuel_d1_first"
[[ -f "${FUEL_WS}/devel/setup.bash" ]] || fail "fuel_ws_devel_setup_missing"

set +u
source /opt/ros/noetic/setup.bash
source "${FUEL_WS}/devel/setup.bash"
set -u

NLOPT_ROOT="${NLOPT_ROOT}" bash "${PROJECT_ROOT}/Scripts/sunray/check_fuel_ros1_preflight.sh" --strict-build \
  >"${RESULT_DIR}/fuel_d2_preflight.log" 2>&1 || fail "fuel_preflight_failed"

[[ -x "${FUEL_WS}/devel/lib/exploration_manager/exploration_node" ]] \
  || fail "exploration_node_not_executable"
[[ -x "${FUEL_WS}/devel/lib/plan_manage/traj_server" ]] \
  || fail "traj_server_not_executable"

cp "${PROJECT_ROOT}/Scripts/sunray/fuel_d2_adapter_dry_run.launch" "${RESULT_DIR}/fuel_d2_adapter_dry_run.launch"

roscore -p "${ROS_MASTER_PORT}" >"${RESULT_DIR}/roscore.log" 2>&1 &
ROSCORE_PID=$!
for _ in {1..20}; do
  if rosnode list >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done
rosnode list >/dev/null 2>&1 || fail "roscore_not_ready"

roslaunch --wait "${PROJECT_ROOT}/Scripts/sunray/fuel_d2_adapter_dry_run.launch" \
  >"${RESULT_DIR}/fuel_d2_roslaunch.log" 2>&1 &
ROSLAUNCH_PID=$!
sleep 6
if ! kill -0 "${ROSLAUNCH_PID}" >/dev/null 2>&1; then
  fail "fuel_roslaunch_exited_before_stimulus"
fi

set +e
timeout "${STIMULUS_TIMEOUT_S}" \
  python3 "${PROJECT_ROOT}/Scripts/sunray/fuel_d2_synthetic_stimulus.py" \
    --duration-s "${STIMULUS_DURATION_S}" \
    --summary-file "${RESULT_DIR}/fuel_d2_stimulus_summary.json" \
    >"${RESULT_DIR}/fuel_d2_stimulus.log" 2>&1
stimulus_exit=$?
set -e

rostopic list >"${RESULT_DIR}/topics.txt" 2>"${RESULT_DIR}/rostopic_list.err" || true
for topic in /planning/bspline /mosim/fuel_d2/position_cmd_observed /sdf_map/occupancy_local /sdf_map/occupancy_all; do
  rostopic info "${topic}" >"${RESULT_DIR}/topic_info_${topic//\//_}.txt" 2>&1 || true
done

forbidden_topics="$(grep -E '^/(uav[0-9]+/)?mavros(/|$)|^/mavros(/|$)|^/fmu(/|$)|setpoint_raw|setpoint_position|actuator_control' "${RESULT_DIR}/topics.txt" || true)"
if [[ -n "${forbidden_topics}" ]]; then
  printf '%s\n' "${forbidden_topics}" >"${RESULT_DIR}/forbidden_topics.txt"
  fail "forbidden_mavros_or_px4_command_topic_present"
fi

if [[ "${stimulus_exit}" -ne 0 ]]; then
  printf '{"status":"failed","reason":"stimulus_failed","stimulus_exit":%s,"result_dir":"%s"}\n' \
    "${stimulus_exit}" "${RESULT_DIR}" >"${RESULT_DIR}/RUN_MANIFEST.json"
  echo "FUEL_D2_ADAPTER_DRY_RUN=FAIL"
  echo "reason=stimulus_failed"
  echo "stimulus_exit=${stimulus_exit}"
  echo "result_dir=${RESULT_DIR}"
  exit "${stimulus_exit}"
fi

printf '{"status":"passed","result_dir":"%s","ros_master_uri":"%s","claim":"FUEL-D2 adapter dry-run only; no Gazebo/PX4/MAVROS control claim"}\n' \
  "${RESULT_DIR}" "${ROS_MASTER_URI}" >"${RESULT_DIR}/RUN_MANIFEST.json"
echo "FUEL_D2_ADAPTER_DRY_RUN=PASS"
echo "result_dir=${RESULT_DIR}"
