#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SCENARIO="${SCENARIO:-Config/scenarios/system/sunray150_gazebo_ros2_smoke.yaml}"
RESULT_ROOT="${RESULT_ROOT:-Results/gazebo_ros2/sunray150_gazebo_ros2_single_uav_hover_command_bracket}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-20}"
COMMANDS="${COMMANDS:-}"
CONTROLLER_COMMAND_RATE_HZ="${CONTROLLER_COMMAND_RATE_HZ:-}"
CONTROLLER_COMMAND_TIMES="${CONTROLLER_COMMAND_TIMES:-}"
RUNNER="${RUNNER:-Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh}"
EVALUATOR="${EVALUATOR:-Scripts/quality/evaluate_gazebo_hover_bracket.py}"

cd "${PROJECT_ROOT}"
mkdir -p "${RESULT_ROOT}"

if [[ -z "${COMMANDS}" ]]; then
  COMMANDS="$(python3 - <<PY
import yaml
from pathlib import Path
data = yaml.safe_load(Path("${SCENARIO}").read_text(encoding="utf-8"))
cfg = data["ros2"]["single_uav_hover_command_bracket"]
print(" ".join(str(item) for item in cfg["commands"]))
PY
)"
fi

if [[ -z "${CONTROLLER_COMMAND_RATE_HZ}" ]]; then
  CONTROLLER_COMMAND_RATE_HZ="$(python3 - <<PY
import yaml
from pathlib import Path
data = yaml.safe_load(Path("${SCENARIO}").read_text(encoding="utf-8"))
cfg = data["ros2"]["single_uav_hover_command_bracket"]
print(cfg.get("publish_rate_hz", 5))
PY
)"
fi

if [[ -z "${CONTROLLER_COMMAND_TIMES}" ]]; then
  CONTROLLER_COMMAND_TIMES="$(python3 - <<PY
import yaml
from pathlib import Path
data = yaml.safe_load(Path("${SCENARIO}").read_text(encoding="utf-8"))
cfg = data["ros2"]["single_uav_hover_command_bracket"]
print(cfg.get("publish_times", 5))
PY
)"
fi

OUTPUT_JSON="$(python3 - <<PY
import yaml
from pathlib import Path
data = yaml.safe_load(Path("${SCENARIO}").read_text(encoding="utf-8"))
cfg = data["ros2"]["single_uav_hover_command_bracket"]
print(f"${RESULT_ROOT}/{cfg.get('output_json', 'GAZEBO_HOVER_COMMAND_BRACKET_EVAL.json')}")
PY
)"

command_dir_name() {
  python3 - "$1" <<'PY'
import sys
value = float(sys.argv[1])
print(f"cmd_{value:.6f}".replace(".", "p"))
PY
}

sample_manifest="${RESULT_ROOT}/HOVER_BRACKET_RUN_MANIFEST.json"
printf '{\n  "schema": "mosim.gazebo_hover_command_bracket_run_manifest.v1",\n  "status": "running",\n  "scenario": "%s",\n  "result_root": "%s",\n  "commands": [%s],\n  "claim_boundary": "open-loop thrust-scale bracket only; no hover, closed_loop, planner_ready, controller-performance, or multi-UAV claim",\n  "samples": []\n}\n' \
  "${SCENARIO}" \
  "${RESULT_ROOT}" \
  "$(python3 - <<PY
import json
print(", ".join(json.dumps(float(item)) for item in "${COMMANDS}".split()))
PY
)" > "${sample_manifest}"

for command in ${COMMANDS}; do
  sample_dir="${RESULT_ROOT}/$(command_dir_name "${command}")"
  mkdir -p "${sample_dir}"
  sample_command="${command} ${command} ${command} ${command}"
  echo "running_hover_bracket_sample command=${command} result_dir=${sample_dir}"
  RESULT_DIR="${sample_dir}" \
  RUNTIME_GATE_PROFILE=single_uav_hover_command_bracket \
  START_GAZEBO_PAUSED="${START_GAZEBO_PAUSED:-1}" \
  UNPAUSE_GAZEBO_AFTER_CONTROLLER_COMMAND="${UNPAUSE_GAZEBO_AFTER_CONTROLLER_COMMAND:-1}" \
  RUN_GAZEBO=1 \
  RUN_ROS2_BRIDGE=1 \
  RUN_ACTUATOR_BRIDGE=1 \
  RUN_CONTROLLER_OUTPUT_NODE=1 \
  RUN_CONTROLLER_OUTPUT_FIXTURE=1 \
  RUN_ACTUATOR_COMMAND_CHECK=1 \
  RUN_GAZEBO_TRUTH_POSE=1 \
  RUN_PLANT_RESPONSE_EVAL=1 \
  RUN_LOCAL_MAP=0 \
  RUN_TOPIC_CHECK=0 \
  RUN_RATE_CHECK=0 \
  RUN_STATIC_TF=0 \
  RUN_TF_CHECK=0 \
  RUN_FASTLIO_PLANNER_INPUT_ADAPTER=0 \
  RUN_SPARK_FASTLIO=0 \
  RUN_CONTROLLER_COMMAND=0 \
  RUN_COMMAND_ACK_GUARD=0 \
  BUILD_MOSIM_ROS2_MSGS=0 \
  CONTROLLER_COMMAND_TYPE=normalized_motor_speed \
  CONTROLLER_COMMAND_VALUES="${sample_command}" \
  CONTROLLER_COMMAND_RATE_HZ="${CONTROLLER_COMMAND_RATE_HZ}" \
  CONTROLLER_COMMAND_TIMES="${CONTROLLER_COMMAND_TIMES}" \
  TIMEOUT_SECONDS="${TIMEOUT_SECONDS}" \
  bash "${RUNNER}" || true
done

python3 "${EVALUATOR}" \
  --scenario "${SCENARIO}" \
  --result-root "${RESULT_ROOT}" \
  --output-json "${OUTPUT_JSON}" \
  --commands ${COMMANDS}

python3 - <<PY
import json
from pathlib import Path

result_root = Path("${RESULT_ROOT}")
output_json = Path("${OUTPUT_JSON}")
eval_report = json.loads(output_json.read_text(encoding="utf-8")) if output_json.exists() else {}
payload = {
    "schema": "mosim.gazebo_hover_command_bracket_run_manifest.v1",
    "status": "completed" if eval_report.get("gate_passed") else "completed_with_blockers",
    "scenario": "${SCENARIO}",
    "result_root": "${RESULT_ROOT}",
    "eval_json": "${OUTPUT_JSON}",
    "commands": [float(item) for item in "${COMMANDS}".split()],
    "sample_dirs": [
        str(result_root / f"cmd_{float(item):.6f}".replace(".", "p"))
        for item in "${COMMANDS}".split()
    ],
    "gate_passed": bool(eval_report.get("gate_passed", False)),
    "blockers": eval_report.get("blockers", []),
    "warnings": eval_report.get("warnings", []),
    "claim_boundary": "open-loop thrust-scale bracket only; no hover, closed_loop, planner_ready, controller-performance, or multi-UAV claim",
}
Path("${sample_manifest}").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
PY
