#!/usr/bin/env bash
# Factory L2 single-UAV Diff fixed-goal gate with the GPU PointCloud2 backend.

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
GPU_LIVOX_PLUGIN_WS="${GPU_LIVOX_PLUGIN_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/gpu_livox_pointcloud_ws}"

exec env \
  SUNRAY_MID360_RAY_BACKEND=gpu \
  GPU_LIVOX_PLUGIN_WS="${GPU_LIVOX_PLUGIN_WS}" \
  SUNRAY_LIVOX_PLUGIN_FILENAME="${GPU_LIVOX_PLUGIN_WS}/devel/lib/libmosim_gpu_livox_pointcloud.so" \
  bash "${PROJECT_ROOT}/Scripts/sunray/run_factory_l2_diff_single_c99_gate.sh" "$@"
