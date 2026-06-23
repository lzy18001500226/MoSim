#!/usr/bin/env bash
# Open the complete Gazebo animation review path for the accepted single-UAV
# figure-8/static-obstacle slice. This is a visual review wrapper, not a
# replacement for the headless numeric gate.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RESULT_ROOT="${RESULT_ROOT:-Results/gazebo_ros2}"
RESULT_DIR="${RESULT_DIR:-${RESULT_ROOT}/sunray150_single_uav_figure8_animation_review_$(date +%Y%m%d_%H%M%S)}"
SCENARIO="${SCENARIO:-Config/scenarios/system/sunray150_single_uav_competition_light.yaml}"
WORLD="${WORLD:-Config/gazebo/worlds/yunzong_planning_test_sunray150_assembled.sdf}"
WORLD_NAME="${WORLD_NAME:-yunzong_planning_test_sunray150_assembled}"
GUI_CONFIG="${GUI_CONFIG:-Config/gazebo/gui/sunray150_visual_review_gui.config}"
GAZEBO_GUI_CAPTURE_REVIEW="${GAZEBO_GUI_CAPTURE_REVIEW:-1}"
GAZEBO_GUI_CAPTURE_DELAY_S="${GAZEBO_GUI_CAPTURE_DELAY_S:-45}"
GAZEBO_GUI_CAPTURE_EXTRA_DELAY_S="${GAZEBO_GUI_CAPTURE_EXTRA_DELAY_S:-62}"
GAZEBO_GUI_CAPTURE_TITLE_REGEX="${GAZEBO_GUI_CAPTURE_TITLE_REGEX:-Gazebo|Ignition|sunray|yunzong|figure8|competition}"
GAZEBO_GUI_CAPTURE_PROCESS_REGEX="${GAZEBO_GUI_CAPTURE_PROCESS_REGEX:-.*}"
GAZEBO_GUI_SOFTWARE_RENDERING="${GAZEBO_GUI_SOFTWARE_RENDERING:-0}"
GAZEBO_GUI_TRAIL_MARKER="${GAZEBO_GUI_TRAIL_MARKER:-0}"
GAZEBO_GUI_CAMERA_FOLLOW="${GAZEBO_GUI_CAMERA_FOLLOW:-1}"
GAZEBO_GUI_CAMERA_ORBIT="${GAZEBO_GUI_CAMERA_ORBIT:-0}"
GAZEBO_RVIZ_REVIEW_PATHS="${GAZEBO_RVIZ_REVIEW_PATHS:-1}"
GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_X_M="${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_X_M:--0.233}"
GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Y_M="${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Y_M:--0.933}"
GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Z_M="${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Z_M:-0.467}"
TRAIL_MARKER_SCRIPT="${TRAIL_MARKER_SCRIPT:-Scripts/gazebo/publish_gazebo_truth_trail_marker.py}"

cd "${PROJECT_ROOT}"
mkdir -p "${RESULT_DIR}"

