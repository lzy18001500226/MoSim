#!/usr/bin/env bash
set -euo pipefail

# Check the ROS1 topics that prove the native FAST-LIO/RViz replay path is
# actually publishing runtime data. This is a runtime probe; use DRY_RUN=1 for
# machines without ROS1.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
DRY_RUN="${DRY_RUN:-0}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-5}"
REQUIRED_TOPICS=(
  "/velodyne_points"
  "/imu/data"
  "/mosim/local_occupancy_grid"
  "/mosim/local_plan"
  "/cloud_registered"
  "/Odometry"
)

cd "${PROJECT_ROOT}"

if [[ "${DRY_RUN}" == "1" ]]; then
  printf '{\n'
  printf '  "schema": "mosim.fastlio_ros1_topic_check_dryrun.v1",\n'
  printf '  "required_topics": ['
  for index in "${!REQUIRED_TOPICS[@]}"; do
    [[ "${index}" == "0" ]] || printf ', '
    printf '"%s"' "${REQUIRED_TOPICS[$index]}"
  done
  printf '],\n'
  printf '  "claim": "dry-run only; no ROS master or topics were queried"\n'
  printf '}\n'
  exit 0
fi

for command_name in rostopic timeout; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Missing ${command_name}. Source/install ROS1 before checking runtime topics." >&2
    exit 4
  fi
done

TOPICS="$(rostopic list)"
missing=()
for topic in "${REQUIRED_TOPICS[@]}"; do
  if ! grep -Fxq "${topic}" <<<"${TOPICS}"; then
    missing+=("${topic}")
  fi
done

if [[ "${#missing[@]}" -gt 0 ]]; then
  echo "Missing required ROS topics:" >&2
  printf '  %s\n' "${missing[@]}" >&2
  exit 5
fi

for topic in "${REQUIRED_TOPICS[@]}"; do
  timeout "${TIMEOUT_SECONDS}" rostopic echo -n 1 "${topic}" >/dev/null
done

echo "FAST-LIO/RViz ROS1 topic check passed."
