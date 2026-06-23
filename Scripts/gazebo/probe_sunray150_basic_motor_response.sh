#!/usr/bin/env bash
# Minimal Gazebo motor-response probe for the accepted assembled Sunray150.
# This is a diagnostic gate only: fixed motor command -> state pose deltas.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
WORLD="${WORLD:-Config/gazebo/worlds/sunray150_single_uav_competition_light.sdf}"
WORLD_NAME="${WORLD_NAME:-sunray150_single_uav_competition_light}"
MODEL_NAME="${MODEL_NAME:-base_link}"
EXPECTED_ENTITY_ID="${EXPECTED_ENTITY_ID:-24}"
TRUTH_TOPIC="${TRUTH_TOPIC:-/world/${WORLD_NAME}/state}"
COMMAND_TOPIC="${COMMAND_TOPIC:-/sunray150/gazebo/command/motor_speed}"
COMMAND_MSGTYPE="${COMMAND_MSGTYPE:-ignition.msgs.Actuators}"
COMMAND_VELOCITY="${COMMAND_VELOCITY:-440 440 440 440}"
COMMAND_RATE_HZ="${COMMAND_RATE_HZ:-20}"
COMMAND_SECONDS="${COMMAND_SECONDS:-4}"
RECORDER_TIMEOUT_SECONDS="${RECORDER_TIMEOUT_SECONDS:-12}"
RECORDER_TARGET_SAMPLES="${RECORDER_TARGET_SAMPLES:-40}"
RECORDER_SAMPLE_TIMEOUT_SECONDS="${RECORDER_SAMPLE_TIMEOUT_SECONDS:-2}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/sunray150_basic_motor_response_probe}"

cd "${PROJECT_ROOT}"
source Scripts/gazebo/setup_gazebo_wsl_env.sh
mkdir -p "${RESULT_DIR}"

server_pid=""
command_pid=""
recorder_pid=""
cleanup() {
  if [[ -n "${command_pid}" ]]; then
    kill "${command_pid}" 2>/dev/null || true
    wait "${command_pid}" 2>/dev/null || true
  fi
  if [[ -n "${recorder_pid}" ]]; then
    kill "${recorder_pid}" 2>/dev/null || true
    wait "${recorder_pid}" 2>/dev/null || true
  fi
  if [[ -n "${server_pid}" ]]; then
    kill "${server_pid}" 2>/dev/null || true
    sleep 1
    pkill -P "${server_pid}" 2>/dev/null || true
    kill -9 "${server_pid}" 2>/dev/null || true
    wait "${server_pid}" 2>/dev/null || true
  fi
}
trap cleanup EXIT

ign gazebo -r -s "${WORLD}" \
  > "${RESULT_DIR}/gazebo.stdout.log" \
  2> "${RESULT_DIR}/gazebo.stderr.log" &
server_pid="$!"
printf '%s\n' "${server_pid}" > "${RESULT_DIR}/gazebo.pid"

for _ in $(seq 1 40); do
  ign topic -l > "${RESULT_DIR}/topics.txt" 2>&1 || true
  if grep -q "/world/${WORLD_NAME}/stats" "${RESULT_DIR}/topics.txt"; then
    break
  fi
  sleep 0.25
done

python3 Scripts/gazebo/capture_gazebo_state_truth_topic.py \
  --topic "${TRUTH_TOPIC}" \
  --model-name "${MODEL_NAME}" \
  --frame-id world \
  --expected-entity-id "${EXPECTED_ENTITY_ID}" \
  --capture-mode topic \
  --output-jsonl "${RESULT_DIR}/gazebo_truth_pose.jsonl" \
  --summary-json "${RESULT_DIR}/GAZEBO_TRUTH_POSE_RECORDING.json" \
  --timeout-seconds "${RECORDER_TIMEOUT_SECONDS}" \
  --sample-timeout-seconds "${RECORDER_SAMPLE_TIMEOUT_SECONDS}" \
  --target-samples "${RECORDER_TARGET_SAMPLES}" \
  --sleep-seconds 0.05 \
  > "${RESULT_DIR}/truth_recorder.stdout.log" \
  2> "${RESULT_DIR}/truth_recorder.stderr.log" &
recorder_pid="$!"

sleep 1.0

python3 - "${COMMAND_RATE_HZ}" "${COMMAND_SECONDS}" "${COMMAND_TOPIC}" "${COMMAND_MSGTYPE}" "${COMMAND_VELOCITY}" "${RESULT_DIR}" <<'PY' &
import subprocess
import sys
import time
from pathlib import Path

