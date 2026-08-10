#!/usr/bin/env bash
# ROS Noetic's setup script reads optional unset environment variables.
set -eo pipefail

usage() {
  cat <<'EOF'
Usage: run_qgc_online_waypoint_fixture.sh --run-dir <dir> --manifest <path> --coordinate-evidence <path> [--ros-master-port <port>]

Starts a controlled ROS1 display fixture and a read-only runtime_sidecar. It
does not launch PX4, Gazebo, MAVROS control, a mission adapter, or QGC.
Stop this visible terminal with Ctrl+C after the visual audit.
EOF
}

run_dir=""
manifest=""
coordinate_evidence=""
ros_master_port="11431"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-dir) run_dir="$2"; shift 2 ;;
    --manifest) manifest="$2"; shift 2 ;;
    --coordinate-evidence) coordinate_evidence="$2"; shift 2 ;;
    --ros-master-port) ros_master_port="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$run_dir" || -z "$manifest" || -z "$coordinate_evidence" ]]; then
  usage >&2
  exit 2
fi
if [[ ! -f "$manifest" || ! -f "$coordinate_evidence" ]]; then
  echo "manifest or coordinate evidence is missing" >&2
  exit 2
fi
if ! [[ "$ros_master_port" =~ ^[0-9]{2,5}$ ]]; then
  echo "ros master port is invalid" >&2
  exit 2
fi

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
mkdir -p "$run_dir"
source /opt/ros/noetic/setup.bash
set -u
export ROS_MASTER_URI="http://127.0.0.1:${ros_master_port}"
export ROS_HOSTNAME="127.0.0.1"

roscore_pid=""
publisher_pid=""
sidecar_pid=""
cleanup() {
  trap - EXIT INT TERM
  for pid in "$sidecar_pid" "$publisher_pid" "$roscore_pid"; do
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
  for pid in "$sidecar_pid" "$publisher_pid" "$roscore_pid"; do
    if [[ -n "$pid" ]]; then
      wait "$pid" 2>/dev/null || true
    fi
  done
}
trap cleanup EXIT
trap 'cleanup; exit 0' INT TERM

# The audit must own its ROS master. Reusing an arbitrary existing master can
# make a failed roscore launch look healthy until that unrelated master exits.
if rosparam list >/dev/null 2>&1; then
  echo "Refusing to reuse a ROS master already reachable at ${ROS_MASTER_URI}" >&2
  exit 1
fi

roscore -p "$ros_master_port" > "$run_dir/qgc_online_waypoint_roscore.log" 2>&1 &
roscore_pid="$!"
roscore_ready=0
for _ in $(seq 1 50); do
  if ! kill -0 "$roscore_pid" 2>/dev/null; then
    wait "$roscore_pid" 2>/dev/null || true
    echo "Controlled ROS master exited during startup; see $run_dir/qgc_online_waypoint_roscore.log" >&2
    exit 1
  fi
  if rosparam list >/dev/null 2>&1; then
    roscore_ready=1
    break
  fi
  sleep 0.1
done
if [[ "$roscore_ready" != "1" ]] || ! kill -0 "$roscore_pid" 2>/dev/null; then
  echo "ROS master did not become ready" >&2
  exit 1
fi

python3 -u "$project_root/Scripts/ui/publish_qgc_online_waypoint_fixture.py" \
  --frame-id mworks_world \
  --rate-hz 2 \
  > "$run_dir/qgc_online_waypoint_fixture_publisher.log" 2>&1 &
publisher_pid="$!"

python3 -u "$project_root/Scripts/ui/runtime_sidecar.py" \
  --run-dir "$run_dir" \
  --manifest "$manifest" \
  --contract "$project_root/Config/control_platform/factory_injection_contract.json" \
  --vehicle-count 1 \
  --rate-hz 2 \
  --max-track-points 240 \
  --ready-timeout-s 20 \
  --expected-path-topic /mosim/qgc_audit/expected_path \
  --future-marker-topic /mosim/qgc_audit/future_path \
  --coordinate-evidence "$coordinate_evidence" \
  --skip-controller-command-readiness \
  --skip-actuator-telemetry-readiness \
  --read-only \
  > "$run_dir/qgc_online_waypoint_sidecar.log" 2>&1 &
sidecar_pid="$!"

printf '%s\n' "$roscore_pid" > "$run_dir/qgc_online_waypoint_roscore.pid"
printf '%s\n' "$publisher_pid" > "$run_dir/qgc_online_waypoint_fixture_publisher.pid"
printf '%s\n' "$sidecar_pid" > "$run_dir/qgc_online_waypoint_sidecar.pid"
printf '%s\n' "ROS_MASTER_URI=$ROS_MASTER_URI" > "$run_dir/qgc_online_waypoint_fixture.env"
printf '%s\n' "Controlled ROS1 display fixture is running. Press Ctrl+C to stop it."
wait "$sidecar_pid"
