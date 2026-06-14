#!/usr/bin/env bash
set -euo pipefail

# Open the accepted Factory scene and drive only the visible UAV body through
# the MWORKS-to-UE bridge. This is the platform gate before any RViz/FAST-LIO
# manual review.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
SCENE_ID="factoryenvironmentcollect"
SCENE_SOURCE_ID="local_factoryenvironmentcollect"
MAP_PACKAGE="/Game/Maps/Demonstration"
MAP_ID="local_factoryenvironmentcollect"
SCENE_DIR="${PROJECT_ROOT}/Results/unreal_scene_mapping/${SCENE_ID}"
VISUAL_GATE_REPLAY_CSV="${VISUAL_GATE_REPLAY_CSV:-${SCENE_DIR}/render_replay.csv}"
MWORKS_STATE_REPLAY_CSV="${MWORKS_STATE_REPLAY_CSV:-${SCENE_DIR}/mworks_smoke/raw/sunray150_ue_${SCENE_ID}_linear_mpc_smoke.csv}"
UNREAL_HOST="${UNREAL_HOST:-$(ip route | awk '/^default/ {print $3; exit}')}"
OPEN_UE="${OPEN_UE:-1}"
REVIEW_DRY_RUN="${REVIEW_DRY_RUN:-0}"
if [[ -z "${FOLLOW_UAV_CAMERA+x}" ]]; then
  FOLLOW_UAV_CAMERA=1
  if [[ "${REVIEW_DRY_RUN}" == "1" ]]; then
    FOLLOW_UAV_CAMERA=0
  fi
fi
STREAM_ONLY="${STREAM_ONLY:-0}"
STREAM_FPS="${STREAM_FPS:-60}"
STREAM_RESAMPLE_HZ="${STREAM_RESAMPLE_HZ:-60}"
STREAM_REPLAY_SPEED="${STREAM_REPLAY_SPEED:-1.0}"
STREAM_MAX_FRAMES="${STREAM_MAX_FRAMES:-1}"
STREAM_PATH_REPLAY="${STREAM_PATH_REPLAY:-0}"
STREAM_LOOP_COUNT="${STREAM_LOOP_COUNT:-1}"
WAIT_UDP_SECONDS="${WAIT_UDP_SECONDS:-60}"
REVIEW_CAMERA_X_CM="${REVIEW_CAMERA_X_CM:--5733}"
REVIEW_CAMERA_Y_CM="${REVIEW_CAMERA_Y_CM:-2423}"
REVIEW_CAMERA_Z_CM="${REVIEW_CAMERA_Z_CM:-280}"
REVIEW_CAMERA_PITCH_DEG="${REVIEW_CAMERA_PITCH_DEG:--12}"
REVIEW_CAMERA_YAW_DEG="${REVIEW_CAMERA_YAW_DEG:-0}"
REVIEW_CAMERA_ROLL_DEG="${REVIEW_CAMERA_ROLL_DEG:-0}"
# Follow-camera controls use the accepted UE runtime mesh orientation:
# +Y is visually aft, +X is visually right, +Z is up. Therefore a left-aft-up
# view uses positive BACK, negative RIGHT, and positive UP.
FOLLOW_CAMERA_BACK_CM="${FOLLOW_CAMERA_BACK_CM:-40}"
FOLLOW_CAMERA_RIGHT_CM="${FOLLOW_CAMERA_RIGHT_CM:--10}"
FOLLOW_CAMERA_UP_CM="${FOLLOW_CAMERA_UP_CM:-20}"
FOLLOW_CAMERA_PITCH_DEG="${FOLLOW_CAMERA_PITCH_DEG:--18}"
FOLLOW_CAMERA_OFFSET_CM="${FOLLOW_CAMERA_OFFSET_CM:-}"
EXPECTED_FIRST_X_M="${EXPECTED_FIRST_X_M:--55.33}"
EXPECTED_FIRST_Y_M="${EXPECTED_FIRST_Y_M:--24.23}"
EXPECTED_FIRST_Z_M="${EXPECTED_FIRST_Z_M:-1.90}"
EXPECTED_FIRST_YAW_RAD="${EXPECTED_FIRST_YAW_RAD:-0.0}"
LOG_PATH="${PROJECT_ROOT}/UE5/MoSimSceneLibrary/Saved/Logs/MoSimSceneLibrary.log"

