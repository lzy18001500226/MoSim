#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FALCON_ROOT="${ROOT_DIR}/src/planning/falcon"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="${1:-${ROOT_DIR}/Results/sunray_ros1/falcon_f1_preflight_${STAMP}}"
mkdir -p "${OUT_DIR}"

{
  echo "{"
  echo "  \"status\": \"preflight_collected\","
  echo "  \"root_dir\": \"${ROOT_DIR}\","
  echo "  \"falcon_root\": \"${FALCON_ROOT}\","
  echo "  \"timestamp\": \"${STAMP}\","
  echo "  \"checks\": {"

  set +u
  source /opt/ros/noetic/setup.bash 2>/dev/null || true
  set -u

  cmake_line="$(cmake --version 2>/dev/null | head -n 1 || true)"
  cmake_version="$(printf '%s' "${cmake_line}" | awk '{print $3}')"
  ros_distro="${ROS_DISTRO:-}"
  roslaunch_path="$(command -v roslaunch || true)"
  catkin_make_path="$(command -v catkin_make || true)"
  roscore_path="$(command -v roscore || true)"
  nvcc_path="$(command -v nvcc || true)"
  nvcc_version="$(nvcc --version 2>/dev/null | tail -n 1 || true)"
  lkh_path="$(command -v LKH || true)"
  package_count="$(find "${FALCON_ROOT}" -name package.xml 2>/dev/null | wc -l | tr -d ' ')"

  printf '    "ros_distro": "%s",\n' "${ros_distro}"
  printf '    "roslaunch": "%s",\n' "${roslaunch_path}"
  printf '    "catkin_make": "%s",\n' "${catkin_make_path}"
  printf '    "roscore": "%s",\n' "${roscore_path}"
  printf '    "cmake_version": "%s",\n' "${cmake_version}"
  printf '    "cmake_min_3_20": "%s",\n' "$(python3 - "${cmake_version}" <<'PY'
import sys
from distutils.version import LooseVersion
v = sys.argv[1] or "0"
print(str(LooseVersion(v) >= LooseVersion("3.20")).lower())
PY
)"
  printf '    "nlopt_pkg_config": "%s",\n' "$(pkg-config --modversion nlopt 2>/dev/null || true)"
  printf '    "nlopt_ldconfig": "%s",\n' "$(ldconfig -p 2>/dev/null | grep -i nlopt | head -n 1 | sed 's/"/\\"/g' || true)"
  printf '    "open3d_ldconfig": "%s",\n' "$(ldconfig -p 2>/dev/null | grep -i open3d | head -n 1 | sed 's/"/\\"/g' || true)"
  printf '    "nvcc": "%s",\n' "${nvcc_path}"
  printf '    "nvcc_version": "%s",\n' "${nvcc_version}"
  printf '    "lkh": "%s",\n' "${lkh_path}"

  for pkg in libgoogle-glog-dev libarmadillo-dev libdw-dev libdwarf-dev libc++-dev libc++abi-dev; do
    status="$(dpkg-query -W -f='${Status}' "${pkg}" 2>/dev/null || true)"
    printf '    "%s": "%s",\n' "${pkg}" "${status}"
  done

  printf '    "package_xml_count": "%s"\n' "${package_count}"
  echo "  }"
  echo "}"
} > "${OUT_DIR}/FALCON_F1_PREFLIGHT.json"

cat > "${OUT_DIR}/SUMMARY.md" <<EOF
# FALCON F1 Dependency Preflight

Status: \`preflight_collected\`

This packet is read-only. It does not install dependencies, build FALCON, or
start Gazebo/PX4/MAVROS/RViz.

Key result file: \`FALCON_F1_PREFLIGHT.json\`
EOF

echo "{\"status\":\"preflight_collected\",\"out_dir\":\"${OUT_DIR}\"}"