capture_gazebo_gui_review_window() {
  if [[ "${GAZEBO_GUI_CAPTURE_REVIEW}" != "1" ]]; then
    return 0
  fi
  local capture_dir="${RESULT_DIR}/screenshots/gazebo_gui_review"
  local mid_capture_dir="${capture_dir}/mid_figure8"
  local final_capture_dir="${capture_dir}/post_landing"
  mkdir -p "${mid_capture_dir}" "${final_capture_dir}"
  sleep "${GAZEBO_GUI_CAPTURE_DELAY_S}" || true

  if ! command -v powershell.exe >/dev/null 2>&1; then
    cat > "${RESULT_DIR}/GAZEBO_GUI_CAPTURE_STATUS.json" <<JSON
{
  "schema": "mosim.gazebo_gui_capture_status.v1",
  "status": "capture_unavailable",
  "reason": "missing_powershell_exe",
  "capture_dir": "${capture_dir}",
  "claim_boundary": "visual evidence capture attempt only; no controller, planner, localization, or closed-loop success is claimed"
}
JSON
    return 0
  fi

  local ps_script="${PROJECT_ROOT}/Scripts/tools/capture_window_foreground.ps1"
  local ps_script_win mid_capture_dir_win final_capture_dir_win stdout_log stderr_log rc=0
  ps_script_win="$(wslpath -w "${ps_script}")"
  mid_capture_dir_win="$(wslpath -w "${mid_capture_dir}")"
  final_capture_dir_win="$(wslpath -w "${final_capture_dir}")"
  stdout_log="${RESULT_DIR}/gazebo_gui_capture.stdout.log"
  stderr_log="${RESULT_DIR}/gazebo_gui_capture.stderr.log"
  powershell.exe -NoProfile -ExecutionPolicy Bypass \
    -File "${ps_script_win}" \
    -TitleRegex "${GAZEBO_GUI_CAPTURE_TITLE_REGEX}" \
    -ProcessRegex "${GAZEBO_GUI_CAPTURE_PROCESS_REGEX}" \
    -OutDir "${mid_capture_dir_win}" \
    -Maximize \
    -MinimizeAfter \
    > "${stdout_log}" \
    2> "${stderr_log}" || rc="$?"
  printf '%s\n' "${rc}" > "${RESULT_DIR}/gazebo_gui_capture.rc"

  local extra_delay="${GAZEBO_GUI_CAPTURE_EXTRA_DELAY_S}"
  if python3 - <<PY
import sys
sys.exit(0 if float("${extra_delay}") > float("${GAZEBO_GUI_CAPTURE_DELAY_S}") else 1)
PY
  then
    local wait_more
    wait_more="$(python3 - <<PY
print(max(0.0, float("${extra_delay}") - float("${GAZEBO_GUI_CAPTURE_DELAY_S}")))
PY
)"
    sleep "${wait_more}" || true
    powershell.exe -NoProfile -ExecutionPolicy Bypass \
      -File "${ps_script_win}" \
      -TitleRegex "${GAZEBO_GUI_CAPTURE_TITLE_REGEX}" \
      -ProcessRegex "${GAZEBO_GUI_CAPTURE_PROCESS_REGEX}" \
      -OutDir "${final_capture_dir_win}" \
      -Maximize \
      -MinimizeAfter \
      >> "${stdout_log}" \
      2>> "${stderr_log}" || rc="$?"
    printf '%s\n' "${rc}" > "${RESULT_DIR}/gazebo_gui_capture_final.rc"
  fi

  python3 - <<PY
import json
from pathlib import Path
capture_dir = Path("${capture_dir}")
manifests = sorted(capture_dir.glob("*/capture_manifest.json"))
rows = []
for manifest in manifests:
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8-sig"))
        if isinstance(payload, list):
            rows.extend(payload)
        elif isinstance(payload, dict):
            rows.append(payload)
    except Exception as exc:
        rows.append({"manifest": str(manifest), "manifest_error": f"{exc.__class__.__name__}: {exc}"})
