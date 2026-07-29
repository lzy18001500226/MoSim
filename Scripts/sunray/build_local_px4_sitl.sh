#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: build_local_px4_sitl.sh [--configure | --build | --plugins-only] [options]

Build the project-local PX4 SITL source without starting PX4 or Gazebo.

Options:
  --configure              Configure only (default).
  --build                  Configure, then build PX4 and the required Gazebo
                           Classic plugin bundle by default.
  --plugins-only           Reuse an existing validated PX4 build directory and
                           build only the required Gazebo Classic plugins.
  --bootstrap-python       Install the PX4 Kconfig Python package into the
                           project build tree before configuring.
  --target <name>          CMake target to build (default: px4).
  --jobs <count>           Parallel build jobs (default: 2).
  --skip-gazebo-classic-plugins
                           Do not build the Gazebo Classic plugin subproject.
  --build-dir <relative>   Project-relative directory below build/px4/
                           (default: build/px4/px4_sitl_default).
  --help                   Show this help text.
EOF
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 2
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PX4_SOURCE_DIR="${PROJECT_ROOT}/src/flight_stack/px4/PX4-Autopilot"
BUILD_RELATIVE_DIR="build/px4/px4_sitl_default"
BUILD_TARGET="px4"
BUILD_JOBS=2
ACTION="configure"
BOOTSTRAP_PYTHON=0
BUILD_GAZEBO_CLASSIC_PLUGINS="${PX4_BUILD_GAZEBO_CLASSIC_PLUGINS:-true}"
PX4_BOOTSTRAP_PACKAGES=(kconfiglib future)

