#!/usr/bin/env bash
# Build the project-owned GPU ray PointCloud2 plugin in an isolated ROS1 overlay.

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_SOURCE_ROOT="${SUNRAY_SOURCE_ROOT:-${PROJECT_ROOT}/src/simulation/gazebo}"
GPU_LIVOX_PLUGIN_WS="${GPU_LIVOX_PLUGIN_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/gpu_livox_pointcloud_ws}"
LOG_PATH="${LOG_PATH:-${PROJECT_ROOT}/Results/sunray_ros1/gpu_livox_pointcloud_build.log}"

SRC_PKG="${SUNRAY_SOURCE_ROOT}/plugins/sunray/gpu_livox_pointcloud"
DST_PKG="${GPU_LIVOX_PLUGIN_WS}/src/mosim_gpu_livox_pointcloud"

if [[ ! -f "${SRC_PKG}/package.xml" || ! -f "${SRC_PKG}/CMakeLists.txt" ]]; then
  echo "GPU LiDAR plugin source is incomplete: ${SRC_PKG}" >&2
  exit 2
fi

mkdir -p "$(dirname "${LOG_PATH}")" "${GPU_LIVOX_PLUGIN_WS}/src" "${DST_PKG}"
# The A/B runner invokes this setup only after its source-content fingerprint
# changes. Do not retain an older source timestamp here: otherwise make can
# reuse a stale object file even though the copied source content changed.
cp -a --no-preserve=timestamps "${SRC_PKG}/." "${DST_PKG}/"

{
  echo "GPU_LIVOX_PLUGIN_WS=${GPU_LIVOX_PLUGIN_WS}"
  echo "SRC_PKG=${SRC_PKG}"
  echo "DST_PKG=${DST_PKG}"
  export PATH=/opt/ros/noetic/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/wsl/lib
  set +u
  source /usr/share/gazebo/setup.sh
  source /opt/ros/noetic/setup.bash
  set -u
  cd "${GPU_LIVOX_PLUGIN_WS}"
  catkin_make --only-pkg-with-deps mosim_gpu_livox_pointcloud -DCMAKE_BUILD_TYPE=Release
  test -f "${GPU_LIVOX_PLUGIN_WS}/devel/lib/libmosim_gpu_livox_pointcloud.so"
  ldd "${GPU_LIVOX_PLUGIN_WS}/devel/lib/libmosim_gpu_livox_pointcloud.so" | grep -E "GpuRayPlugin|gazebo|roscpp" || true
} > "${LOG_PATH}" 2>&1

echo "${GPU_LIVOX_PLUGIN_WS}"