pngs = sorted(capture_dir.glob("*/*.png"))
Path("${RESULT_DIR}/GAZEBO_GUI_CAPTURE_STATUS.json").write_text(json.dumps({
    "schema": "mosim.gazebo_gui_capture_status.v1",
    "status": "captured" if int("${rc}") == 0 and pngs else "capture_incomplete",
    "capture_method": "foreground_copyfromscreen_window_rect",
    "capture_rc": int("${rc}"),
    "capture_dir": "${capture_dir}",
    "capture_manifests": [str(path) for path in manifests],
    "png_count": len(pngs),
    "png_files": [{"path": str(path), "bytes": path.stat().st_size} for path in pngs],
    "window_rows": rows,
    "title_regex": "${GAZEBO_GUI_CAPTURE_TITLE_REGEX}",
    "process_regex": "${GAZEBO_GUI_CAPTURE_PROCESS_REGEX}",
    "stdout": "${stdout_log}",
    "stderr": "${stderr_log}",
    "claim_boundary": "Gazebo GUI visual evidence capture only; this does not prove controller performance, planner_ready, final closed_loop, localization success, or multi-UAV readiness",
    "foreground_capture_note": "Gazebo/OpenGL viewports are not reliable through PrintWindow background capture, so this review route briefly foregrounds/maximizes the Gazebo window, captures the target window rectangle, then minimizes it."
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
}

cat > "${RESULT_DIR}/ANIMATION_REVIEW_REQUEST.json" <<JSON
{
  "schema": "mosim.gazebo_animation_review_request.v1",
  "status": "starting",
  "purpose": "complete Gazebo simulation animation review for the single-UAV figure-8/static-obstacle slice",
  "scenario": "${SCENARIO}",
  "world": "${WORLD}",
  "world_name": "${WORLD_NAME}",
  "vehicle": "model://sunray150_assembled",
  "static_obstacle_source": "world_cylinders",
  "control_chain": "PositionCommand -> PlannerSetpoint -> ControllerOutput -> Gazebo actuator plant",
  "numeric_baseline": "full-world rerun required; light-world four-obstacle baseline is superseded for full-world visual review",
  "review_boundary": "visual animation review only; do not claim final controller performance, planner_ready, final closed_loop, UE acceptance, or multi-UAV readiness",
  "result_dir": "${RESULT_DIR}",
  "gazebo_gui_capture_review": $([[ "${GAZEBO_GUI_CAPTURE_REVIEW}" == "1" ]] && echo true || echo false),
    "gazebo_gui_capture_delay_s": ${GAZEBO_GUI_CAPTURE_DELAY_S},
    "gazebo_gui_capture_extra_delay_s": ${GAZEBO_GUI_CAPTURE_EXTRA_DELAY_S},
  "gazebo_gui_capture_title_regex": "${GAZEBO_GUI_CAPTURE_TITLE_REGEX}",
  "gazebo_gui_capture_process_regex": "${GAZEBO_GUI_CAPTURE_PROCESS_REGEX}",
  "gazebo_gui_trail_marker": $([[ "${GAZEBO_GUI_TRAIL_MARKER}" == "1" ]] && echo true || echo false),
  "gazebo_rviz_review_paths": $([[ "${GAZEBO_RVIZ_REVIEW_PATHS}" == "1" ]] && echo true || echo false),
  "gazebo_gui_camera_follow": $([[ "${GAZEBO_GUI_CAMERA_FOLLOW}" == "1" ]] && echo true || echo false),
  "gazebo_gui_camera_orbit": $([[ "${GAZEBO_GUI_CAMERA_ORBIT}" == "1" ]] && echo true || echo false),
  "gazebo_gui_camera_follow_offset_m": [${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_X_M}, ${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Y_M}, ${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Z_M}],
  "trail_marker_script": "${TRAIL_MARKER_SCRIPT}",
  "review_speed_policy": "default animation review uses scenario timing; any faster visual review must be explicitly requested with *_OVERRIDE environment variables"
}
JSON

capture_gazebo_gui_review_window &
gazebo_gui_capture_pid="$!"

GAZEBO_GUI_REVIEW=1 \
GAZEBO_GUI_START_PAUSED=1 \
GAZEBO_GUI_VERBOSE="${GAZEBO_GUI_VERBOSE:-2}" \
GUI_CONFIG="${GUI_CONFIG}" \
MOSIM_GAZEBO_SOFTWARE_RENDERING="${GAZEBO_GUI_SOFTWARE_RENDERING}" \
MOSIM_GAZEBO_USE_NVIDIA=0 \
SCENARIO="${SCENARIO}" \
WORLD_OVERRIDE="${WORLD}" \
WORLD_NAME_OVERRIDE="${WORLD_NAME}" \
STATIC_OBSTACLE_SOURCE_OVERRIDE="${STATIC_OBSTACLE_SOURCE_OVERRIDE:-world_cylinders}" \
WORLD_CYLINDER_OBSTACLE_RADIUS_M_OVERRIDE="${WORLD_CYLINDER_OBSTACLE_RADIUS_M_OVERRIDE:-0.35}" \
RESULT_DIR="${RESULT_DIR}" \
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-90}" \
FIGURE_DURATION_S_OVERRIDE="${FIGURE_DURATION_S_OVERRIDE:-}" \
TRACKER_DURATION_S_OVERRIDE="${TRACKER_DURATION_S_OVERRIDE:-}" \
FIGURE_PERIOD_S_OVERRIDE="${FIGURE_PERIOD_S_OVERRIDE:-}" \
FIGURE_X_AMP_OVERRIDE="${FIGURE_X_AMP_OVERRIDE:-}" \
FIGURE_Y_AMP_OVERRIDE="${FIGURE_Y_AMP_OVERRIDE:-}" \
FIGURE_ALTITUDE_OVERRIDE="${FIGURE_ALTITUDE_OVERRIDE:-}" \
TRUTH_TARGET_SAMPLES_OVERRIDE="${TRUTH_TARGET_SAMPLES_OVERRIDE:-}" \
TRAIL_MARKER_SCRIPT="${TRAIL_MARKER_SCRIPT}" \
GAZEBO_GUI_TRAIL_MARKER="${GAZEBO_GUI_TRAIL_MARKER}" \
GAZEBO_RVIZ_REVIEW_PATHS="${GAZEBO_RVIZ_REVIEW_PATHS}" \
GAZEBO_GUI_CAMERA_FOLLOW="${GAZEBO_GUI_CAMERA_FOLLOW}" \
GAZEBO_GUI_CAMERA_ORBIT="${GAZEBO_GUI_CAMERA_ORBIT}" \
GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_X_M="${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_X_M}" \
GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Y_M="${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Y_M}" \
GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Z_M="${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Z_M}" \
TRACKER_ROLL_CONTROL_SIGN_OVERRIDE="${TRACKER_ROLL_CONTROL_SIGN_OVERRIDE:--1.0}" \
TRACKER_PITCH_CONTROL_SIGN_OVERRIDE="${TRACKER_PITCH_CONTROL_SIGN_OVERRIDE:-1.0}" \
TRACKER_XY_CONTROL_SIGN_OVERRIDE="${TRACKER_XY_CONTROL_SIGN_OVERRIDE:-1.0}" \
TRACKER_TAKEOFF_XY_ENABLE_ALTITUDE_M_OVERRIDE="${TRACKER_TAKEOFF_XY_ENABLE_ALTITUDE_M_OVERRIDE:-}" \
TRACKER_TAKEOFF_STABLE_Z_ERROR_M_OVERRIDE="${TRACKER_TAKEOFF_STABLE_Z_ERROR_M_OVERRIDE:-}" \
TRACKER_TAKEOFF_STABLE_S_OVERRIDE="${TRACKER_TAKEOFF_STABLE_S_OVERRIDE:-}" \
TRACKER_HOLD_LAST_SETPOINT_WHEN_TRUTH_BUFFERED_OVERRIDE="${TRACKER_HOLD_LAST_SETPOINT_WHEN_TRUTH_BUFFERED_OVERRIDE:-0}" \
"${PROJECT_ROOT}/Scripts/gazebo/run_sunray150_figure8_obstacle_gate.sh"

wait "${gazebo_gui_capture_pid}" 2>/dev/null || true

python3 - <<PY
import json
from pathlib import Path
result_dir = Path("${RESULT_DIR}")
request = json.loads((result_dir / "ANIMATION_REVIEW_REQUEST.json").read_text(encoding="utf-8"))
runtime = {}
runtime_path = result_dir / "RUNTIME_STATUS.json"
if runtime_path.exists():
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
capture_status = {}
capture_path = result_dir / "GAZEBO_GUI_CAPTURE_STATUS.json"
if capture_path.exists():
    capture_status = json.loads(capture_path.read_text(encoding="utf-8"))
request.update({
    "status": "completed" if runtime.get("gate_passed") else "completed_with_runtime_blocker",
    "runtime_status": str(runtime_path),
    "gate_passed": bool(runtime.get("gate_passed")),
    "visual_artifact_type": "live_gazebo_gui_window" if capture_status.get("status") != "captured" else "live_gazebo_gui_window_plus_screenshot_bundle",
    "visual_artifact_note": "Gazebo GUI was opened by this wrapper; user visual acceptance still requires observing the live animation or a separately captured video/screenshot.",
    "gazebo_gui_capture_status": str(capture_path) if capture_path.exists() else "",
    "gazebo_gui_capture_result": capture_status,
})
(result_dir / "ANIMATION_REVIEW_REQUEST.json").write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(result_dir)
PY
