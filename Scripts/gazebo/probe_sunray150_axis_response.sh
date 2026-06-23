#!/usr/bin/env bash
# Bounded actuator-axis response probe for sunray150_assembled.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
WORLD="${WORLD:-Config/gazebo/worlds/sunray150_single_uav_competition_light.sdf}"
WORLD_NAME="${WORLD_NAME:-sunray150_single_uav_competition_light}"
MODEL_NAME="${MODEL_NAME:-sunray150_assembled}"
TRUTH_TOPIC="${TRUTH_TOPIC:-/world/${WORLD_NAME}/dynamic_pose/info}"
TRUTH_RECORDER_SCRIPT="${TRUTH_RECORDER_SCRIPT:-Scripts/gazebo/capture_gazebo_pose_truth_topic.py}"
EXPECTED_ENTITY_ID="${EXPECTED_ENTITY_ID:-}"
COMMAND_TOPIC="${COMMAND_TOPIC:-/sunray150/gazebo/command/motor_speed}"
COMMAND_MSGTYPE="${COMMAND_MSGTYPE:-ignition.msgs.Actuators}"
COMMAND_VELOCITY="${COMMAND_VELOCITY:-440 440 440 440}"
COMMAND_RATE_HZ="${COMMAND_RATE_HZ:-20}"
COMMAND_TIMES="${COMMAND_TIMES:-20}"
TARGET_SAMPLES="${TARGET_SAMPLES:-80}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-8}"
MIN_SIM_DURATION_SECONDS="${MIN_SIM_DURATION_SECONDS:-0}"
WAIT_TRUTH_TOPIC_SECONDS="${WAIT_TRUTH_TOPIC_SECONDS:-8}"
RECORDER_STARTUP_DELAY_SECONDS="${RECORDER_STARTUP_DELAY_SECONDS:-0.5}"
RECORDER_SAMPLE_TIMEOUT_SECONDS="${RECORDER_SAMPLE_TIMEOUT_SECONDS:-5.0}"
TRUTH_CAPTURE_MODE="${TRUTH_CAPTURE_MODE:-sample}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/sunray150_axis_response_probe}"

cd "${PROJECT_ROOT}"
source Scripts/gazebo/setup_gazebo_wsl_env.sh
mkdir -p "${RESULT_DIR}"

server_pid=""
recorder_pid=""
command_pid=""
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

ign gazebo -s "${WORLD}" \
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

truth_topic_ready=0
truth_wait_iterations="$(python3 - <<PY
import math
print(max(1, int(math.ceil(float("${WAIT_TRUTH_TOPIC_SECONDS}") / 0.25))))
PY
)"
for _ in $(seq 1 "${truth_wait_iterations}"); do
  ign topic -l > "${RESULT_DIR}/topics.txt" 2>&1 || true
  ign topic -i -t "${TRUTH_TOPIC}" > "${RESULT_DIR}/truth_topic_info.txt" 2>&1 || true
  if grep -q "^${TRUTH_TOPIC}$" "${RESULT_DIR}/topics.txt" \
    && grep -q "Publishers" "${RESULT_DIR}/truth_topic_info.txt" \
    && ! grep -q "No publishers" "${RESULT_DIR}/truth_topic_info.txt"; then
    truth_topic_ready=1
    break
  fi
  sleep 0.25
done
printf '%s\n' "${truth_topic_ready}" > "${RESULT_DIR}/truth_topic_ready.txt"

expected_entity_args=()
if [[ -n "${EXPECTED_ENTITY_ID}" ]]; then
  expected_entity_args=(--expected-entity-id "${EXPECTED_ENTITY_ID}")
fi

recorder_script="${TRUTH_RECORDER_SCRIPT}"
recorder_args=(
  --topic "${TRUTH_TOPIC}"
  --model-name "${MODEL_NAME}"
  --frame-id world
  --output-jsonl "${RESULT_DIR}/gazebo_truth_pose.jsonl"
  --summary-json "${RESULT_DIR}/GAZEBO_TRUTH_POSE_RECORDING.json"
  --timeout-seconds "${TIMEOUT_SECONDS}"
  --min-duration-seconds "${MIN_SIM_DURATION_SECONDS}"
  --sample-timeout-seconds "${RECORDER_SAMPLE_TIMEOUT_SECONDS}"
  --target-samples "${TARGET_SAMPLES}"
  --sleep-seconds 0.0
  --capture-mode "${TRUTH_CAPTURE_MODE}"
)
if [[ "${TRUTH_TOPIC}" == */state ]]; then
  recorder_script="Scripts/gazebo/capture_gazebo_state_truth_topic.py"
  recorder_args+=("${expected_entity_args[@]}")
else
  recorder_args+=(--startup-delay-seconds "${RECORDER_STARTUP_DELAY_SECONDS}")
fi

