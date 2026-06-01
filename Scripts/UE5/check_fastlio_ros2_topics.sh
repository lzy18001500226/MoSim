#!/usr/bin/env bash
set -euo pipefail

# Check the ROS2 topics that prove the native RViz2/FAST-LIO-family replay path
# is actually publishing runtime data. Use DRY_RUN=1 for machines without ROS2.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
DRY_RUN="${DRY_RUN:-0}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-5}"
REQUIRE_FASTLIO_OUTPUTS="${REQUIRE_FASTLIO_OUTPUTS:-1}"
INPUT_TOPICS=(
  "/velodyne_points"
  "/imu/data"
  "/mosim/local_occupancy_grid"
  "/mosim/local_plan"
)
FASTLIO_OUTPUT_TOPICS=(
  "/cloud_registered"
  "/Odometry"
)

cd "${PROJECT_ROOT}"

REQUIRED_TOPICS=("${INPUT_TOPICS[@]}")
if [[ "${REQUIRE_FASTLIO_OUTPUTS}" == "1" ]]; then
  REQUIRED_TOPICS+=("${FASTLIO_OUTPUT_TOPICS[@]}")
fi

if [[ "${DRY_RUN}" == "1" ]]; then
  printf '{\n'
  printf '  "schema": "mosim.fastlio_ros2_topic_check_dryrun.v1",\n'
  printf '  "require_fastlio_outputs": %s,\n' "$([[ "${REQUIRE_FASTLIO_OUTPUTS}" == "1" ]] && echo true || echo false)"
  printf '  "required_topics": ['
  for index in "${!REQUIRED_TOPICS[@]}"; do
    [[ "${index}" == "0" ]] || printf ', '
    printf '"%s"' "${REQUIRED_TOPICS[$index]}"
  done
  printf '],\n'
  printf '  "claim": "dry-run only; no ROS2 graph or topics were queried"\n'
  printf '}\n'
  exit 0
fi

if [[ ! -f "${ROS_SETUP}" ]]; then
  echo "Missing ROS2 setup file: ${ROS_SETUP}" >&2
  exit 4
fi
# shellcheck disable=SC1090
set +u
source "${ROS_SETUP}"
set -u

for command_name in ros2 timeout; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Missing ${command_name}. Source/install ROS2 before checking runtime topics." >&2
    exit 4
  fi
done

TOPICS="$(ros2 topic list)"
missing=()
for topic in "${REQUIRED_TOPICS[@]}"; do
  if ! grep -Fxq "${topic}" <<<"${TOPICS}"; then
    missing+=("${topic}")
  fi
done

if [[ "${#missing[@]}" -gt 0 ]]; then
  echo "Missing required ROS2 topics:" >&2
  printf '  %s\n' "${missing[@]}" >&2
  exit 5
fi

for topic in "${REQUIRED_TOPICS[@]}"; do
  timeout "${TIMEOUT_SECONDS}" ros2 topic echo --once "${topic}" >/dev/null
done

echo "FAST-LIO/RViz2 ROS2 topic check passed."
