#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
cd "${PROJECT_ROOT}"

# This wrapper opens native runtime review surfaces only.
# UE is the rendered-scene window; RViz is the point-cloud/map window.
# RVIZ_PROFILE=split opens separate planning-grid and point-cloud RViz windows.
# Browser HTML is not used.

SCENE_ID=derelictcorridormegascans
START_UE=${START_UE:-1}
START_RVIZ=${START_RVIZ:-1}
START_FASTLIO=${START_FASTLIO:-0}
RECORD_FASTLIO=${RECORD_FASTLIO:-0}
WAIT_FOR_WINDOWS=${WAIT_FOR_WINDOWS:-1}
PIDS=()

wait_for_background() {
  local status=0
  for pid in "${PIDS[@]:-}"; do
    if ! wait "${pid}"; then
      status=1
    fi
  done
  return "${status}"
}

if [[ "${START_UE}" == "1" ]]; then
  OPEN_UE=1 OPEN_RVIZ=0 STREAM_LOOP_COUNT=1 STREAM_FPS=12 WAIT_UDP_SECONDS=45 Scripts/UE5/review_scene_mapping_loop.sh derelictcorridormegascans &
  PIDS+=("$!")
fi

if [[ "${START_RVIZ}" == "1" ]]; then
  RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros1.sh derelictcorridormegascans &
  PIDS+=("$!")
fi

if [[ "${START_FASTLIO}" == "1" ]]; then
  Scripts/UE5/run_fastlio_rviz_replay_ros1.sh derelictcorridormegascans &
  PIDS+=("$!")
fi

if [[ "${RECORD_FASTLIO}" == "1" ]]; then
  python3 Scripts/UE5/record_fastlio_ros1_runtime.py --scene-id derelictcorridormegascans --output-dir Results/unreal_scene_mapping/derelictcorridormegascans/fastlio_runtime --duration-seconds 20
  python3 Scripts/UE5/evaluate_fastlio_runtime.py --scene-id derelictcorridormegascans --truth-dataset Results/unreal_scene_mapping/derelictcorridormegascans/fastlio_replay_dataset.jsonl --odometry-jsonl Results/unreal_scene_mapping/derelictcorridormegascans/fastlio_runtime/fastlio_odometry.jsonl --output-json Results/unreal_scene_mapping/derelictcorridormegascans/fastlio_runtime/FASTLIO_RUNTIME_EVALUATION.json --output-md Results/unreal_scene_mapping/derelictcorridormegascans/fastlio_runtime/FASTLIO_RUNTIME_EVALUATION.md --fail-on-threshold
fi

if [[ "${WAIT_FOR_WINDOWS}" == "1" ]]; then
  wait_for_background
fi
