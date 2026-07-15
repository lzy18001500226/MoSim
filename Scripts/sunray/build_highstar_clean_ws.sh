#!/usr/bin/env bash
# Build a clean, persistent HighStar ROS1 workspace for MoSim Factory probes.

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
HIGHSTAR_SRC="${HIGHSTAR_SRC:-${PROJECT_ROOT}/References/Lab/exploration_coverage/HighStar}"
HIGHSTAR_WS="${HIGHSTAR_WS:-/opt/mosim_work/sunray_ws/highstar_clean_ws_20260708_current}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/build/highstar_clean_ws_20260708_current}"
CATKIN_SIMPLE_SRC="${CATKIN_SIMPLE_SRC:-${PROJECT_ROOT}/References/Lab/planning_local/Fast-Drone-250/src/utils/catkin_simple}"
MAV_MSGS_SRC="${MAV_MSGS_SRC:-${PROJECT_ROOT}/References/Lab/exploration_coverage/3dmr/exploration_ws/src/mav_comm/mav_msgs}"
BUILD_JOBS="${BUILD_JOBS:-2}"

mkdir -p "${RESULT_DIR}"

if [[ ! -d "${HIGHSTAR_SRC}" ]]; then
  echo "HighStar source missing: ${HIGHSTAR_SRC}" >&2
  exit 2
fi
if [[ ! -f "${CATKIN_SIMPLE_SRC}/package.xml" ]]; then
  echo "catkin_simple source missing: ${CATKIN_SIMPLE_SRC}" >&2
  exit 2
fi
if [[ ! -f "${MAV_MSGS_SRC}/package.xml" ]]; then
  echo "mav_msgs source missing: ${MAV_MSGS_SRC}" >&2
  exit 2
fi

mkdir -p "${HIGHSTAR_WS}/src"

set +u
source /opt/ros/noetic/setup.bash
set -u

if [[ ! -f "${HIGHSTAR_WS}/src/CMakeLists.txt" ]]; then
  (cd "${HIGHSTAR_WS}/src" && catkin_init_workspace)
fi

link_pkg() {
  local src="$1"
  local name="$2"
  local dst="${HIGHSTAR_WS}/src/${name}"
  if [[ -L "${dst}" || -d "${dst}" ]]; then
    return
  fi
  ln -s "${src}" "${dst}"
}

while IFS= read -r pkg_xml; do
  pkg_dir="$(dirname "${pkg_xml}")"
  pkg_name="$(basename "${pkg_dir}")"
  link_pkg "${pkg_dir}" "${pkg_name}"
done < <(find "${HIGHSTAR_SRC}" -mindepth 2 -maxdepth 4 -name package.xml | sort)

link_pkg "${CATKIN_SIMPLE_SRC}" "catkin_simple"
link_pkg "${MAV_MSGS_SRC}" "mav_msgs"

create_system_lib_shim() {
  local name="$1"
  local header="$2"
  local lib="$3"
  local catkin_dep="${4:-}"
  local shim_dir="${HIGHSTAR_WS}/src/${name}"
  mkdir -p "${shim_dir}/src"
  cat > "${shim_dir}/src/dependency_tracker.cc" <<EOF
namespace ${name}_shim {
void dependency_tracker() {}
}
EOF
  cat > "${shim_dir}/package.xml" <<EOF
<?xml version="1.0"?>
<package format="2">
  <name>${name}</name>
  <version>0.0.1</version>
  <description>Local shim for system ${name} used by HighStar build probes.</description>
  <maintainer email="local@example.com">MoSim</maintainer>
  <license>BSD</license>
  <buildtool_depend>catkin</buildtool_depend>
  <build_depend>roscpp</build_depend>
  <exec_depend>roscpp</exec_depend>
  ${catkin_dep}
</package>
EOF
  cat > "${shim_dir}/CMakeLists.txt" <<EOF
cmake_minimum_required(VERSION 3.0.2)
project(${name})

find_package(catkin REQUIRED${catkin_dep:+ COMPONENTS gflags_catkin})
find_path(${name}_INCLUDE_DIR ${header} REQUIRED)
find_library(${name}_LIBRARY NAMES ${lib} REQUIRED)

add_library(\${PROJECT_NAME} SHARED src/dependency_tracker.cc)
target_include_directories(\${PROJECT_NAME} PUBLIC \${${name}_INCLUDE_DIR})
target_link_libraries(\${PROJECT_NAME} \${${name}_LIBRARY} \${catkin_LIBRARIES})

catkin_package(
  INCLUDE_DIRS \${${name}_INCLUDE_DIR}
  LIBRARIES \${PROJECT_NAME}
  ${catkin_dep:+CATKIN_DEPENDS gflags_catkin}
)
EOF
}

create_system_lib_shim "gflags_catkin" "gflags/gflags.h" "gflags"
create_system_lib_shim "glog_catkin" "glog/logging.h" "glog" "<build_depend>gflags_catkin</build_depend><exec_depend>gflags_catkin</exec_depend>"

{
  echo "workspace=${HIGHSTAR_WS}"
  echo "source=${HIGHSTAR_SRC}"
  echo "catkin_simple=${CATKIN_SIMPLE_SRC}"
  echo "mav_msgs=${MAV_MSGS_SRC}"
  echo "started_at=$(date --iso-8601=seconds)"
} > "${RESULT_DIR}/build_manifest.txt"
find "${HIGHSTAR_WS}/src" -maxdepth 1 -mindepth 1 -printf '%p\n' | sort > "${RESULT_DIR}/package_list.txt"

cd "${HIGHSTAR_WS}"
set +e
catkin_make -DCMAKE_BUILD_TYPE=Release -j"${BUILD_JOBS}" > "${RESULT_DIR}/catkin_make.log" 2>&1
build_rc=$?
set -e
echo "${build_rc}" > "${RESULT_DIR}/build_exit_code.txt"
if [[ "${build_rc}" -ne 0 ]]; then
  tail -120 "${RESULT_DIR}/catkin_make.log" >&2 || true
  exit "${build_rc}"
fi

find "${HIGHSTAR_WS}/devel" -maxdepth 4 \
  \( -name murder_node -o -name traj_exc_node -o -name libmurder.so -o -name libfrontier_grid.so -o -name libmurder_fsm.so \) \
  -printf '%TY-%Tm-%Td %TH:%TM:%TS %s %p\n' | sort > "${RESULT_DIR}/binary_timestamps.txt"
echo "source ${HIGHSTAR_WS}/devel/setup.bash" > "${RESULT_DIR}/source_setup_hint.txt"
echo "${HIGHSTAR_WS}" > "${RESULT_DIR}/workspace_path.txt"
cat "${RESULT_DIR}/binary_timestamps.txt"
