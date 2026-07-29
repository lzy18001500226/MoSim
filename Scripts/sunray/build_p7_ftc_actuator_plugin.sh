#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
WORKSPACE="${FTC_PLUGIN_WS:-${PROJECT_ROOT}/build/ros1/ftc_actuator_plugin_ws}"
PACKAGE_SOURCE="${PROJECT_ROOT}/Scripts/sunray/gazebo_ftc_actuator_plugin"

export PATH=/opt/ros/noetic/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
unset CONDA_PREFIX CONDA_DEFAULT_ENV PYTHONHOME
set +u
source /opt/ros/noetic/setup.bash
set -u
export CMAKE_PREFIX_PATH=/opt/ros/noetic
export PKG_CONFIG_PATH=/opt/ros/noetic/lib/pkgconfig:/usr/lib/x86_64-linux-gnu/pkgconfig:/usr/share/pkgconfig
mkdir -p "${WORKSPACE}/src"
ln -sfn "${PACKAGE_SOURCE}" "${WORKSPACE}/src/mosim_gazebo_ftc_actuator_plugin"
catkin_make -C "${WORKSPACE}" -DCMAKE_BUILD_TYPE=Release
test -f "${WORKSPACE}/devel/lib/libmosim_gazebo_ftc_actuator_plugin.so"
printf '%s\n' "${WORKSPACE}/devel/lib/libmosim_gazebo_ftc_actuator_plugin.so"
