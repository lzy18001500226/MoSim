#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
WORLD="${WORLD:-Config/gazebo/worlds/sunray150_single_uav_competition_light.sdf}"
WORLD_NAME="${WORLD_NAME:-sunray150_single_uav_competition_light}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/tmp_pose_topic_probe}"

cd "${PROJECT_ROOT}"
source Scripts/gazebo/setup_gazebo_wsl_env.sh
mkdir -p "${RESULT_DIR}"

ign gazebo -s -r "${WORLD}" \
  > "${RESULT_DIR}/gazebo.stdout.log" \
  2> "${RESULT_DIR}/gazebo.stderr.log" &
pid="$!"

cleanup() {
  kill "${pid}" 2>/dev/null || true
  wait "${pid}" 2>/dev/null || true
}
trap cleanup EXIT

for _ in $(seq 1 40); do
  ign topic -l > "${RESULT_DIR}/topics.txt" 2>&1 || true
  if grep -q "/world/${WORLD_NAME}/dynamic_pose/info" "${RESULT_DIR}/topics.txt"; then
    break
  fi
  sleep 0.25
done

timeout 2s ign topic -e -t "/world/${WORLD_NAME}/dynamic_pose/info" \
  > "${RESULT_DIR}/dynamic_pose_info.txt" \
  2> "${RESULT_DIR}/dynamic_pose_info.stderr.txt" || true

timeout 2s ign topic -e -t "/world/${WORLD_NAME}/pose/info" \
  > "${RESULT_DIR}/pose_info.txt" \
  2> "${RESULT_DIR}/pose_info.stderr.txt" || true

timeout 2s ign topic -e -t "/model/sunray150_assembled/pose" \
  > "${RESULT_DIR}/model_pose.txt" \
  2> "${RESULT_DIR}/model_pose.stderr.txt" || true

python3 - "${RESULT_DIR}" <<'PY'
import json
import re
import sys
from pathlib import Path

result = Path(sys.argv[1])
report = {
    "schema": "mosim.tmp_pose_topic_probe.v1",
    "topics": (result / "topics.txt").read_text(encoding="utf-8", errors="replace").splitlines(),
    "captures": {},
}
for name in ["dynamic_pose_info", "pose_info", "model_pose"]:
    text = (result / f"{name}.txt").read_text(encoding="utf-8", errors="replace") if (result / f"{name}.txt").exists() else ""
    stderr = (result / f"{name}.stderr.txt").read_text(encoding="utf-8", errors="replace") if (result / f"{name}.stderr.txt").exists() else ""
    report["captures"][name] = {
        "bytes": len(text.encode("utf-8", errors="replace")),
        "separator_count": len(re.findall(r"(?m)^---\\s*$", text)),
        "contains_sunray150_assembled": "sunray150_assembled" in text,
        "stderr_tail": stderr[-300:],
    }
(result / "POSE_TOPIC_PROBE.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
PY
