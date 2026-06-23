#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
cd "${PROJECT_ROOT}"
source Scripts/gazebo/setup_gazebo_wsl_env.sh

world="${WORLD:-Config/gazebo/worlds/sunray150_single_uav_competition_light.sdf}"
world_name="${WORLD_NAME:-sunray150_single_uav_competition_light}"

ign gazebo -s -r "${world}" >/tmp/mosim_state_probe.out 2>/tmp/mosim_state_probe.err &
pid="$!"
cleanup() {
  kill "${pid}" 2>/dev/null || true
  wait "${pid}" 2>/dev/null || true
}
trap cleanup EXIT

sleep 4
echo "SERVICES"
timeout 5s ign service -l | grep "${world_name}" | head -80 || true
echo "TOPICS"
timeout 5s ign topic -l | grep "${world_name}" | head -80 || true
echo "STATE_SERVICE"
timeout 6s ign service \
  -s "/world/${world_name}/state" \
  --reqtype ignition.msgs.Empty \
  --reptype ignition.msgs.SerializedStepMap \
  --timeout 3000 \
  --req "" | head -120 || true
echo "STATE_TOPIC"
timeout 4s ign topic -e -t "/world/${world_name}/state" -n 1 | head -120 || true
echo "SERVER_STDERR"
tail -80 /tmp/mosim_state_probe.err || true
