#!/usr/bin/env bash
set -euo pipefail

# Prepare and optionally launch the manual review loop for one accepted UE scene:
# real rendered map + UAV UDP playback + radar/local-plan debug overlay. The
# separate point-cloud/map windows are RViz2 via open_mapping_rviz_ros2.sh, not
# browser HTML. Use RVIZ_PROFILE=split to open grid/planning and point-cloud
# views as separate RViz2 windows.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
SCENE_ID="${1:-factoryenvironmentcollect}"
OUTPUT_ROOT="${OUTPUT_ROOT:-${PROJECT_ROOT}/Results/unreal_scene_mapping}"
UNREAL_HOST="${UNREAL_HOST:-$(ip route | awk '/^default/ {print $3; exit}')}"
OPEN_UE="${OPEN_UE:-1}"
OPEN_RVIZ="${OPEN_RVIZ:-0}"
REGENERATE="${REGENERATE:-0}"
REVIEW_DRY_RUN="${REVIEW_DRY_RUN:-0}"
STREAM_FPS="${STREAM_FPS:-12}"
STREAM_REPLAY_SPEED="${STREAM_REPLAY_SPEED:-1.0}"
STREAM_LOOP_COUNT="${STREAM_LOOP_COUNT:-3}"
WAIT_UDP_SECONDS="${WAIT_UDP_SECONDS:-60}"

cd "${PROJECT_ROOT}"

case "${SCENE_ID}" in
  factoryenvironmentcollect|FactoryEnvironmentCollect|factory)
    SCENE_ID="factoryenvironmentcollect"
    SCENE_SOURCE_ID="local_factoryenvironmentcollect"
    MAP_PACKAGE="/Game/Maps/Demonstration"
    MAP_ID="local_factoryenvironmentcollect"
    ;;
  derelictcorridormegascans|DerelictCorridorMegascans|derelict)
    SCENE_ID="derelictcorridormegascans"
    SCENE_SOURCE_ID="local_derelictcorridormegascans"
    MAP_PACKAGE="/Game/DerelictCorridor/Maps/DerelictCorridor"
    MAP_ID="local_derelictcorridormegascans"
    ;;
  *)
    echo "Unsupported scene: ${SCENE_ID}" >&2
    echo "Use factoryenvironmentcollect or derelictcorridormegascans." >&2
    exit 2
    ;;
esac

SCENE_DIR="${OUTPUT_ROOT}/${SCENE_ID}"
REPLAY_CSV="${SCENE_DIR}/render_replay.csv"
FASTLIO_HANDOFF="${SCENE_DIR}/fastlio_handoff.json"
LOCAL_KNOWN_MAP="${SCENE_DIR}/local_known_map_frames.jsonl"
LOCAL_PLAN_FRAMES="${SCENE_DIR}/local_plan_frames.jsonl"
LIDAR_POINT_FRAMES="${SCENE_DIR}/lidar_point_frames.jsonl"
FASTLIO_REPLAY_DATASET="${SCENE_DIR}/fastlio_replay_dataset.jsonl"
FASTLIO_ADAPTER_MANIFEST="${SCENE_DIR}/fastlio_adapter_manifest.json"
PLANNER_SUMMARY="${SCENE_DIR}/planner_summary.json"
REVIEW_PACKET="${SCENE_DIR}/manual_review_packet.md"

if [[ "${REGENERATE}" == "1" || ! -f "${REPLAY_CSV}" || ! -f "${FASTLIO_HANDOFF}" ]]; then
  python3 Scripts/UE5/scene_truth_pipeline.py --scene "${SCENE_ID}" --output-root "${OUTPUT_ROOT}"
fi

if [[ "${REGENERATE}" == "1" || ! -f "${FASTLIO_REPLAY_DATASET}" || ! -f "${FASTLIO_ADAPTER_MANIFEST}" ]]; then
  python3 Scripts/UE5/prepare_fastlio_replay.py --scene "${SCENE_ID}" --output-root "${OUTPUT_ROOT}"
fi

for Required in "${REPLAY_CSV}" "${FASTLIO_HANDOFF}" "${LOCAL_KNOWN_MAP}" "${LOCAL_PLAN_FRAMES}" "${LIDAR_POINT_FRAMES}" "${FASTLIO_REPLAY_DATASET}" "${FASTLIO_ADAPTER_MANIFEST}" "${PLANNER_SUMMARY}"; do
  if [[ ! -f "${Required}" ]]; then
    echo "Missing required review artifact: ${Required}" >&2
    exit 3
  fi
done

python3 Scripts/UE5/activate_renderer_scene_source.py --scene-source-id "${SCENE_SOURCE_ID}"

python3 - "${SCENE_ID}" "${SCENE_SOURCE_ID}" "${MAP_PACKAGE}" "${REPLAY_CSV}" "${FASTLIO_HANDOFF}" "${LOCAL_KNOWN_MAP}" "${LOCAL_PLAN_FRAMES}" "${LIDAR_POINT_FRAMES}" "${FASTLIO_ADAPTER_MANIFEST}" "${PLANNER_SUMMARY}" "${REVIEW_PACKET}" <<'PY'
import json
import sys
from pathlib import Path