cd "${PROJECT_ROOT}"

if [[ -z "${REPLAY_CSV:-}" ]]; then
  if [[ "${FOLLOW_UAV_CAMERA}" == "1" ]]; then
    REPLAY_CSV="${MWORKS_STATE_REPLAY_CSV}"
  else
    REPLAY_CSV="${VISUAL_GATE_REPLAY_CSV}"
  fi
fi

if [[ ! -f "${REPLAY_CSV}" ]]; then
  echo "Missing Factory UAV replay CSV: ${REPLAY_CSV}" >&2
  exit 3
fi

if [[ "${REPLAY_CSV}" == "${VISUAL_GATE_REPLAY_CSV}" ]]; then
python3 - <<PY
from pathlib import Path
import csv
import math
path = Path("${REPLAY_CSV}")
expected = (${EXPECTED_FIRST_X_M}, ${EXPECTED_FIRST_Y_M}, ${EXPECTED_FIRST_Z_M})
expected_yaw = float("${EXPECTED_FIRST_YAW_RAD}")
rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
if not rows:
    raise SystemExit(f"empty replay CSV: {path}")
first = rows[0]
actual = tuple(float(first[name]) for name in ("x", "y", "z"))
actual_yaw = float(first.get("yaw", "0.0"))
needs_write = False
if any(abs(a - e) > 1e-6 for a, e in zip(actual, expected)):
    print(f"Adjusting Factory review first frame from {actual} to {expected}; user gate requires UAV start at the accepted task start, while the review camera stays offset for manual movement.")
    for name, value in zip(("x", "y", "z"), expected):
        first[name] = f"{value:.5f}"
    if "x_ref" in first and "y_ref" in first and "z_ref" in first and len(rows) > 1:
        first["x_ref"] = rows[1].get("x", first["x_ref"])
        first["y_ref"] = rows[1].get("y", first["y_ref"])
        first["z_ref"] = rows[1].get("z", first["z_ref"])
    needs_write = True
if "yaw" in first and abs(actual_yaw - expected_yaw) > 1e-6:
    print(f"Adjusting Factory review first yaw from {actual_yaw:.6f} rad to {expected_yaw:.6f} rad; the vehicle visual gate uses neutral heading before replay/planner review.")
    first["yaw"] = f"{expected_yaw:.6f}"
    needs_write = True
if needs_write:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\\n")
        writer.writeheader()
        writer.writerows(rows)
PY
else
  echo "Using MWORKS/Sysplorer state replay for movement review: ${REPLAY_CSV}"
  echo "This is smoke-level MWORKS state playback, not final closed-loop product validation."
fi

python3 Scripts/UE5/activate_renderer_scene_source.py --scene-source-id "${SCENE_SOURCE_ID}"

if [[ "${STREAM_ONLY}" == "1" ]]; then
  OPEN_UE=0
fi