rate_hz = float(sys.argv[1])
duration_s = float(sys.argv[2])
topic = sys.argv[3]
msgtype = sys.argv[4]
values = [float(item) for item in sys.argv[5].split()]
result_dir = Path(sys.argv[6])
payload = "velocity: [" + ", ".join(f"{value:.12g}" for value in values) + "]"
period = 1.0 / max(rate_hz, 1e-6)
deadline = time.monotonic() + max(duration_s, 0.0)
stdout_parts = []
stderr_parts = []
returncodes = []
while time.monotonic() < deadline:
    completed = subprocess.run(
        ["ign", "topic", "-t", topic, "--msgtype", msgtype, "-p", payload],
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=2.0,
    )
    stdout_parts.append(completed.stdout)
    stderr_parts.append(completed.stderr)
    returncodes.append(int(completed.returncode))
    time.sleep(period)
result_dir.joinpath("command.stdout.log").write_text("".join(stdout_parts), encoding="utf-8")
result_dir.joinpath("command.stderr.log").write_text("".join(stderr_parts), encoding="utf-8")
result_dir.joinpath("command.rc").write_text(("0" if all(code == 0 for code in returncodes) else "1") + "\n", encoding="utf-8")
result_dir.joinpath("command_publish_count.txt").write_text(str(len(returncodes)) + "\n", encoding="utf-8")
PY
command_pid="$!"

if wait "${recorder_pid}"; then
  printf '0\n' > "${RESULT_DIR}/truth_recorder.rc"
else
  printf '%s\n' "$?" > "${RESULT_DIR}/truth_recorder.rc"
fi
recorder_pid=""

if wait "${command_pid}"; then
  printf '0\n' > "${RESULT_DIR}/command_wait.rc"
else
  printf '%s\n' "$?" > "${RESULT_DIR}/command_wait.rc"
fi
command_pid=""

python3 - "${RESULT_DIR}" "${COMMAND_VELOCITY}" <<'PY'
import json
import math
import sys
from pathlib import Path

result_dir = Path(sys.argv[1])
command_velocity = [float(item) for item in sys.argv[2].split()]
rows = []
pose_path = result_dir / "gazebo_truth_pose.jsonl"
if pose_path.exists():
    for line in pose_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        pos = row.get("position_m")
        quat = row.get("orientation_xyzw")
        if isinstance(pos, list) and len(pos) == 3 and isinstance(quat, list) and len(quat) == 4:
            rows.append(row)

def euler(q):
    x, y, z, w = [float(item) for item in q]
    n = math.sqrt(x*x + y*y + z*z + w*w) or 1.0
    x, y, z, w = x/n, y/n, z/n, w/n
    roll = math.atan2(2*(w*x + y*z), 1 - 2*(x*x + y*y))
    pitch_arg = max(-1.0, min(1.0, 2*(w*y - z*x)))
    pitch = math.asin(pitch_arg)
    yaw = math.atan2(2*(w*z + x*y), 1 - 2*(y*y + z*z))
    return [roll, pitch, yaw]

report = {
    "schema": "mosim.sunray150_basic_motor_response_probe.v1",
    "status": "blocked_no_samples",
    "command_velocity": command_velocity,
    "sample_count": len(rows),
    "claim_boundary": [
        "direct fixed-motor Gazebo plant diagnostic only",
        "does not prove hover, forward flight, trajectory tracking, planner_ready, closed_loop, controller performance, or multi-UAV readiness"
    ],
}

if rows:
    first = rows[0]
    last = rows[-1]
    p0 = [float(item) for item in first["position_m"]]
    p1 = [float(item) for item in last["position_m"]]
    r0 = euler(first["orientation_xyzw"])
    r1 = euler(last["orientation_xyzw"])
    duration = float(last.get("time", 0.0)) - float(first.get("time", 0.0))
    max_tilt = 0.0
    for row in rows:
        roll, pitch, _ = euler(row["orientation_xyzw"])
        max_tilt = max(max_tilt, abs(roll), abs(pitch))
    report.update({
        "status": "recorded",
        "first_time_s": round(float(first.get("time", 0.0)), 6),
        "last_time_s": round(float(last.get("time", 0.0)), 6),
        "duration_s": round(duration, 6),
        "first_position_m": [round(item, 6) for item in p0],
        "last_position_m": [round(item, 6) for item in p1],
        "delta_position_m": [round(p1[i] - p0[i], 6) for i in range(3)],
        "first_rpy_rad": [round(item, 6) for item in r0],
        "last_rpy_rad": [round(item, 6) for item in r1],
        "delta_rpy_rad": [round(r1[i] - r0[i], 6) for i in range(3)],
        "max_abs_roll_or_pitch_rad": round(max_tilt, 6),
    })

summary_path = result_dir / "BASIC_MOTOR_RESPONSE_PROBE.json"
summary_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
PY
