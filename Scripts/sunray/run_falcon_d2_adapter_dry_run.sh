#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="${1:-${ROOT_DIR}/Results/sunray_ros1/falcon_d2_adapter_dry_run_${STAMP}}"
mkdir -p "${OUT_DIR}"

ROS_MASTER_URI="${ROS_MASTER_URI:-http://127.0.0.1:11319}"
export ROS_MASTER_URI

set +u
source /opt/ros/noetic/setup.bash
set -u

bridge_summary="${OUT_DIR}/FALCON_D2_BRIDGE_SUMMARY.json"
stimulus_summary="${OUT_DIR}/FALCON_D2_SYNTHETIC_STIMULUS.json"
roscore_log="${OUT_DIR}/roscore.log"
bridge_log="${OUT_DIR}/bridge.log"
stimulus_log="${OUT_DIR}/stimulus.log"

cleanup() {
  if [ -n "${bridge_pid:-}" ]; then kill "${bridge_pid}" >/dev/null 2>&1 || true; fi
  if [ -n "${roscore_pid:-}" ]; then kill "${roscore_pid}" >/dev/null 2>&1 || true; fi
}
trap cleanup EXIT

roscore -p "${ROS_MASTER_URI##*:}" > "${roscore_log}" 2>&1 &
roscore_pid=$!
sleep 3

python3 "${ROOT_DIR}/Scripts/sunray/falcon_mosim_topic_bridge.py" \
  --summary-json "${bridge_summary}" \
  > "${bridge_log}" 2>&1 &
bridge_pid=$!
sleep 1

status="failed"
if timeout 30s python3 "${ROOT_DIR}/Scripts/sunray/falcon_d2_synthetic_stimulus.py" \
  --summary-json "${stimulus_summary}" \
  > "${stimulus_log}" 2>&1; then
  status="passed"
fi

cleanup
trap - EXIT

python3 - "$OUT_DIR" "$status" <<'PY'
import json
import sys
from pathlib import Path

out = Path(sys.argv[1])
status = sys.argv[2]
payload = {
    "schema": "mosim.falcon_d2_adapter_dry_run.v1",
    "status": status,
    "out_dir": str(out),
    "files": {
        "bridge_summary": str(out / "FALCON_D2_BRIDGE_SUMMARY.json"),
        "stimulus_summary": str(out / "FALCON_D2_SYNTHETIC_STIMULUS.json"),
        "roscore_log": str(out / "roscore.log"),
        "bridge_log": str(out / "bridge.log"),
        "stimulus_log": str(out / "stimulus.log"),
    },
    "claim_boundary": "Topic bridge dry-run only; not Gazebo/PX4/MAVROS/RViz or full-coverage evidence.",
}
(out / "FALCON_D2_ADAPTER_DRY_RUN.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
)
(out / "SUMMARY.md").write_text(
    "# FALCON D2 Adapter Dry Run\n\n"
    f"Status: `{status}`\n\n"
    "This verifies synthetic MoSim odom/cloud inputs are bridged to FALCON input topics.\n"
    "It is not runtime exploration evidence.\n",
    encoding="utf-8",
)
print(json.dumps(payload, ensure_ascii=False))
PY
