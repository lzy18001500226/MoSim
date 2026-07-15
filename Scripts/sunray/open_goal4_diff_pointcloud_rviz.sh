#!/usr/bin/env bash
set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/diff_planner_schemeA_D4_rviz_keepalive_20260626_180413}"
GOAL4_DIFF_PLANNER_WS="${GOAL4_DIFF_PLANNER_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/goal4_diff_planner_ws_px4msg}"

source /opt/ros/noetic/setup.bash
source "${GOAL4_DIFF_PLANNER_WS}/devel/setup.bash"

exec rviz -d "${PROJECT_ROOT}/Config/rviz/sunray_ros1_goal4_diff_pointcloud_review.rviz" \
  > "${RESULT_DIR}/rviz_diff_pointcloud_review_hide_rays.log" 2>&1
