#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RUN_ID="${RUN_ID:-p7_ftc_generated_gazebo_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/control_platform/${RUN_ID}}"
PLUGIN_WS="${FTC_PLUGIN_WS:-${PROJECT_ROOT}/Results/control_platform/p7_ftc_gazebo_plugin_ws_v2}"
GENERATED_DIR="${PROJECT_ROOT}/Results/control_platform/p7_ftc_mworks_20260717/generated_c/MoSim_P7_FaultTolerantControl_CFunction_Sysblock"
GENERATED_LIB="${RESULT_DIR}/libp7_ftc_generated.so"
mkdir -p "${RESULT_DIR}"

bash "${PROJECT_ROOT}/Scripts/sunray/build_p7_ftc_actuator_plugin.sh" \
  > "${RESULT_DIR}/plugin_build.log" 2>&1

gcc -std=c99 -O2 -fPIC -shared \
  -I"${GENERATED_DIR}" -I"${GENERATED_DIR}/extern_inc" \
  "${GENERATED_DIR}/MoSim_P7_FaultTolerantControl_CFunction_Sysblock.c" \
  "${GENERATED_DIR}/MoSim_P7_FaultTolerantControl_CFunction_Sysblock_data.c" \
  "${GENERATED_DIR}/extern_inc/momodel_extern_ince1.c" \
  -lm -o "${GENERATED_LIB}" 2> "${RESULT_DIR}/generated_library_build.log"

set +u
source /opt/ros/noetic/setup.bash
source "${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws/devel/setup.bash"
set -u

coordinator_pid=""
basic_pid=""
cleanup() {
  if [[ -n "${coordinator_pid}" ]]; then kill "${coordinator_pid}" 2>/dev/null || true; fi
  if [[ -n "${basic_pid}" ]]; then kill "${basic_pid}" 2>/dev/null || true; fi
}
trap cleanup EXIT

set +e
FTC_PLUGIN_WS="${PLUGIN_WS}" \
MOSIM_ENABLE_FTC_ACTUATOR_PLUGIN=true \
GAZEBO_PLUGIN_PATH="${PLUGIN_WS}/devel/lib:${GAZEBO_PLUGIN_PATH:-}" \
LD_LIBRARY_PATH="${PLUGIN_WS}/devel/lib:${LD_LIBRARY_PATH:-}" \
PX4CTRL_SKIP_MISSION=true \
TOTAL_TIMEOUT_S=150 \
FREQUENCY_AUDIT_DURATION_S=0 \
CONTROL_DIAGNOSTICS_DURATION_S=100 \
TIME_TF_AUDIT_DURATION_S=0 \
RESULT_DIR="${RESULT_DIR}/basic_gate" \
bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh" takeoff_hover_land \
  > "${RESULT_DIR}/basic_gate_runner.log" 2>&1 &
basic_pid=$!
set -e

master_ready=false
for _ in $(seq 1 120); do
  if rosparam get /rosversion >/dev/null 2>&1; then master_ready=true; break; fi
  if ! kill -0 "${basic_pid}" 2>/dev/null; then break; fi
  sleep 0.5
done
if [[ "${master_ready}" != "true" ]]; then
  echo "ROS master did not become ready for P7 coordinator" >&2
  exit 4
fi

python3 "${PROJECT_ROOT}/Scripts/sunray/run_p7_ftc_generated_coordinator.py" \
  --generated-library "${GENERATED_LIB}" \
  --output "${RESULT_DIR}/P7_FTC_GENERATED_GAZEBO_GATE.json" \
  --csv "${RESULT_DIR}/P7_FTC_GENERATED_GAZEBO_TELEMETRY.csv" \
  > "${RESULT_DIR}/coordinator.log" 2>&1 &
coordinator_pid=$!

set +e
wait "${coordinator_pid}"
coordinator_rc=$?
wait "${basic_pid}"
basic_rc=$?
set -e
coordinator_pid=""
basic_pid=""

python3 - "${RESULT_DIR}" "${basic_rc}" "${coordinator_rc}" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
basic_rc, coordinator_rc = map(int, sys.argv[2:])
gate_path = root / "P7_FTC_GENERATED_GAZEBO_GATE.json"
gate = json.loads(gate_path.read_text(encoding="utf-8")) if gate_path.exists() else {}
summary = {
    "schema": "mosim.p7.ftc_runtime_closeout.v1",
    "status": "passed" if coordinator_rc == 0 and gate.get("status") == "passed" else "failed",
    "basic_gate_exit_code": basic_rc,
    "coordinator_exit_code": coordinator_rc,
    "generated_gate": str(gate_path),
    "basic_gate_result_dir": str(root / "basic_gate"),
    "claim_boundary": gate.get("claim_boundary", "No generated FTC runtime evidence produced."),
}
(root / "P7_FTC_RUNTIME_CLOSEOUT.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0 if summary["status"] == "passed" else 1)
PY
