#!/usr/bin/env bash
# Shared source-only defaults for the active Sunray ROS1 runtime lane.
# This file is intended to be sourced by runtime entrypoints.

if [[ -z "${PROJECT_ROOT:-}" ]]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
fi

LOCAL_ROS1_WS="${LOCAL_ROS1_WS:-${PROJECT_ROOT}/build/ros1/local_source_ws}"
MOSIM_RUNTIME_OVERLAY_ID="${MOSIM_RUNTIME_OVERLAY_ID:-${RUN_ID:-runtime}}"
SUNRAY_RUNTIME_OVERLAY_ROOT="${SUNRAY_RUNTIME_OVERLAY_ROOT:-${PROJECT_ROOT}/build/ros1/runtime_overlays}"
SUNRAY_WS="${SUNRAY_WS:-${SUNRAY_RUNTIME_OVERLAY_ROOT}/${MOSIM_RUNTIME_OVERLAY_ID}}"
SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR:-${PROJECT_ROOT}/src/flight_stack/px4/PX4-Autopilot}"
PX4_BUILD_DIR="${PX4_BUILD_DIR:-${PROJECT_ROOT}/build/px4/px4_sitl_default}"
# ROS1 resolves a node executable below the package returned by rospack.  The
# source package has no in-tree build/ directory, so the generated runtime
# overlay owns a small px4 package that exposes the external source-local build.
PX4_ROS1_OVERLAY_PKG="${PX4_ROS1_OVERLAY_PKG:-${SUNRAY_WS}/px4}"
PX4CTRL_WS="${PX4CTRL_WS:-${LOCAL_ROS1_WS}}"
LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS:-${LOCAL_ROS1_WS}}"
FASTLIO_WS="${FASTLIO_WS:-${LOCAL_ROS1_WS}}"
FTC_PLUGIN_WS="${FTC_PLUGIN_WS:-${PROJECT_ROOT}/build/ros1/ftc_actuator_plugin_ws}"

export LOCAL_ROS1_WS
export MOSIM_RUNTIME_OVERLAY_ID
export SUNRAY_RUNTIME_OVERLAY_ROOT
export SUNRAY_WS
export SUNRAY_PX4_DIR
export PX4_BUILD_DIR
export PX4_ROS1_OVERLAY_PKG
export PX4CTRL_WS
export LIVOX_PLUGIN_WS
export FASTLIO_WS
export FTC_PLUGIN_WS
