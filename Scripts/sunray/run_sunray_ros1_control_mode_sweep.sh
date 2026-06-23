#!/usr/bin/env bash
# Compare Sunray/PX4 control command interfaces on the same model/world.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RUN_ID="${RUN_ID:-sunray_ros1_control_mode_sweep_$(date +%Y%m%d_%H%M%S)}"
RESULT_ROOT="${RESULT_ROOT:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
MODES="${MODES:-xyzpos posvel xyvelzpos ctrltraj}"
MISSIONS="${MISSIONS:-takeoff_hover_land figure8}"

mkdir -p "${RESULT_ROOT}"

status_for_run() {
  local gate="$1"
  python3 - "$gate" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
try:
    j = json.loads(p.read_text(encoding="utf-8"))
except Exception as exc:
    print(f"blocked_json:{exc}")
    raise SystemExit(0)
print(j.get("status", "unknown"))
PY
}

for mission in ${MISSIONS}; do
  for mode in ${MODES}; do
    case "${mission}" in
      takeoff_hover_land)
        timeout_s="${TAKEOFF_TIMEOUT_S:-150}"
        extra_args="${TAKEOFF_MISSION_ARGS:-}"
        ;;
      figure8)
        timeout_s="${FIGURE8_TIMEOUT_S:-190}"
        extra_args="${FIGURE8_MISSION_ARGS:---figure8-period-s 16 --figure8-laps 2 --initial-hover-s 5 --pre-figure8-hold-s 2 --post-figure8-hold-s 2 --max-figure8-rmse-xy-m 0.35 --max-figure8-max-xy-error-m 0.75 --max-figure8-time-sync-rmse-xy-m 0.45 --max-figure8-time-sync-max-xy-error-m 1.0}"
        ;;
      *)
        echo "Unknown mission: ${mission}" >&2
        exit 2
        ;;
    esac

    run_dir="${RESULT_ROOT}/${mission}_${mode}"
    echo "=== ${mission} ${mode} -> ${run_dir}" | tee -a "${RESULT_ROOT}/sweep.log"
    set +e
    PROJECT_ROOT="${PROJECT_ROOT}" \
    RUN_ID="${RUN_ID}_${mission}_${mode}" \
    RESULT_DIR="${run_dir}" \
    MISSION="${mission}" \
    GUI="${GUI:-false}" \
    RVIZ="${RVIZ:-false}" \
    FASTLIO="${FASTLIO:-false}" \
    WAIT_NONEMPTY_LIDAR="${WAIT_NONEMPTY_LIDAR:-true}" \
    REQUIRE_NONEMPTY_LIDAR="${REQUIRE_NONEMPTY_LIDAR:-false}" \
    TOTAL_TIMEOUT_S="${timeout_s}" \
    MISSION_NODE_ARGS="--control-mode ${mode} ${extra_args} ${MISSION_NODE_ARGS_EXTRA:-}" \
    bash "${PROJECT_ROOT}/Scripts/sunray/run_sunray_ros1_native_mission_gate.sh" \
      > "${run_dir}.stdout.log" 2> "${run_dir}.stderr.log"
    rc=$?
    set -e
    echo "${rc}" > "${run_dir}.exit_code"
    if [[ -f "${run_dir}/SUNRAY_ROS1_NATIVE_MISSION_GATE.json" ]]; then
      status="$(status_for_run "${run_dir}/SUNRAY_ROS1_NATIVE_MISSION_GATE.json")"
    else
      status="blocked_no_gate_json"
    fi
    echo "${mission},${mode},${rc},${status},${run_dir}" | tee -a "${RESULT_ROOT}/sweep_runs.csv"
  done
done

python3 "${PROJECT_ROOT}/Scripts/sunray/summarize_sunray_ros1_control_mode_sweep.py" \
  --result-root "${RESULT_ROOT}" \
  --out "${RESULT_ROOT}/control_mode_sweep_summary.json" \
  --csv-out "${RESULT_ROOT}/control_mode_sweep_summary.csv"

echo "${RESULT_ROOT}"
