#!/usr/bin/env bash

source /opt/ros/noetic/setup.bash
set -euo pipefail

project_root="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
workspace="${1:-/opt/mosim_work/sunray_ws/fuel_ws_planner_only_debug_20260701_003}"
nlopt_source="${NLOPT_SOURCE:-${project_root}/Results/sunray_ros1/workspaces/fuel_deps/src/nlopt-v2.7.1}"
nlopt_build="${NLOPT_ASAN_BUILD:-/opt/mosim_work/sunray_ws/fuel_deps_asan/build/nlopt-v2.7.1}"
nlopt_prefix="${NLOPT_ASAN_PREFIX:-/opt/mosim_work/sunray_ws/fuel_deps_asan/install/nlopt-v2.7.1}"

if [[ ! -f "${nlopt_source}/CMakeLists.txt" ]]; then
  echo "NLopt source is missing: ${nlopt_source}" >&2
  exit 2
fi

cmake -S "${nlopt_source}" -B "${nlopt_build}" \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_INSTALL_PREFIX="${nlopt_prefix}" \
  -DBUILD_SHARED_LIBS=ON \
  -DNLOPT_PYTHON=OFF \
  -DNLOPT_OCTAVE=OFF \
  -DNLOPT_MATLAB=OFF \
  -DNLOPT_GUILE=OFF \
  -DCMAKE_C_FLAGS='-O0 -g -fsanitize=address -fno-omit-frame-pointer' \
  -DCMAKE_CXX_FLAGS='-O0 -g -fsanitize=address -fno-omit-frame-pointer' \
  -DCMAKE_EXE_LINKER_FLAGS='-fsanitize=address' \
  -DCMAKE_SHARED_LINKER_FLAGS='-fsanitize=address'
cmake --build "${nlopt_build}" --parallel 2
cmake --install "${nlopt_build}"

cd "${workspace}"
catkin_make \
  -DCMAKE_BUILD_TYPE=Debug \
  -DNLOPT_ROOT="${nlopt_prefix}" \
  -DNLOPT_INCLUDE_DIR="${nlopt_prefix}/include" \
  -DNLOPT_LIBRARY="${nlopt_prefix}/lib/libnlopt.so" \
  -DCMAKE_CXX_FLAGS_DEBUG='-O0 -g -fsanitize=address -fno-omit-frame-pointer -DEIGEN_MALLOC_ALREADY_ALIGNED=1 -DEIGEN_DONT_VECTORIZE=1' \
  -DCMAKE_C_FLAGS_DEBUG='-O0 -g -fsanitize=address -fno-omit-frame-pointer' \
  -DCMAKE_EXE_LINKER_FLAGS='-fsanitize=address' \
  -DCMAKE_SHARED_LINKER_FLAGS='-fsanitize=address' \
  -j2

for flags_file in \
  build/fuel_planner/path_searching/CMakeFiles/path_searching.dir/flags.make \
  build/fuel_planner/active_perception/CMakeFiles/active_perception.dir/flags.make \
  build/fuel_planner/exploration_manager/CMakeFiles/exploration_node.dir/flags.make; do
  if ! grep -q -- '-fsanitize=address' "${flags_file}"; then
    echo "ASAN compile flag missing from ${flags_file}" >&2
    exit 3
  fi
done

echo "FUEL full ASAN stack rebuilt with NLopt at ${nlopt_prefix}"