python3 "${recorder_script}" "${recorder_args[@]}" \
  > "${RESULT_DIR}/truth_recorder.stdout.log" \
  2> "${RESULT_DIR}/truth_recorder.stderr.log" &
recorder_pid="$!"

sleep 0.5

velocity_yaml="$(python3 - <<PY
values = [float(item) for item in "${COMMAND_VELOCITY}".split()]
if len(values) != 4:
    raise SystemExit(f"COMMAND_VELOCITY must contain exactly 4 values, got {len(values)}: {values}")
print("velocity: [" + ", ".join(f"{value:.12g}" for value in values) + "]")
PY
)"

python3 - "${COMMAND_RATE_HZ}" "5" "${TIMEOUT_SECONDS}" "${COMMAND_TOPIC}" "${velocity_yaml}" "${RESULT_DIR}" "${COMMAND_MSGTYPE}" "pre_unpause" <<'PY'
import subprocess
import sys
import time
from pathlib import Path

rate_hz = float(sys.argv[1])
times = int(sys.argv[2])
timeout_s = float(sys.argv[3])
topic = sys.argv[4]
payload = sys.argv[5]
result_dir = Path(sys.argv[6])
phase = sys.argv[8]
period = 1.0 / max(rate_hz, 1e-6)
deadline = time.monotonic() + timeout_s
stdout_parts = []
stderr_parts = []
returncodes = []
for _ in range(max(1, times)):
    if time.monotonic() >= deadline:
        break
    try:
        completed = subprocess.run(
            ["ign", "topic", "-t", topic, "--msgtype", sys.argv[7], "-p", payload],
            check=False,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=max(1.0, min(2.0, deadline - time.monotonic())),
        )
        stdout_parts.append(completed.stdout)
        stderr_parts.append(completed.stderr)
        returncodes.append(int(completed.returncode))
    except subprocess.TimeoutExpired as exc:
        stdout_parts.append(exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or ""))
        stderr_parts.append(exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or ""))
        stderr_parts.append(f"\nign topic publish timed out after {exc.timeout}s\n")
        returncodes.append(124)
    time.sleep(max(0.0, period))
result_dir.joinpath(f"command_{phase}.stdout.log").write_text("".join(stdout_parts), encoding="utf-8")
(result_dir / f"command_{phase}.stderr.log").write_text("".join(stderr_parts), encoding="utf-8")
(result_dir / f"command_{phase}.rc").write_text(("0" if all(code == 0 for code in returncodes) else "1") + "\n", encoding="utf-8")
(result_dir / f"command_{phase}_publish_count.txt").write_text(str(len(returncodes)) + "\n", encoding="utf-8")
PY

ign service \
  -s "/world/${WORLD_NAME}/control" \
  --reqtype ignition.msgs.WorldControl \
  --reptype ignition.msgs.Boolean \
  --timeout 2000 \
  --req "pause: false" \
  > "${RESULT_DIR}/unpause.stdout.log" \
  2> "${RESULT_DIR}/unpause.stderr.log" || true

python3 - "${COMMAND_RATE_HZ}" "${COMMAND_TIMES}" "${TIMEOUT_SECONDS}" "${COMMAND_TOPIC}" "${velocity_yaml}" "${RESULT_DIR}" "${COMMAND_MSGTYPE}" "post_unpause" <<'PY' &
import subprocess
import sys
import time
from pathlib import Path

rate_hz = float(sys.argv[1])
times = int(sys.argv[2])
timeout_s = float(sys.argv[3])
topic = sys.argv[4]
payload = sys.argv[5]
result_dir = Path(sys.argv[6])
phase = sys.argv[8]
period = 1.0 / max(rate_hz, 1e-6)
deadline = time.monotonic() + timeout_s
stdout_parts = []
stderr_parts = []
returncodes = []
for _ in range(max(1, times)):
    if time.monotonic() >= deadline:
        break
    try:
        completed = subprocess.run(
            ["ign", "topic", "-t", topic, "--msgtype", sys.argv[7], "-p", payload],
            check=False,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=max(1.0, min(2.0, deadline - time.monotonic())),
        )
        stdout_parts.append(completed.stdout)
        stderr_parts.append(completed.stderr)
        returncodes.append(int(completed.returncode))
    except subprocess.TimeoutExpired as exc:
        stdout_parts.append(exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or ""))
        stderr_parts.append(exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or ""))
        stderr_parts.append(f"\nign topic publish timed out after {exc.timeout}s\n")
        returncodes.append(124)
    time.sleep(max(0.0, period))
result_dir.joinpath(f"command_{phase}.stdout.log").write_text("".join(stdout_parts), encoding="utf-8")
(result_dir / f"command_{phase}.stderr.log").write_text("".join(stderr_parts), encoding="utf-8")
(result_dir / f"command_{phase}.rc").write_text(("0" if all(code == 0 for code in returncodes) else "1") + "\n", encoding="utf-8")
(result_dir / f"command_{phase}_publish_count.txt").write_text(str(len(returncodes)) + "\n", encoding="utf-8")
PY
command_pid="$!"

