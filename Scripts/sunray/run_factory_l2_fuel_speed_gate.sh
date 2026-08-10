#!/usr/bin/env bash

set -euo pipefail

project_root="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
execute_s="${1:-45}"
result_dir="${2:?usage: run_factory_l2_fuel_speed_gate.sh EXECUTE_S RESULT_DIR}"

export PROJECT_ROOT="${project_root}"
export RESULT_DIR="${result_dir}"
# The source-local Factory gate must resolve px4ctrl from the checked-out
# workspace unless a caller explicitly supplies another workspace.
export PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/build/ros1/local_source_ws}"
export FACTORY_WORLD_MODE=clean
export PLANNER_VARIANT=fuel
export MISSION_MODE=exploration_stream
export SUNRAY_UAV_INIT_X=-10.575025
export SUNRAY_UAV_INIT_Y=-19.36313
export SUNRAY_UAV_INIT_Z=0.2
export SUNRAY_UAV_INIT_YAW=0
export TARGET_X=-10.575025
export TARGET_Y=-19.36313
export TARGET_Z=1.2
export GOAL4_TAKEOFF_HEIGHT=1.2
export GOAL4_TAKEOFF_TIMEOUT_S=90
# Keep the PX4CTRL auto-takeoff target identical to the mission gate target.
# A lower internal target lets the FSM enter hover before the mission gate is
# satisfied and caused both original and C99 runs to overshoot the 1.2 m gate.
# Keep the PX4CTRL auto-takeoff target identical to the mission gate by
# default, while allowing a controller-specific frozen profile to provide its
# already-validated relative takeoff height.
export PX4CTRL_AUTO_TAKEOFF_HEIGHT="${PX4CTRL_AUTO_TAKEOFF_HEIGHT:-${GOAL4_TAKEOFF_HEIGHT}}"
export GOAL4_EGO_TAKEOVER_TIMEOUT_S=90
export DIFF_PUBLISH_HOVER_DURING_TAKEOFF=true
export DIFF_PUBLISH_HOVER_DURING_TAKEOFF_DELAY_S=0.5
export PLANNER_CMD_ADAPTER_INITIAL_ENABLED=false
export GOAL4_FUEL_WS="${GOAL4_FUEL_WS:-/opt/mosim_work/sunray_ws/fuel_ws_release_20260713}"
export FUEL_EXPLORATION_EXECUTE_S="${execute_s}"

# Factory L2 currently advances simulation time at roughly 0.2-0.25x wall
# time. Budget the outer wall timeout from the requested simulation window so
# a valid exploration run is not truncated by the generic 220 s default.
if [[ -z "${TOTAL_TIMEOUT_S:-}" ]]; then
  export TOTAL_TIMEOUT_S="$(awk -v duration="${execute_s}" 'BEGIN { printf "%d", 100 + duration * 5 + 0.999 }')"
fi

