#!/usr/bin/env bash
set -euo pipefail

cd /mnt/c/Users/HP/Desktop/MoSim

STAMP=$(date +%Y%m%d_%H%M%S)
RESULT_DIR="/mnt/c/Users/HP/Desktop/MoSim/Results/sunray_ros1/sunray_ros1_freq100_spiral_zbias_smoothz_zlead03_${STAMP}"
mkdir -p "${RESULT_DIR}"

export PROJECT_ROOT=/mnt/c/Users/HP/Desktop/MoSim
export RESULT_DIR
export MISSION=spiral_climb
export GUI=false
export RVIZ=false
export FASTLIO=false
export WAIT_NONEMPTY_LIDAR=false
export REQUIRE_NONEMPTY_LIDAR=false
export USE_SIM_TIME=true
export CLEAN_START=true
export TOTAL_TIMEOUT_S=240
export FREQUENCY_AUDIT_DURATION_S=0
export CONTROL_DIAGNOSTICS_DURATION_S=90
export TIME_TF_AUDIT_DURATION_S=0

export MAVROS_STREAM_RATE_HZ=100
export PX4_PATCH_MAVLINK_STREAMS=true
export PX4_MAVLINK_STREAM_NAMES="LOCAL_POSITION_NED"
export MAVROS_SET_STREAM_GROUPS="position"
export MAVROS_SET_MESSAGE_IDS="32:LOCAL_POSITION_NED"
export MAVROS_SET_MESSAGE_INTERVALS=true
export MAVROS_PATCH_RATE_LIMITS=false

export SUNRAY_GAZEBO_MAX_STEP_SIZE_S=0.001
export SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ=1000
export SUNRAY_CTRL_CONTROL_LOOP_HZ=200.0
export SUNRAY_CTRL_QUAD_MASS=0.67
export SUNRAY_CTRL_HOV_PERCENT=0.37
export SUNRAY_CTRL_KP_XY=9.5
export SUNRAY_CTRL_KV_XY=5.2
export SUNRAY_CTRL_KVI_XY=0.2
export SUNRAY_CTRL_KP_Z=3.0
export SUNRAY_CTRL_KV_Z=3.0
export SUNRAY_CTRL_KVI_Z=0.8
export SUNRAY_CTRL_TILT_ANGLE_MAX=20.0
export SUNRAY_TAKEOFF_HEIGHT=1.0
export SUNRAY_LAND_SPEED=0.25

export MISSION_NODE_ARGS="--position-hold-mode ctrlxyzpos --control-mode ctrltraj --initial-hover-s 14.0 --enable-hover-bias-calibration --hover-bias-calibration-axes z --hover-bias-calibration-settle-s 8.0 --hover-bias-calibration-tail-s 4.0 --hover-bias-calibration-verify-s 3.0 --hover-bias-calibration-gain 0.6 --hover-bias-calibration-max-step-m 0.02 --steady-hover-eval-tail-s 8.0 --spiral-radius-m 0.50 --spiral-height-m 0.35 --spiral-period-s 44 --spiral-turns 2 --spiral-entry-s 6.0 --spiral-entry-settle-s 1.0 --spiral-speed-ramp-s 0.0 --spiral-z-profile smoothstep --trajectory-time-lead-s 0.2 --trajectory-z-time-lead-s 0.3 --command-rate-hz 20 --max-spiral-max-xyz-error-m 0.05 --max-spiral-p95-xyz-error-m 0.05 --max-spiral-rmse-xyz-m 0.05"

echo "${RESULT_DIR}" | tee "${RESULT_DIR}/result_dir.txt"
exec bash Scripts/sunray/run_sunray_ros1_native_mission_gate.sh
