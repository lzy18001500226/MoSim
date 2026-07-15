#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
DEPS_ROOT="${FUEL_DEPS_ROOT:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/fuel_deps}"
NLOPT_VERSION="${NLOPT_VERSION:-v2.7.1}"
NLOPT_SRC="${DEPS_ROOT}/src/nlopt-${NLOPT_VERSION}"
NLOPT_BUILD="${DEPS_ROOT}/build/nlopt-${NLOPT_VERSION}"
NLOPT_PREFIX="${NLOPT_ROOT:-${DEPS_ROOT}/install/nlopt-${NLOPT_VERSION}}"

fail() {
  echo "FUEL_DEPS_SETUP=FAIL"
  echo "reason=$1"
  exit 1
}

echo "FUEL_DEPS_SETUP=START"
echo "project_root=${PROJECT_ROOT}"
echo "deps_root=${DEPS_ROOT}"
echo "nlopt_version=${NLOPT_VERSION}"
echo "nlopt_prefix=${NLOPT_PREFIX}"

[[ -d "${PROJECT_ROOT}" ]] || fail "project_root_missing"
command -v git >/dev/null 2>&1 || fail "missing_command:git"
command -v cmake >/dev/null 2>&1 || fail "missing_command:cmake"
command -v make >/dev/null 2>&1 || fail "missing_command:make"

mkdir -p "${DEPS_ROOT}/src" "${DEPS_ROOT}/build" "${DEPS_ROOT}/install"

if [[ -d "${NLOPT_SRC}/.git" ]]; then
  git -C "${NLOPT_SRC}" fetch --depth 1 origin "${NLOPT_VERSION}"
  git -C "${NLOPT_SRC}" checkout -q FETCH_HEAD
elif [[ -e "${NLOPT_SRC}" ]]; then
  fail "nlopt_source_path_exists_but_is_not_git:${NLOPT_SRC}"
else
  git clone --depth 1 --branch "${NLOPT_VERSION}" \
    https://github.com/stevengj/nlopt.git "${NLOPT_SRC}"
fi

cmake -S "${NLOPT_SRC}" -B "${NLOPT_BUILD}" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="${NLOPT_PREFIX}" \
  -DNLOPT_PYTHON=OFF \
  -DNLOPT_OCTAVE=OFF \
  -DNLOPT_MATLAB=OFF \
  -DNLOPT_GUILE=OFF \
  -DNLOPT_SWIG=OFF

cmake --build "${NLOPT_BUILD}" --target install -- -j"${FUEL_DEPS_BUILD_JOBS:-2}"

[[ -f "${NLOPT_PREFIX}/include/nlopt.hpp" || -f "${NLOPT_PREFIX}/include/nlopt.h" ]] \
  || fail "nlopt_header_missing_after_install"
[[ -f "${NLOPT_PREFIX}/lib/libnlopt.so" || -f "${NLOPT_PREFIX}/lib64/libnlopt.so" ]] \
  || fail "nlopt_library_missing_after_install"

echo "NLOPT_ROOT=${NLOPT_PREFIX}"
NLOPT_ROOT="${NLOPT_PREFIX}" bash "${PROJECT_ROOT}/Scripts/sunray/check_fuel_ros1_preflight.sh" --strict-build
echo "FUEL_DEPS_SETUP=PASS"