export EGO_MAX_VEL=2.0
export EGO_MAX_ACC=1.5
export EGO_MAX_JERK=4.0
export FUEL_MAP_SIZE_X="${FUEL_MAP_SIZE_X:-64}"
export FUEL_MAP_SIZE_Y="${FUEL_MAP_SIZE_Y:-64}"
export FUEL_MAP_SIZE_Z="${FUEL_MAP_SIZE_Z:-3}"
export FUEL_GRID_RESOLUTION_M=0.2
export FUEL_BOX_MIN_X="${FUEL_BOX_MIN_X:--42.575025}"
export FUEL_BOX_MIN_Y="${FUEL_BOX_MIN_Y:--51.36313}"
export FUEL_BOX_MIN_Z="${FUEL_BOX_MIN_Z:-0.9}"
export FUEL_BOX_MAX_X="${FUEL_BOX_MAX_X:-21.424975}"
export FUEL_BOX_MAX_Y="${FUEL_BOX_MAX_Y:-12.63687}"
export FUEL_BOX_MAX_Z="${FUEL_BOX_MAX_Z:-1.6}"
export FUEL_FRAME_BRIDGE_ENABLED=true
export FUEL_FRAME_OFFSET_X=-10.575025
export FUEL_FRAME_OFFSET_Y=-19.36313
export FUEL_FRAME_OFFSET_Z=0
# MAVROS local_position and px4ctrl commands are already expressed relative
# to the takeoff origin. Only world-map data needs the Factory origin shift.
export FUEL_STATE_INPUT_OFFSET_X=0
export FUEL_STATE_INPUT_OFFSET_Y=0
export FUEL_STATE_INPUT_OFFSET_Z=0
export FUEL_COMMAND_OUTPUT_OFFSET_X=0
export FUEL_COMMAND_OUTPUT_OFFSET_Y=0
export FUEL_COMMAND_OUTPUT_OFFSET_Z=0
export FUEL_SENSOR_POSE_SOURCE=fastlio
export FUEL_MAX_RAY_LENGTH_M=12
export FUEL_PERCEPTION_MAX_DIST_M=12
export FUEL_PERCEPTION_VIS_DIST_M=8
export FUEL_FRONTIER_CLUSTER_MIN=60
export FUEL_FRONTIER_CLUSTER_SIZE_XY="${FUEL_FRONTIER_CLUSTER_SIZE_XY:-4.0}"
export FUEL_FRONTIER_MIN_VISIB_NUM=5
export FUEL_FRONTIER_MIN_CANDIDATE_CLEARANCE_M=0.12
export FUEL_EXPLORATION_NEAR_FRONTIER_ESCAPE_ENABLE="${FUEL_EXPLORATION_NEAR_FRONTIER_ESCAPE_ENABLE:-true}"
export FUEL_EXPLORATION_NEAR_FRONTIER_ESCAPE_DISTANCE="${FUEL_EXPLORATION_NEAR_FRONTIER_ESCAPE_DISTANCE:-0.75}"
export FUEL_EXPLORATION_NEAR_FRONTIER_ESCAPE_MAX_SPEED="${FUEL_EXPLORATION_NEAR_FRONTIER_ESCAPE_MAX_SPEED:-0.25}"
export FUEL_EXPLORATION_NEAR_FRONTIER_ESCAPE_ALTERNATIVE_DISTANCE="${FUEL_EXPLORATION_NEAR_FRONTIER_ESCAPE_ALTERNATIVE_DISTANCE:-2.0}"
export FUEL_MANAGER_LOCAL_SEGMENT_LENGTH_M=6
export FUEL_DYNAMIC_FEASIBILITY_MAX_ITERATIONS=12
export FUEL_DYNAMIC_FEASIBILITY_NORM_TOLERANCE="${FUEL_DYNAMIC_FEASIBILITY_NORM_TOLERANCE:-0.01}"
export FUEL_DYNAMIC_FEASIBILITY_MAX_TIME_SCALE="${FUEL_DYNAMIC_FEASIBILITY_MAX_TIME_SCALE:-2.0}"
export FUEL_P_OCC=0.8
# Match the existing Sunray FUEL safety envelope. The generic 0.099 m value
# inflates only one 0.2 m voxel and allowed the physical airframe to contact an
# obstacle while the point-mass trajectory was still considered collision-free.
export FUEL_OBSTACLES_INFLATION="${FUEL_OBSTACLES_INFLATION:-0.35}"
export FUEL_HARD_COLLISION_GATE_ENABLED="${FUEL_HARD_COLLISION_GATE_ENABLED:-true}"
export FUEL_HARD_COLLISION_SAMPLE_DT_S="${FUEL_HARD_COLLISION_SAMPLE_DT_S:-0.02}"
export FUEL_EMERGENCY_STOP_ENABLED="${FUEL_EMERGENCY_STOP_ENABLED:-true}"
export FUEL_EMERGENCY_STOP_DECELERATION_MPS2="${FUEL_EMERGENCY_STOP_DECELERATION_MPS2:-1.5}"
export FUEL_EMERGENCY_STOP_MARGIN_M="${FUEL_EMERGENCY_STOP_MARGIN_M:-0.35}"
# r83 normal exploration stayed below 0.665 m XY tracking error. Recover from
# odometry after a sustained 1.0 m divergence instead of extending a stale
# active spline until controller attitude saturates.
export FUEL_TRACKING_ERROR_RECOVERY_ENABLED="${FUEL_TRACKING_ERROR_RECOVERY_ENABLED:-true}"
export FUEL_TRACKING_ERROR_XY_LIMIT_M="${FUEL_TRACKING_ERROR_XY_LIMIT_M:-1.0}"
export FUEL_TRACKING_ERROR_PERSISTENCE_S="${FUEL_TRACKING_ERROR_PERSISTENCE_S:-0.2}"
export FUEL_COLLISION_RECOVERY_ENABLE="${FUEL_COLLISION_RECOVERY_ENABLE:-true}"
export FUEL_COLLISION_RECOVERY_RADIUS_M="${FUEL_COLLISION_RECOVERY_RADIUS_M:-0.75}"
export FUEL_COLLISION_RECOVERY_DURATION_S="${FUEL_COLLISION_RECOVERY_DURATION_S:-8.0}"
export FUEL_COLLISION_RECOVERY_MAX_ENTRIES="${FUEL_COLLISION_RECOVERY_MAX_ENTRIES:-12}"
export FUEL_COLLISION_RECOVERY_MIN_TIME_S="${FUEL_COLLISION_RECOVERY_MIN_TIME_S:-0.30}"
export FUEL_COLLISION_RECOVERY_MIN_PROGRESS="${FUEL_COLLISION_RECOVERY_MIN_PROGRESS:-0.10}"

