#!/usr/bin/env bash
# Run a bounded equal-motor sweep on the diagnostic Sunray150 Gazebo world.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SWEEP_VALUES="${SWEEP_VALUES:-380 400 420 440}"
RESULT_ROOT="${RESULT_ROOT:-Results/gazebo_ros2/basic_diag_axis_sweep_$(date +%Y%m%d_%H%M%S)}"

cd "${PROJECT_ROOT}"
mkdir -p "${RESULT_ROOT}"

for value in ${SWEEP_VALUES}; do
  result_dir="${RESULT_ROOT}/equal_${value}"
  mkdir -p "${result_dir}"
  echo "=== equal ${value} rad/s ==="
  RESULT_DIR="${result_dir}" \
  WORLD=Config/gazebo/worlds/sunray150_motor_plugin_diagnostic.sdf \
  WORLD_NAME=sunray150_motor_plugin_diagnostic \
  MODEL_NAME=sunray150_assembled_motor_test \
  TRUTH_TOPIC=/world/sunray150_motor_plugin_diagnostic/state \
  EXPECTED_ENTITY_ID=8 \
  COMMAND_VELOCITY="${value} ${value} ${value} ${value}" \
  COMMAND_TIMES=80 \
  TARGET_SAMPLES=120 \
  TIMEOUT_SECONDS=8 \
  MIN_SIM_DURATION_SECONDS=2 \
  TRUTH_CAPTURE_MODE=auto \
  bash Scripts/gazebo/probe_sunray150_axis_response.sh \
    > "${result_dir}/axis_response.stdout.log" \
    2> "${result_dir}/axis_response.stderr.log" || true
  cat "${result_dir}/AXIS_RESPONSE_PROBE.json"
done

python3 - "${RESULT_ROOT}" <<'PY'
import json
import math
import sys
from pathlib import Path

root = Path(sys.argv[1])
rows = []
for report_path in sorted(root.glob("equal_*/AXIS_RESPONSE_PROBE.json")):
    data = json.loads(report_path.read_text(encoding="utf-8"))
    value = float(report_path.parent.name.split("_", 1)[1])
    first = data.get("first_position_m") or [None, None, None]
    last = data.get("last_position_m") or [None, None, None]
    delta = data.get("delta_position_m") or [None, None, None]
    last_rpy = data.get("last_rpy_rad") or [None, None, None]
    rows.append({
        "command_rad_s": value,
        "status": data.get("status"),
        "sample_count": data.get("sample_count"),
        "duration_s": data.get("duration_s"),
        "first_z_m": first[2],
        "last_z_m": last[2],
        "delta_z_m": delta[2],
        "final_abs_roll_pitch_rad": max(abs(float(last_rpy[0] or 0.0)), abs(float(last_rpy[1] or 0.0))),
        "report": report_path.as_posix(),
    })

summary = {
    "schema": "mosim.sunray150_basic_axis_sweep.v1",
    "status": "recorded" if rows else "blocked_no_reports",
    "result_root": root.as_posix(),
    "rows": rows,
    "claim_boundary": [
        "diagnostic equal-motor plant response only",
        "does not prove visual acceptance, takeoff sequence, hover controller, forward flight, obstacle avoidance, or competition performance",
    ],
}
(root / "BASIC_AXIS_SWEEP_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
PY