if [[ "${OPEN_UE}" == "1" ]]; then
  FOLLOW_CAMERA_ARGS=()
  if [[ "${FOLLOW_UAV_CAMERA}" == "1" ]]; then
    if [[ -n "${FOLLOW_CAMERA_OFFSET_CM}" ]]; then
      FOLLOW_CAMERA_ARGS=(
        "-MoSimFollowPlaybackCamera"
        "-MoSimFollowCameraOffset=${FOLLOW_CAMERA_OFFSET_CM}"
        "-MoSimFollowCameraPitch=${FOLLOW_CAMERA_PITCH_DEG}"
      )
    else
      FOLLOW_CAMERA_ARGS=(
        "-MoSimFollowPlaybackCamera"
        "-MoSimFollowCameraBackCm=${FOLLOW_CAMERA_BACK_CM}"
        "-MoSimFollowCameraRightCm=${FOLLOW_CAMERA_RIGHT_CM}"
        "-MoSimFollowCameraUpCm=${FOLLOW_CAMERA_UP_CM}"
        "-MoSimFollowCameraPitch=${FOLLOW_CAMERA_PITCH_DEG}"
      )
    fi
  fi
  UNREAL_EXTRA_ARGS="${MAP_PACKAGE} -MoSimDayReview -MoSimReviewCameraX=${REVIEW_CAMERA_X_CM} -MoSimReviewCameraY=${REVIEW_CAMERA_Y_CM} -MoSimReviewCameraZ=${REVIEW_CAMERA_Z_CM} -MoSimReviewCameraPitch=${REVIEW_CAMERA_PITCH_DEG} -MoSimReviewCameraYaw=${REVIEW_CAMERA_YAW_DEG} -MoSimReviewCameraRoll=${REVIEW_CAMERA_ROLL_DEG} ${FOLLOW_CAMERA_ARGS[*]}" \
    RESTART_UNREAL_GAME=1 \
    bash Scripts/UE5/open_unreal_renderer.sh simulation-review

  echo "Waiting for MoSimSceneLibrary UDP receiver on Windows port 5005..."
  UDP_READY=0
  for _ in $(seq 1 "${WAIT_UDP_SECONDS}"); do
    if powershell.exe -NoProfile -Command \
      "\$game = Get-CimInstance Win32_Process -Filter \"name = 'UnrealEditor.exe'\" | Where-Object { \$_.CommandLine -like '*MoSimSceneLibrary.uproject*' -and \$_.CommandLine -like '* -game*' } | Select-Object -First 1; if (-not \$game) { exit 1 }; \$udp = Get-NetUDPEndpoint -LocalPort 5005 -ErrorAction SilentlyContinue | Where-Object { \$_.OwningProcess -eq \$game.ProcessId } | Select-Object -First 1; if (\$udp) { exit 0 } else { exit 1 }" >/dev/null 2>&1; then
      UDP_READY=1
      break
    fi
    sleep 1
  done

  if [[ "${UDP_READY}" != "1" ]]; then
    echo "UE game window did not expose UDP 5005 within ${WAIT_UDP_SECONDS}s." >&2
    exit 4
  fi
fi

COMMON_ARGS=(
  "${REPLAY_CSV}"
  --host "${UNREAL_HOST}"
  --port 5005
  --scene-id "${SCENE_ID}_uav_platform_review"
  --map-id "${MAP_ID}"
  --coordinate-policy mworks_world_m_z_up
  --local-plan-source preview_from_reference
  --local-map-cells 0
  --lidar-point-limit 0
  --disable-visual-helpers
)

if [[ "${REVIEW_DRY_RUN}" == "1" || ( "${OPEN_UE}" != "1" && "${STREAM_ONLY}" != "1" ) ]]; then
  python3 Scripts/UE5/stream_unreal_udp.py "${COMMON_ARGS[@]}" \
    --dry-run --max-frames 3 --no-sleep
else
  STREAM_ARGS=(
    --fps "${STREAM_FPS}"
    --resample-hz "${STREAM_RESAMPLE_HZ}"
    --replay-speed "${STREAM_REPLAY_SPEED}"
    --print-every 20
  )
  if [[ "${STREAM_PATH_REPLAY}" == "1" ]]; then
    STREAM_ARGS+=(--loop --loop-count "${STREAM_LOOP_COUNT}")
  else
    STREAM_ARGS+=(--max-frames "${STREAM_MAX_FRAMES}")
  fi
  python3 Scripts/UE5/stream_unreal_udp.py "${COMMON_ARGS[@]}" "${STREAM_ARGS[@]}"
fi

echo "Factory UAV platform review stream complete."
if [[ "${FOLLOW_UAV_CAMERA}" == "1" ]]; then
  echo "Manual gate: review MWORKS/Sysplorer smoke state playback. Expect roll/pitch/yaw attitude changes from the CSV state source; do not accept pure path-point translation as simulation."
else
  echo "Manual gate: confirm the reference-colored Sunray150 body/propellers hold at the Factory review start; arrow keys orbit the UAV camera with fixed radius."
fi

if [[ -f "${LOG_PATH}" ]]; then
  echo "Recent UE diagnostic log lines:"
  grep -E "MoSim Sunray|Quadrotor MWORKS UDP first frame|MWORKS review camera active|MWORKS review camera following|MWORKS review camera follow orbit" "${LOG_PATH}" | tail -n 60 || true
fi