scene_id, scene_source_id, map_package, replay_csv, fastlio, local_known_map, local_plan_frames, lidar_point_frames, fastlio_adapter, summary, packet = sys.argv[1:]
summary_data = json.loads(Path(summary).read_text(encoding="utf-8"))
handoff = json.loads(Path(fastlio).read_text(encoding="utf-8"))
adapter = json.loads(Path(fastlio_adapter).read_text(encoding="utf-8"))
lines = [
    f"# Manual Review Packet: {scene_id}",
    "",
    "Review target:",
    f"- Scene source: `{scene_source_id}`",
    f"- UE map: `{map_package}`",
    f"- UAV replay CSV: `{replay_csv}`",
    f"- FAST-LIO handoff: `{fastlio}`",
    f"- FAST-LIO adapter manifest: `{fastlio_adapter}`",
    f"- Local-known-map replay: `{local_known_map}`",
    f"- Local-plan replay: `{local_plan_frames}`",
    f"- UE LiDAR point replay: `{lidar_point_frames}`",
    "",
    "Expected evidence:",
    "- The UE window shows the accepted real rendered scene, not the old STL/blockout preview.",
    "- A blue UAV body moves inside the map, with propellers, trajectory trail, radar sector, reference marker, local-plan spline, and optional local-known-map debug cells.",
    "- If separate map windows are required, open RViz2 with `RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros2.sh`; browser HTML is not the primary review route.",
    "- The planner did not receive the global truth map as a prior.",
    "- Collision validation against exported UE truth is true.",
    "",
    "Planner summary:",
    f"- policy: `{summary_data.get('planner_policy')}`",
    f"- path_cells: `{summary_data.get('path_cells')}`",
    f"- replans: `{summary_data.get('replan_count')}`",
    f"- lidar_points: `{summary_data.get('merged_lidar_point_count')}`",
    f"- global_truth_available_to_planner: `{summary_data.get('global_truth_available_to_planner')}`",
    f"- collision_free_against_truth: `{summary_data.get('collision_free_against_truth')}`",
    "",
    "FAST-LIO status:",
    f"- `{handoff.get('status')}`",
    f"- adapter: `{adapter.get('status')}`",
    "- This is still an input handoff/adapter, not a completed FAST-LIO localization result.",
    "",
    "Reject if:",
    "- The scene is black/white/blank, loaded outside the accepted map, or clearly shows the old generated preview map.",
    "- The UAV path starts outside the usable map, visibly clips through walls, or the overlay is absent.",
    "- The RViz/native point-cloud window has zero/obviously wrong points when native map review is requested.",
]
Path(packet).write_text("\n".join(lines) + "\n", encoding="utf-8")
print(packet)
PY

if [[ "${OPEN_RVIZ}" == "1" ]]; then
  RVIZ_PROFILE="${RVIZ_PROFILE:-split}" Scripts/UE5/open_mapping_rviz_ros2.sh "${SCENE_ID}" &
fi

if [[ "${OPEN_UE}" != "1" ]]; then
  echo "Prepared ${REVIEW_PACKET}"
  exit 0
fi

UNREAL_EXTRA_ARGS="${MAP_PACKAGE}" RESTART_UNREAL_GAME=1 bash Scripts/UE5/open_unreal_renderer.sh simulation-review

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
  echo "Review packet prepared at ${REVIEW_PACKET}" >&2
  exit 4
fi

if [[ "${REVIEW_DRY_RUN}" == "1" ]]; then
  python3 Scripts/UE5/stream_unreal_udp.py "${REPLAY_CSV}" \
    --host "${UNREAL_HOST}" \
    --port 5005 \
    --scene-id "${SCENE_ID}_mapping_replay" \
    --map-id "${MAP_ID}" \
    --local-plan-source evidence_backed_scene_truth_pipeline \
    --coordinate-policy ue_world_m_z_up \
    --local-known-map-jsonl "${LOCAL_KNOWN_MAP}" \
    --local-plan-jsonl "${LOCAL_PLAN_FRAMES}" \
    --lidar-point-frames-jsonl "${LIDAR_POINT_FRAMES}" \
    --dry-run --max-frames 2 --no-sleep
else
  python3 Scripts/UE5/stream_unreal_udp.py "${REPLAY_CSV}" \
    --host "${UNREAL_HOST}" \
    --port 5005 \
    --scene-id "${SCENE_ID}_mapping_replay" \
    --map-id "${MAP_ID}" \
    --fps "${STREAM_FPS}" \
    --replay-speed "${STREAM_REPLAY_SPEED}" \
    --local-plan-source evidence_backed_scene_truth_pipeline \
    --coordinate-policy ue_world_m_z_up \
    --local-known-map-jsonl "${LOCAL_KNOWN_MAP}" \
    --local-plan-jsonl "${LOCAL_PLAN_FRAMES}" \
    --lidar-point-frames-jsonl "${LIDAR_POINT_FRAMES}" \
    --loop --loop-count "${STREAM_LOOP_COUNT}" \
    --print-every 20
fi

echo "Manual review packet: ${REVIEW_PACKET}"