# Keep the native planner trajectory visible to the controller. These gates
# must not become a hidden substitute for planner dynamic feasibility.
export FUEL_PRESERVE_NATIVE_TRAJECTORY=true
export FUEL_CMD_SMOOTH_ENABLE=false
export FUEL_CMD_SMOOTH_MAX_SPEED_MPS=0
export FUEL_CMD_SMOOTH_MAX_STEP_M=0
export FUEL_CMD_SMOOTH_ZERO_DYNAMICS=false
export FUEL_CMD_MOTION_TIME_BASIS=ros_sim_time
export FUEL_CMD_MAX_VELOCITY_MPS=0
export FUEL_CMD_MAX_ACCELERATION_MPS2=0
export FUEL_CMD_MAX_LATERAL_ACCELERATION_MPS2=0
export FUEL_CMD_MAX_JERK_MPS3=0
export FUEL_CMD_FIXED_Z=1.2
export FUEL_RAW_CMD_MAX_POSITION_JUMP_M=0
export FUEL_RAW_CMD_MAX_POSITION_JUMP_SPEED_MPS=0
export DIFF_CMD_SAFETY_MAX_POSITION_JUMP_M=0
export DIFF_CMD_SAFETY_MAX_POSITION_JUMP_SPEED_MPS=3.0
export DIFF_CMD_MIN_Z=0.9
export DIFF_CMD_MAX_Z=1.6
export PLANNER_CMD_SEED_FROM_ODOM_ON_ENABLE=true

