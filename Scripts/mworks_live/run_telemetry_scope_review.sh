#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RUN_ID="${RUN_ID:-telemetry_scope_review_$(date +%Y%m%d_%H%M%S)}"
RESULT_ROOT="${RESULT_ROOT:-${PROJECT_ROOT}/Results/control_platform/mworks_telemetry_scope_review/${RUN_ID}}"
MWORKS_HOST="${MWORKS_HOST:-}"
MWORKS_PORT="${MWORKS_PORT:-49020}"
SCOPE_RATE_HZ="${SCOPE_RATE_HZ:-50}"
FLIGHT_MISSION="${FLIGHT_MISSION:-takeoff_hover_land}"
TELEMETRY_READY_TIMEOUT_S="${TELEMETRY_READY_TIMEOUT_S:-180}"
RUNTIME_PID=""
SENDER_PID=""

source "${PROJECT_ROOT}/Scripts/sunray/sunray_ros1_runtime_lock.sh"

cleanup() {
  set +e
  [[ -n "${SENDER_PID}" ]] && kill -TERM "${SENDER_PID}" >/dev/null 2>&1 || true
  [[ -n "${RUNTIME_PID}" ]] && kill -TERM "${RUNTIME_PID}" >/dev/null 2>&1 || true
  [[ -n "${SENDER_PID}" ]] && wait "${SENDER_PID}" >/dev/null 2>&1 || true
  [[ -n "${RUNTIME_PID}" ]] && wait "${RUNTIME_PID}" >/dev/null 2>&1 || true
  sunray_ros1_runtime_lock_release
}
trap cleanup EXIT TERM INT

mkdir -p "${RESULT_ROOT}/flight" "${RESULT_ROOT}/telemetry_scope"
printf '%s\n' "${RUN_ID}" > "${RESULT_ROOT}/run_id.txt"

sunray_ros1_runtime_lock_acquire

if pgrep -x gzserver >/dev/null 2>&1 || pgrep -f '[r]osmaster --core' >/dev/null 2>&1; then
  echo "existing Sunray/Gazebo runtime detected; refusing a second runtime" >&2
  exit 11
fi

export RUN_ID
export RESULT_DIR="${RESULT_ROOT}/flight"
export GUI="${GUI:-false}"
export KEEP_ALIVE="${KEEP_ALIVE:-false}"
export VEHICLE="${VEHICLE:-sunray150_with_mid360}"
export SUNRAY_STRIP_PX4_MODEL_PATH="false"
export REVIEW_OPEN_RVIZ="${REVIEW_OPEN_RVIZ:-false}"
export REVIEW_START_FASTLIO="${REVIEW_START_FASTLIO:-${REVIEW_OPEN_RVIZ}}"
export REVIEW_START_OCCUPANCY_NODE="${REVIEW_START_OCCUPANCY_NODE:-false}"
if [[ "${FLIGHT_MISSION}" == "figure8" ]]; then
  export TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S:-220}"
  export PX4CTRL_MISSION_EXTRA_ARGS="${PX4CTRL_MISSION_EXTRA_ARGS:---initial-hover-s 10 --steady-hover-tail-s 8 --force-disarm-after-land --command-x-bias-m -0.006 --command-y-bias-m -0.004 --command-z-bias-m 0.0 --figure8-period-s 42 --figure8-cycles 2 --figure8-x-amp-m 0.65 --figure8-y-amp-m 0.30 --trajectory-time-lead-s 0.18 --post-hold-s 2 --max-trajectory-xyz-rmse-m 0.05 --max-trajectory-xyz-p95-m 0.05 --max-trajectory-xyz-max-m 0.06 --max-hover-z-rmse-m 0.025}"
else
  export TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S:-150}"
fi
export MAVROS_READY_TIMEOUT_S="${MAVROS_READY_TIMEOUT_S:-90}"
export MAVROS_SET_STREAM_GROUPS="${MAVROS_SET_STREAM_GROUPS:-position}"
export FREQUENCY_AUDIT_DURATION_S="${FREQUENCY_AUDIT_DURATION_S:-0}"
export PX4CTRL_CORE_PROFILE="${PX4CTRL_CORE_PROFILE:-original}"
export PX4CTRL_MISSION_EXTRA_ARGS="${PX4CTRL_MISSION_EXTRA_ARGS:---initial-hover-s 55 --steady-hover-tail-s 8 --land-wait-s 25 --force-disarm-after-land --force-disarm-timeout-s 18 --pre-takeoff-state-stable-s 3.0 --pre-takeoff-state-timeout-s 30 --pre-takeoff-max-abs-roll-pitch-deg 0.5}"

printf '%s\n' "${FLIGHT_MISSION}" > "${RESULT_ROOT}/flight_mission.txt"

bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh" "${FLIGHT_MISSION}" \
  > "${RESULT_ROOT}/flight_runtime.log" 2>&1 &
RUNTIME_PID="$!"
printf '%s\n' "${RUNTIME_PID}" > "${RESULT_ROOT}/flight_runtime_pid.txt"

set +u
source /opt/ros/noetic/setup.bash
[[ -f /opt/mosim_work/sunray_ws/Sunray/devel/setup.bash ]] && \
  source /opt/mosim_work/sunray_ws/Sunray/devel/setup.bash
[[ -f "${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws/devel/setup.bash" ]] && \
  source "${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws/devel/setup.bash"
set -u

deadline=$((SECONDS + TELEMETRY_READY_TIMEOUT_S))
while (( SECONDS < deadline )); do
  if ! kill -0 "${RUNTIME_PID}" >/dev/null 2>&1; then
    echo "flight runtime exited before telemetry became available" >&2
    exit 12
  fi
  if timeout 3 rostopic echo -n 1 /uav1/mavros/local_position/odom >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
if ! timeout 3 rostopic echo -n 1 /uav1/mavros/local_position/odom >/dev/null 2>&1; then
  echo "ROS odometry did not become available within ${TELEMETRY_READY_TIMEOUT_S} seconds" >&2
  exit 13
fi

if [[ -z "${MWORKS_HOST}" ]]; then
  MWORKS_HOST="$(ip route show default 2>/dev/null | awk 'NR==1 {print $3}')"
fi
if [[ -z "${MWORKS_HOST}" ]]; then
  echo "unable to resolve Windows host for MWORKS telemetry" >&2
  exit 14
fi

python3 -u "${PROJECT_ROOT}/Scripts/mworks_live/ros1_telemetry_scope_sender.py" \
  --run-id "${RUN_ID}" \
  --result-dir "${RESULT_ROOT}/telemetry_scope" \
  --mworks-host "${MWORKS_HOST}" \
  --mworks-port "${MWORKS_PORT}" \
  --rate-hz "${SCOPE_RATE_HZ}" \
  > "${RESULT_ROOT}/telemetry_scope_sender.log" 2>&1 &
SENDER_PID="$!"
printf '%s\n' "${SENDER_PID}" > "${RESULT_ROOT}/telemetry_scope_sender_pid.txt"
printf '%s\n' "${MWORKS_HOST}:${MWORKS_PORT}" > "${RESULT_ROOT}/mworks_endpoint.txt"

wait "${RUNTIME_PID}"
RUNTIME_PID=""
