#!/usr/bin/env bash
# Open the accepted assembled Sunray150 in a minimal Gazebo review scene and
# hold equal motor speed for visual basic-flight review.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
WORLD="${WORLD:-Config/gazebo/worlds/sunray150_basic_flight_diagnostic_light.sdf}"
COMMAND_TOPIC="${COMMAND_TOPIC:-/sunray150/gazebo/command/motor_speed}"
COMMAND_MSGTYPE="${COMMAND_MSGTYPE:-ignition.msgs.Actuators}"
COMMAND_VELOCITY="${COMMAND_VELOCITY:-450 450 450 450}"
COMMAND_RATE_HZ="${COMMAND_RATE_HZ:-20}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_review/basic_flight_$(date +%Y%m%d_%H%M%S)}"

cd "${PROJECT_ROOT}"
source Scripts/gazebo/setup_gazebo_wsl_env.sh
mkdir -p "${RESULT_DIR}"

velocity_payload="$(python3 - <<PY
values = [float(item) for item in "${COMMAND_VELOCITY}".split()]
if len(values) != 4:
    raise SystemExit(f"COMMAND_VELOCITY must contain 4 values: {values}")
print("velocity: [" + ", ".join(f"{value:.12g}" for value in values) + "]")
PY
)"

ign gazebo -r "${WORLD}" >"${RESULT_DIR}/gazebo.stdout.log" 2>"${RESULT_DIR}/gazebo.stderr.log" &
gazebo_pid="$!"
printf '%s\n' "${gazebo_pid}" >"${RESULT_DIR}/gazebo.pid"

cleanup() {
  kill "${publisher_pid:-}" 2>/dev/null || true
  wait "${publisher_pid:-}" 2>/dev/null || true
}
trap cleanup EXIT

sleep 4
(
  period="$(python3 - <<PY
rate = float("${COMMAND_RATE_HZ}")
print(1.0 / rate)
PY
)"
  while kill -0 "${gazebo_pid}" 2>/dev/null; do
    ign topic -t "${COMMAND_TOPIC}" --msgtype "${COMMAND_MSGTYPE}" -p "${velocity_payload}" \
      >>"${RESULT_DIR}/command.stdout.log" 2>>"${RESULT_DIR}/command.stderr.log" || true
    sleep "${period}"
  done
) &
publisher_pid="$!"
printf '%s\n' "${publisher_pid}" >"${RESULT_DIR}/publisher.pid"

cat >"${RESULT_DIR}/REVIEW_MANIFEST.json" <<JSON
{
  "schema": "mosim.gazebo_basic_flight_visual_review.v1",
  "status": "running_for_manual_review",
  "world": "${WORLD}",
  "command_topic": "${COMMAND_TOPIC}",
  "command_msgtype": "${COMMAND_MSGTYPE}",
  "command_velocity_rad_s": [${COMMAND_VELOCITY// /, }],
  "claim_boundary": [
    "manual visual review only",
    "does not prove final controller performance, trajectory tracking, sensor chain, point cloud, occupancy map, obstacle avoidance, or multi-UAV readiness"
  ]
}
JSON
echo "${RESULT_DIR}"

wait "${gazebo_pid}"