export FASTLIO_MODE=livox_custom
export FASTLIO_SCAN_RATE_HZ=20
# This is FAST-LIO's internal localization voxel size, not the 0.08 m RViz
# accumulated-cloud display voxel. 0.02 m over a 40 m 360-degree scan causes
# PCL VoxelGrid integer-index overflow; 0.05 m removes the overflow but still
# allowed registration to stall during dynamic flight. Use the upstream
# MID360 baseline for the localization map and keep review density separate.
export FASTLIO_FILTER_SIZE_SURF="${FASTLIO_FILTER_SIZE_SURF:-0.5}"
export FASTLIO_FILTER_SIZE_MAP="${FASTLIO_FILTER_SIZE_MAP:-0.5}"
# The default accepted simulation baseline uses FAST-LIO for horizontal
# localization and Gazebo truth only as the height source. Native FAST-LIO z is
# not yet an accepted control input for this gate. A caller with a separately
# frozen control-state contract may override the fusion toggles below.
export FASTLIO_ALIGNMENT_Z_SOURCE=truth
export PX4CTRL_ENABLE_FASTLIO_EKF_FUSION="${PX4CTRL_ENABLE_FASTLIO_EKF_FUSION:-true}"
export PX4CTRL_PARAM_PULL_BEFORE_OVERRIDE=true
# PX4 v1.14 does not consume MAVLink VISION_SPEED_ESTIMATE. Feed synchronized
# pose and velocity through one MAVLink ODOMETRY message instead of split
# external_fusion/vision_speed topics.
export PX4CTRL_FASTLIO_ODOMETRY_FUSION_ENABLED="${PX4CTRL_FASTLIO_ODOMETRY_FUSION_ENABLED:-true}"
export PX4CTRL_FASTLIO_VELOCITY_FUSION_ENABLED="${PX4CTRL_FASTLIO_VELOCITY_FUSION_ENABLED:-false}"
# Keep the legacy defaults for an unset variable, while allowing a bounded
# caller to export an explicit empty value when its frozen run has no override.
export PX4CTRL_EKF2_EV_CTRL_OVERRIDE="${PX4CTRL_EKF2_EV_CTRL_OVERRIDE-15}"
export PX4CTRL_EKF2_HGT_REF_OVERRIDE="${PX4CTRL_EKF2_HGT_REF_OVERRIDE-3}"
# The synchronized r60 diagnostic measured about 0.128 m/s 95th-percentile
# FAST-LIO velocity error and rare dynamic peaks near 0.50 m/s. The previous
# 0.20 m/s covariance was overconfident and caused a short EV velocity reject
# burst even though position/height fusion and flight safety remained valid.
export FASTLIO_MAVROS_ODOMETRY_VELOCITY_STDDEV_MPS="${FASTLIO_MAVROS_ODOMETRY_VELOCITY_STDDEV_MPS:-0.35}"
export PX4CTRL_CORE_PROFILE="${PX4CTRL_CORE_PROFILE:-l1_awff}"
export PX4CTRL_CTRL_FREQ_MAX=100
export PX4CTRL_KP_XY="${PX4CTRL_KP_XY:-4}"
export PX4CTRL_KP_Z="${PX4CTRL_KP_Z:-4}"
export PX4CTRL_KV_XY="${PX4CTRL_KV_XY:-4}"
export PX4CTRL_KV_Z="${PX4CTRL_KV_Z:-4}"
export SUNRAY_GAZEBO_MAX_STEP_SIZE_S=0.001
export SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ=1000
export SUNRAY_SPLIT_WORLD_BASIC_LAUNCH=true
export MAVROS_READY_TIMEOUT_S=180
export SUNRAY_MID360_PLUGIN_DOWNSAMPLE="${SUNRAY_MID360_PLUGIN_DOWNSAMPLE:-4}"
export SUNRAY_MID360_GOAL5_CSV_STRIDE="${SUNRAY_MID360_GOAL5_CSV_STRIDE:-4}"
export GUI=false
export OPEN_RVIZ=false

set +e
bash "${project_root}/Scripts/sunray/run_px4ctrl_ego_single_gate.sh"
gate_exit_code=$?
set -e

if [[ "${PX4CTRL_FASTLIO_ODOMETRY_FUSION_ENABLED}" == "true" ]]; then
  set +e
  python3 "${project_root}/Scripts/sunray/analyze_px4_ev_fusion_ulog.py" \
    --project-root "${project_root}" \
    --ulog "${result_dir}/PX4_ESTIMATOR.ulg" \
    --output "${result_dir}/PX4_EV_FUSION_GATE.json"
  fusion_gate_exit_code=$?
  set -e
  if [[ "${gate_exit_code}" -eq 0 && "${fusion_gate_exit_code}" -ne 0 ]]; then
    gate_exit_code="${fusion_gate_exit_code}"
  fi
fi

exit "${gate_exit_code}"
