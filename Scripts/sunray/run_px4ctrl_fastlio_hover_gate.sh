#!/usr/bin/env bash
# Source-local formal single-aircraft FAST-LIO/PX4-EKF takeoff-hover-land gate.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
MISSION="${1:-${MISSION:-takeoff_hover_land}}"

if [[ "$#" -gt 1 ]]; then
  echo "Usage: bash Scripts/sunray/run_px4ctrl_fastlio_hover_gate.sh [takeoff_hover_land]" >&2
  exit 2
fi
if [[ "${MISSION}" != "takeoff_hover_land" ]]; then
  echo "The formal FAST-LIO baseline only accepts MISSION=takeoff_hover_land." >&2
  exit 2
fi
if [[ "${SUNRAY_GPS_SENSOR_MODE:-removed}" != "removed" ]]; then
  echo "The formal FAST-LIO baseline requires SUNRAY_GPS_SENSOR_MODE=removed." >&2
  exit 2
fi
for name in \
  PX4CTRL_BOOT_PARAM_OVERRIDES \
  PX4CTRL_EXTRA_PARAM_OVERRIDES \
  PX4CTRL_EKF2_EV_CTRL_OVERRIDE \
  PX4CTRL_EKF2_HGT_REF_OVERRIDE; do
  if [[ -n "${!name:-}" ]]; then
    echo "${name} must be unset for the frozen FAST-LIO boot contract." >&2
    exit 2
  fi
done

export PROJECT_ROOT
export SUNRAY_GPS_SENSOR_MODE=removed
export PX4CTRL_CORE_PROFILE=original
# The generic px4ctrl source keeps the Modelica/base-adapter 0.37 default.
# This frozen Gazebo hover gate uses the measured runtime thrust map instead.
export PX4CTRL_HOVER_PERCENTAGE=0.456
# Gazebo samples IMU turn-on bias at each PX4 boot, so this formal simulator
# baseline does not reuse a previous run's calibration offsets.
export PX4CTRL_SUNRAY150_IMU_CALIBRATION_ENABLED=false
export PX4CTRL_SUNRAY150_IMU_CALIBRATION_OVERRIDES=
# Freeze the accepted startup window rather than depending on generic runner
# defaults that may belong to another experiment.
export PX4CTRL_TAKEOFF_HOVER_DEFAULT_ARGS="--initial-hover-s 20 --steady-hover-tail-s 8 --land-wait-s 25 --force-disarm-after-land --force-disarm-timeout-s 18 --command-x-bias-m -0.006 --command-y-bias-m -0.004 --command-z-bias-m 0.0 --pre-takeoff-state-stable-s 3.0 --pre-takeoff-state-timeout-s 60 --pre-takeoff-max-abs-roll-pitch-deg 2.0"
export PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=true
export PX4CTRL_START_EXTERNAL_FUSION=true
export PX4CTRL_ODOM_SOURCE=mavros_local
export PX4CTRL_ODOM_TOPIC=/uav1/mavros/local_position/odom
export FASTLIO_ALIGNMENT_Z_SOURCE=truth
export FASTLIO_ALIGNMENT_REFERENCE=config
export FASTLIO_ALIGNMENT_REQUIRED=true
export REVIEW_START_FASTLIO=true
export MISSION=takeoff_hover_land

exec bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh" takeoff_hover_land
