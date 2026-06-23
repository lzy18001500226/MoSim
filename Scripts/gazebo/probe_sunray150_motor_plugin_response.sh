#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
WORLD="${WORLD:-Config/gazebo/worlds/sunray150_motor_plugin_diagnostic.sdf}"
WORLD_NAME="${WORLD_NAME:-sunray150_motor_plugin_diagnostic}"
MODEL_NAME="${MODEL_NAME:-sunray150_assembled_motor_test}"
COMMAND_TOPIC="${COMMAND_TOPIC:-/sunray150/gazebo/command/motor_speed}"
COMMAND_VELOCITY="${COMMAND_VELOCITY:-600}"
TARGET_SAMPLES="${TARGET_SAMPLES:-30}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-12}"

cd "${PROJECT_ROOT}"
source Scripts/gazebo/setup_gazebo_wsl_env.sh

stamp="$(date +%Y%m%d_%H%M%S)"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/motor_plugin_diagnostic_${stamp}}"
mkdir -p "${RESULT_DIR}"

server_pid=""
cleanup() {
  if [[ -n "${server_pid}" ]]; then
    kill "${server_pid}" 2>/dev/null || true
    sleep 1
    pkill -P "${server_pid}" 2>/dev/null || true
  fi
}
trap cleanup EXIT

ign gazebo -r -s "${WORLD}" \
  > "${RESULT_DIR}/server.out" \
  2> "${RESULT_DIR}/server.err" &
server_pid="$!"
printf '%s\n' "${server_pid}" > "${RESULT_DIR}/server.pid"

for _ in $(seq 1 30); do
  ign topic -l > "${RESULT_DIR}/topics.txt" 2>&1 || true
  if grep -q "/world/${WORLD_NAME}/stats" "${RESULT_DIR}/topics.txt"; then
    break
  fi
  sleep 1
done

timeout 5s ign topic -e -t "/world/${WORLD_NAME}/stats" -n 1 \
  > "${RESULT_DIR}/stats_once.txt" \
  2> "${RESULT_DIR}/stats_once.err" || true

python3 Scripts/gazebo/capture_gazebo_pose_truth_topic.py \
  --topic "/world/${WORLD_NAME}/dynamic_pose/info" \
  --model-name "${MODEL_NAME}" \
  --output-jsonl "${RESULT_DIR}/gazebo_truth_pose.jsonl" \
  --summary-json "${RESULT_DIR}/GAZEBO_TRUTH_POSE_RECORDING.json" \
  --timeout-seconds "${TIMEOUT_SECONDS}" \
  --target-samples "${TARGET_SAMPLES}" \
  --frame-id world \
  > "${RESULT_DIR}/recorder.out" \
  2> "${RESULT_DIR}/recorder.err" &
recorder_pid="$!"

sleep 1
timeout 3s ign topic \
  -t "${COMMAND_TOPIC}" \
  --msgtype gz.msgs.Actuators \
  -p "velocity: [${COMMAND_VELOCITY}, ${COMMAND_VELOCITY}, ${COMMAND_VELOCITY}, ${COMMAND_VELOCITY}]" \
  > "${RESULT_DIR}/command.out" \
  2> "${RESULT_DIR}/command.err" || true

wait "${recorder_pid}" || true

python3 - "${RESULT_DIR}" <<'PY'
import json
import math
import sys
from pathlib import Path

result = Path(sys.argv[1])
rows = []
pose_path = result / "gazebo_truth_pose.jsonl"
if pose_path.exists():
    for line in pose_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        pos = row.get("position_m")
        if isinstance(pos, list) and len(pos) == 3:
            rows.append(row)

z_values = [float(row["position_m"][2]) for row in rows]
report = {
    "schema": "mosim.sunray150_motor_plugin_response_probe.v1",
    "status": "passed" if len(z_values) >= 5 and max(z_values) - min(z_values) >= 0.05 else "blocked",
    "result_dir": str(result),
    "sample_count": len(rows),
    "first_z_m": z_values[0] if z_values else None,
    "last_z_m": z_values[-1] if z_values else None,
    "min_z_m": min(z_values) if z_values else None,
    "max_z_m": max(z_values) if z_values else None,
    "z_range_m": (max(z_values) - min(z_values)) if z_values else None,
    "gate": "constant Gazebo transport motor command causes measurable state-topic z response",
    "claim_boundary": [
        "motor-plugin plant response only",
        "no hover, trajectory, controller-performance, planner_ready, or multi-UAV claim"
    ],
}
(result / "MOTOR_PLUGIN_RESPONSE_PROBE.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(0 if report["status"] == "passed" else 1)
PY
