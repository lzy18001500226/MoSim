#!/usr/bin/env bash
set -euo pipefail

cd /mnt/c/Users/HP/Desktop/MoSim

STAMP=$(date +%Y%m%d_%H%M%S)
RESULT_DIR="/mnt/c/Users/HP/Desktop/MoSim/Results/sunray_ros1/sunray_ros1_freq100_figure8_zbias_bestshape_${STAMP}"
mkdir -p "${RESULT_DIR}"

export PROJECT_ROOT=/mnt/c/Users/HP/Desktop/MoSim
export RESULT_DIR
export MISSION=figure8
export GUI=false
export RVIZ=false
export FASTLIO=false
export WAIT_NONEMPTY_LIDAR=false
export REQUIRE_NONEMPTY_LIDAR=false
export USE_SIM_TIME=true
export CLEAN_START=true
export TOTAL_TIMEOUT_S=260
export FREQUENCY_AUDIT_DURATION_S=0
export CONTROL_DIAGNOSTICS_DURATION_S=110
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
export SUNRAY_CTRL_KVI_Z=0.6
export SUNRAY_CTRL_TILT_ANGLE_MAX=20.0
export SUNRAY_TAKEOFF_HEIGHT=1.0
export SUNRAY_LAND_SPEED=0.25

export MISSION_NODE_ARGS="--position-hold-mode ctrlxyzpos --control-mode ctrltraj --initial-hover-s 14.0 --enable-hover-bias-calibration --hover-bias-calibration-axes z --hover-bias-calibration-settle-s 8.0 --hover-bias-calibration-tail-s 4.0 --hover-bias-calibration-verify-s 3.0 --hover-bias-calibration-gain 0.6 --hover-bias-calibration-max-step-m 0.02 --steady-hover-eval-tail-s 8.0 --figure8-amp-x-m 0.65 --figure8-amp-y-m 0.30 --figure8-period-s 42 --figure8-laps 2 --figure8-speed-ramp-s 4 --pre-figure8-hold-s 2 --post-figure8-hold-s 2 --trajectory-time-lead-s 0.2 --command-rate-hz 20 --max-figure8-rmse-xy-m 0.05 --max-figure8-p95-xy-error-m 0.05 --max-figure8-max-xy-error-m 0.05 --max-figure8-time-sync-rmse-xy-m 0.05 --max-figure8-time-sync-p95-xy-error-m 0.05 --max-figure8-time-sync-max-xy-error-m 0.05"

echo "${RESULT_DIR}" | tee "${RESULT_DIR}/result_dir.txt"
exec bash Scripts/sunray/run_sunray_ros1_native_mission_gate.sh
