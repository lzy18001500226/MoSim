#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
cd "${PROJECT_ROOT}"

# This wrapper opens native runtime review surfaces only.
# UE is the rendered-scene window; RViz2 is the point-cloud/map window.
# RVIZ_PROFILE=split opens separate planning-grid and point-cloud RViz2 windows.
# Browser HTML is not used.

SCENE_ID=factoryenvironmentcollect
START_UE=${START_UE:-1}
START_RVIZ=${START_RVIZ:-1}
START_FASTLIO=${START_FASTLIO:-1}
RECORD_FASTLIO=${RECORD_FASTLIO:-0}
WAIT_FOR_WINDOWS=${WAIT_FOR_WINDOWS:-1}
FASTLIO_ROS2_LAUNCH_CMD=${FASTLIO_ROS2_LAUNCH_CMD:-"set +u; source /opt/ros/humble/setup.bash; source ${PROJECT_ROOT}/Results/tmp/spark_fast_lio_ros2_ws/install/livox_ros_driver2/share/livox_ros_driver2/local_setup.bash; source ${PROJECT_ROOT}/Results/tmp/fast_lio_ros2_import_ws/install/fast_lio/share/fast_lio/local_setup.bash; source ${PROJECT_ROOT}/Results/tmp/mosim_dense_lidar_cpp_ws/install/mosim_dense_lidar_cpp/share/mosim_dense_lidar_cpp/local_setup.bash; ros2 launch fast_lio mapping.launch.py rviz:=false config_path:=${PROJECT_ROOT}/Config/ros2 config_file:=mosim_fast_lio_ros2_mid360.yaml"}
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
  OPEN_UE=1 OPEN_RVIZ=0 STREAM_LOOP_COUNT=1 STREAM_FPS=12 WAIT_UDP_SECONDS=45 Scripts/UE5/review_scene_mapping_loop.sh factoryenvironmentcollect &
  PIDS+=("$!")
fi

if [[ "${START_RVIZ}" == "1" && "${START_FASTLIO}" != "1" ]]; then
  RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros2.sh factoryenvironmentcollect &
  PIDS+=("$!")
fi

if [[ "${START_FASTLIO}" == "1" ]]; then
  FASTLIO_ROS2_LAUNCH_CMD="${FASTLIO_ROS2_LAUNCH_CMD}" \
    START_FASTLIO=1 START_RVIZ="${START_RVIZ}" RVIZ_PROFILE=split \
    Scripts/UE5/run_fastlio_rviz_replay_ros2.sh factoryenvironmentcollect &
  PIDS+=("$!")
fi

if [[ "${RECORD_FASTLIO}" == "1" ]]; then
  echo "FAST-LIO recording/evaluation is only valid after a real FAST-LIO runtime publishes output topics." >&2
  python3 Scripts/UE5/record_fastlio_ros2_runtime.py --scene-id factoryenvironmentcollect --output-dir Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_manual_review --duration-seconds 20
  python3 Scripts/UE5/evaluate_fastlio_runtime.py --scene-id factoryenvironmentcollect --truth-dataset Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_mworks_truth_dataset.jsonl --odometry-jsonl Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_manual_review/fastlio_odometry.jsonl --output-json Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_manual_review/FASTLIO_RUNTIME_EVALUATION.json --output-md Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_manual_review/FASTLIO_RUNTIME_EVALUATION.md --fail-on-threshold
fi

if [[ "${WAIT_FOR_WINDOWS}" == "1" ]]; then
  wait_for_background
fi
