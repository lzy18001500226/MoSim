#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
WORLD="${WORLD:-Config/gazebo/worlds/sunray150_single_uav_competition_light.sdf}"
WORLD_NAME="${WORLD_NAME:-sunray150_single_uav_competition_light}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/tmp_pose_topic_single_sample_probe}"

cd "${PROJECT_ROOT}"
source Scripts/gazebo/setup_gazebo_wsl_env.sh
mkdir -p "${RESULT_DIR}"

ign gazebo -s -r "${WORLD}" >"${RESULT_DIR}/gazebo.stdout.log" 2>"${RESULT_DIR}/gazebo.stderr.log" &
pid="$!"
cleanup() {
  kill "${pid}" 2>/dev/null || true
  wait "${pid}" 2>/dev/null || true
}
trap cleanup EXIT

for _ in $(seq 1 40); do
  ign topic -l >"${RESULT_DIR}/topics.txt" 2>&1 || true
  if grep -q "/world/${WORLD_NAME}/dynamic_pose/info" "${RESULT_DIR}/topics.txt"; then
    break
  fi
  sleep 0.25
done

topics=(
  "/world/${WORLD_NAME}/stats"
  "/world/${WORLD_NAME}/state"
  "/world/${WORLD_NAME}/dynamic_pose/info"
  "/world/${WORLD_NAME}/pose/info"
  "/model/sunray150_assembled/pose"
)

for topic in "${topics[@]}"; do
  key="${topic#/}"
  key="${key//\//_}"
  timeout 4s ign topic -i -t "${topic}" >"${RESULT_DIR}/${key}.info.txt" 2>"${RESULT_DIR}/${key}.info.err" || true
  timeout 4s ign topic -e -t "${topic}" -n 1 >"${RESULT_DIR}/${key}.sample.txt" 2>"${RESULT_DIR}/${key}.sample.err" || true
done

python3 - "${RESULT_DIR}" <<'PY'
import json
import sys
from pathlib import Path

result = Path(sys.argv[1])
rows = []
for sample in sorted(result.glob("*.sample.txt")):
    text = sample.read_text(encoding="utf-8", errors="replace")
    info = sample.with_name(sample.name.replace(".sample.txt", ".info.txt"))
    rows.append({
        "topic_key": sample.name.replace(".sample.txt", ""),
        "sample_bytes": len(text.encode("utf-8", errors="replace")),
        "info_tail": info.read_text(encoding="utf-8", errors="replace")[-500:] if info.exists() else "",
        "sample_head": text[:500],
    })
report = {
    "schema": "mosim.tmp_pose_topic_single_sample_probe.v1",
    "rows": rows,
}
(result / "SINGLE_SAMPLE_TOPIC_PROBE.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
PY