while [[ $# -gt 0 ]]; do
  case "$1" in
    --configure)
      ACTION="configure"
      ;;
    --build)
      ACTION="build"
      ;;
    --plugins-only)
      ACTION="plugins_only"
      ;;
    --bootstrap-python)
      BOOTSTRAP_PYTHON=1
      ;;
    --target)
      [[ $# -ge 2 ]] || die "--target requires a value"
      BUILD_TARGET="$2"
      shift
      ;;
    --jobs)
      [[ $# -ge 2 ]] || die "--jobs requires a value"
      BUILD_JOBS="$2"
      shift
      ;;
    --skip-gazebo-classic-plugins)
      BUILD_GAZEBO_CLASSIC_PLUGINS="false"
      ;;
    --build-dir)
      [[ $# -ge 2 ]] || die "--build-dir requires a value"
      BUILD_RELATIVE_DIR="$2"
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      die "unknown option: $1"
      ;;
  esac
  shift
done

[[ "$BUILD_JOBS" =~ ^[1-9][0-9]*$ ]] || die "--jobs must be a positive integer"
[[ "$BUILD_RELATIVE_DIR" == build/px4/* ]] || die "--build-dir must remain below build/px4/"
[[ -f "${PX4_SOURCE_DIR}/CMakeLists.txt" ]] || die "project-local PX4 source is missing: ${PX4_SOURCE_DIR}"
[[ -d "${PX4_SOURCE_DIR}/Tools/simulation/gazebo-classic/sitl_gazebo-classic" ]] || die "PX4 Gazebo Classic source is missing"

BUILD_DIR="${PROJECT_ROOT}/${BUILD_RELATIVE_DIR}"
BUILD_ROOT="${PROJECT_ROOT}/build/px4"
PYTHON_DEPS_DIR="${PROJECT_ROOT}/build/px4/python_deps"
ROS_PYTHON_DIST_PACKAGES="/opt/ros/noetic/lib/python3/dist-packages"
BUILD_ROOT_REAL="$(realpath -m "${BUILD_ROOT}")"
BUILD_DIR_REAL="$(realpath -m "${BUILD_DIR}")"
PYTHON_DEPS_DIR_REAL="$(realpath -m "${PYTHON_DEPS_DIR}")"
case "${BUILD_DIR_REAL}" in
  "${BUILD_ROOT_REAL}"/*) ;;
  *) die "resolved build directory escapes build/px4/: ${BUILD_DIR_REAL}" ;;
esac

sanitize_px4_build_environment() {
  unset CMAKE_PREFIX_PATH CMAKE_MODULE_PATH CMAKE_TOOLCHAIN_FILE CMAKE_GENERATOR
  unset CONDA_PREFIX CONDA_DEFAULT_ENV CONDA_EXE CONDA_PYTHON_EXE
  unset LD_LIBRARY_PATH PKG_CONFIG_PATH PYTHONHOME PYTHONPATH
  export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/wsl/lib"
}

# Clear persistent host-IDE package roots before configuring an existing build
# directory. The PX4 build must resolve its CMake packages from Ubuntu, not a
# Windows Anaconda installation mounted by WSL.
CMAKE_SYSTEM_PACKAGE_RESET_ARGS=(
  -UGTest_DIR
  -UProtobuf_DIR
  -Uabsl_DIR
  -Uutf8_range_DIR
)

sanitize_px4_build_environment
command -v cmake >/dev/null || die "cmake is not available"
command -v ninja >/dev/null || die "ninja is not available"
command -v python3 >/dev/null || die "python3 is not available"
[[ -d "${ROS_PYTHON_DIST_PACKAGES}" ]] || die "ROS Noetic Python packages are missing: ${ROS_PYTHON_DIST_PACKAGES}"

mkdir -p "${BUILD_DIR_REAL}"
mkdir -p "${PYTHON_DEPS_DIR_REAL}"
export PYTHONPATH="${PYTHON_DEPS_DIR_REAL}:${ROS_PYTHON_DIST_PACKAGES}"

if [[ "${BOOTSTRAP_PYTHON}" == "1" ]]; then
  command -v pip3 >/dev/null || die "pip3 is required for --bootstrap-python"
  printf 'PYTHON_BOOTSTRAP_COMMAND=python3 -m pip install --disable-pip-version-check --no-cache-dir --target %q kconfiglib future\n' "${PYTHON_DEPS_DIR_REAL}"
  python3 -m pip install --disable-pip-version-check --no-cache-dir --target "${PYTHON_DEPS_DIR_REAL}" "${PX4_BOOTSTRAP_PACKAGES[@]}"
fi

if ! python3 -c "import menuconfig, defconfig, genconfig, genmsg, future; from future import standard_library"; then
	printf 'PX4_PYTHON_REQUIREMENTS=%s\n' "${PX4_SOURCE_DIR}/Tools/setup/requirements.txt" >&2
	printf 'PX4_PYTHON_DEPS=%s\n' "${PYTHON_DEPS_DIR_REAL}" >&2
	printf 'ROS_PYTHON_DIST_PACKAGES=%s\n' "${ROS_PYTHON_DIST_PACKAGES}" >&2
	printf 'PYTHON_BOOTSTRAP_COMMAND=%s --bootstrap-python\n' "${BASH_SOURCE[0]}" >&2
	die "required PX4 or ROS Python modules are missing; run the explicit bootstrap command above"
fi

printf 'PX4_SOURCE=%s\n' "${PX4_SOURCE_DIR}"
printf 'PX4_BUILD=%s\n' "${BUILD_DIR_REAL}"
printf 'PX4_PYTHON_DEPS=%s\n' "${PYTHON_DEPS_DIR_REAL}"
printf 'PX4_CONFIG=px4_sitl_default\n'
if [[ "${ACTION}" == "plugins_only" ]]; then
  [[ -s "${BUILD_DIR_REAL}/CMakeCache.txt" ]] || die "--plugins-only requires an existing PX4 CMakeCache.txt"
  [[ -s "${BUILD_DIR_REAL}/build.ninja" ]] || die "--plugins-only requires an existing PX4 build.ninja"
  [[ -x "${BUILD_DIR_REAL}/bin/px4" ]] || die "--plugins-only requires an existing PX4 executable"
  grep -Fqx "CMAKE_HOME_DIRECTORY:INTERNAL=${PX4_SOURCE_DIR}" "${BUILD_DIR_REAL}/CMakeCache.txt" \
    || die "--plugins-only PX4 cache does not belong to the project-local source"
  printf 'PX4_TOP_LEVEL_CONFIGURE=REUSED\n'
else
  printf 'CONFIGURE_COMMAND=cmake -S %q -B %q -GNinja -DCONFIG=px4_sitl_default' "${PX4_SOURCE_DIR}" "${BUILD_DIR_REAL}"
  printf ' %q' "${CMAKE_SYSTEM_PACKAGE_RESET_ARGS[@]}"
  printf '\n'
  cmake -S "${PX4_SOURCE_DIR}" -B "${BUILD_DIR_REAL}" -GNinja -DCONFIG=px4_sitl_default \
    "${CMAKE_SYSTEM_PACKAGE_RESET_ARGS[@]}"
fi

if [[ "${ACTION}" == "build" ]]; then
  printf 'BUILD_COMMAND=cmake --build %q --target %q -- -j%s\n' "${BUILD_DIR_REAL}" "${BUILD_TARGET}" "${BUILD_JOBS}"
  cmake --build "${BUILD_DIR_REAL}" --target "${BUILD_TARGET}" -- -j"${BUILD_JOBS}"
fi

if [[ "${ACTION}" == "build" || "${ACTION}" == "plugins_only" ]]; then
  if [[ "${BUILD_GAZEBO_CLASSIC_PLUGINS}" == "true" ]]; then
    GAZEBO_CLASSIC_SOURCE_DIR="${PX4_SOURCE_DIR}/Tools/simulation/gazebo-classic/sitl_gazebo-classic"
    GAZEBO_CLASSIC_BUILD_DIR="${BUILD_DIR_REAL}/build_gazebo-classic"
    GAZEBO_CLASSIC_PLUGIN_TARGETS=(
      gazebo_gps_plugin
      gazebo_groundtruth_plugin
      gazebo_imu_plugin
      gazebo_mavlink_interface
      gazebo_magnetometer_plugin
      gazebo_barometer_plugin
      gazebo_motor_model
      gazebo_multirotor_base_plugin
    )
    printf 'GAZEBO_CLASSIC_CONFIGURE_COMMAND=cmake -S %q -B %q -GNinja -DSEND_ODOMETRY_DATA=ON -DGENERATE_ROS_MODELS=ON\n' \
      "${GAZEBO_CLASSIC_SOURCE_DIR}" "${GAZEBO_CLASSIC_BUILD_DIR}"
    cmake -S "${GAZEBO_CLASSIC_SOURCE_DIR}" -B "${GAZEBO_CLASSIC_BUILD_DIR}" -GNinja \
      -DSEND_ODOMETRY_DATA=ON \
      -DGENERATE_ROS_MODELS=ON
    printf 'GAZEBO_CLASSIC_BUILD_COMMAND=cmake --build %q --target' \
      "${GAZEBO_CLASSIC_BUILD_DIR}"
    printf ' %q' "${GAZEBO_CLASSIC_PLUGIN_TARGETS[@]}"
    printf ' -- -j%s\n' "${BUILD_JOBS}"
    cmake --build "${GAZEBO_CLASSIC_BUILD_DIR}" \
      --target "${GAZEBO_CLASSIC_PLUGIN_TARGETS[@]}" \
      -- -j"${BUILD_JOBS}"
    for plugin in \
      libgazebo_gps_plugin.so \
      libgazebo_groundtruth_plugin.so \
      libgazebo_imu_plugin.so \
      libgazebo_mavlink_interface.so \
      libgazebo_magnetometer_plugin.so \
      libgazebo_barometer_plugin.so \
      libgazebo_motor_model.so \
      libgazebo_multirotor_base_plugin.so; do
      [[ -s "${GAZEBO_CLASSIC_BUILD_DIR}/${plugin}" ]] || die "Gazebo Classic plugin missing after build: ${plugin}"
    done
  elif [[ "${BUILD_GAZEBO_CLASSIC_PLUGINS}" != "false" ]]; then
    die "PX4_BUILD_GAZEBO_CLASSIC_PLUGINS must be true or false"
  elif [[ "${ACTION}" == "plugins_only" ]]; then
    die "--plugins-only cannot be combined with --skip-gazebo-classic-plugins"
  fi
fi