if wait "${recorder_pid}"; then
  printf '0\n' > "${RESULT_DIR}/truth_recorder.rc"
else
  printf '%s\n' "$?" > "${RESULT_DIR}/truth_recorder.rc"
fi
recorder_pid=""
if [[ -n "${command_pid}" ]]; then
  kill "${command_pid}" 2>/dev/null || true
  wait "${command_pid}" 2>/dev/null || true
  if [[ ! -f "${RESULT_DIR}/command_post_unpause.rc" ]]; then
    printf '0\n' > "${RESULT_DIR}/command_post_unpause.rc"
  fi
  command_pid=""
fi

python3 - "${RESULT_DIR}" "${COMMAND_VELOCITY}" "${COMMAND_MSGTYPE}" "${MIN_SIM_DURATION_SECONDS}" <<'PY'
import json
import math
import sys
from pathlib import Path

result = Path(sys.argv[1])
command_velocity = [float(item) for item in sys.argv[2].split()]
command_msgtype = sys.argv[3]
rows = []
for line in (result / "gazebo_truth_pose.jsonl").read_text(encoding="utf-8", errors="replace").splitlines():
    if not line.strip():
        continue
    row = json.loads(line)
    pos = row.get("position_m")
    if isinstance(pos, list) and len(pos) == 3:
        rows.append(row)

def euler(q):
    x, y, z, w = q
    n = math.sqrt(x*x + y*y + z*z + w*w) or 1.0
    x, y, z, w = x/n, y/n, z/n, w/n
    roll = math.atan2(2*(w*x + y*z), 1 - 2*(x*x + y*y))
    sp = 2*(w*y - z*x)
    pitch = math.asin(max(-1.0, min(1.0, sp)))
    yaw = math.atan2(2*(w*z + x*y), 1 - 2*(y*y + z*z))
    return [roll, pitch, yaw]

post_rc_path = result / "command_post_unpause.rc"
pre_rc_path = result / "command_pre_unpause.rc"
command_rc = post_rc_path.read_text(encoding="utf-8").strip() if post_rc_path.exists() else "0"
command_pre_rc = pre_rc_path.read_text(encoding="utf-8").strip() if pre_rc_path.exists() else ""
command_stderr = (result / "command_post_unpause.stderr.log").read_text(encoding="utf-8", errors="replace") if (result / "command_post_unpause.stderr.log").exists() else ""
report = {
    "schema": "mosim.sunray150_axis_response_probe.v1",
    "status": "blocked_command_publish_failed" if command_rc not in {"0", ""} else "blocked_no_samples",
    "command_velocity": command_velocity,
    "command_msgtype": command_msgtype,
    "command_rc": command_rc,
    "command_pre_unpause_rc": command_pre_rc,
    "command_stderr_tail": command_stderr[-800:],
    "sample_count": len(rows),
    "claim_boundary": [
        "direct Gazebo actuator-axis response only",
        "does not prove hover, trajectory tracking, planner_ready, closed_loop, controller performance, or multi-UAV readiness"
    ],
}
if rows:
    enough_duration = True
    if float(sys.argv[4]) > 0:
        min_duration = float(sys.argv[4])
        start_time = float(rows[0].get("time", 0.0))
        duration_rows = [row for row in rows if float(row.get("time", 0.0)) - start_time >= min_duration]
        if not duration_rows:
            enough_duration = False
            report["status"] = "blocked_min_sim_duration_not_reached"
            report["min_required_duration_s"] = min_duration
            report["observed_duration_s"] = round(float(rows[-1].get("time", 0.0)) - start_time, 6)
    first = rows[0]
    last = rows[-1]
    p0 = [float(item) for item in first["position_m"]]
    p1 = [float(item) for item in last["position_m"]]
    r0 = euler(first.get("orientation_xyzw", [0, 0, 0, 1]))
    r1 = euler(last.get("orientation_xyzw", [0, 0, 0, 1]))
    report.update({
        "status": ("recorded" if enough_duration else report["status"]) if command_rc == "0" else "blocked_command_publish_failed",
        "first_time_s": first.get("time"),
        "last_time_s": last.get("time"),
        "duration_s": round(float(last.get("time", 0.0)) - float(first.get("time", 0.0)), 6),
        "first_position_m": [round(item, 6) for item in p0],
        "last_position_m": [round(item, 6) for item in p1],
        "delta_position_m": [round(p1[i] - p0[i], 6) for i in range(3)],
        "first_rpy_rad": [round(item, 6) for item in r0],
        "last_rpy_rad": [round(item, 6) for item in r1],
        "delta_rpy_rad": [round(r1[i] - r0[i], 6) for i in range(3)],
    })

(result / "AXIS_RESPONSE_PROBE.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(report, ensure_ascii=False, indent=2))
PY
