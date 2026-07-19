#!/usr/bin/env bash
set -eo pipefail

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
PX4CTRL_OVERLAY="${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws/devel/setup.bash"

source /opt/ros/noetic/setup.bash
if [[ ! -f "${PX4CTRL_OVERLAY}" ]]; then
  echo "px4ctrl overlay missing: ${PX4CTRL_OVERLAY}" >&2
  exit 3
fi
source "${PX4CTRL_OVERLAY}"
set -u

display_kind="${1:-}"
planner_profile="${2:-none}"
readiness_path="${3:-}"

write_readiness() {
  local status="$1"
  local reason="$2"
  local config_path="${3:-}"
  local fixed_frame="${4:-}"
  local required_topics="${5:-}"
  if [[ -z "${readiness_path}" ]]; then
    return
  fi
  python3 - "${readiness_path}" "${display_kind}" "${status}" "${reason}" "${config_path}" "${fixed_frame}" "${required_topics}" <<'PY'
import json
import os
import sys
import time

path, display, status, reason, config_path, fixed_frame, topics = sys.argv[1:]
os.makedirs(os.path.dirname(path), exist_ok=True)
payload = {
    "schema": "mosim.ros1_display.readiness.v1",
    "display": display,
    "status": status,
    "reason_code": reason,
    "rviz_config": config_path,
    "fixed_frame": fixed_frame,
    "required_topics": [topic for topic in topics.split(",") if topic],
    "updated_at": time.time(),
}

# A delayed duplicate launcher may run after ROS shutdown. Preserve an already
# proven ready display and retain the late attempt as diagnostic evidence.
if os.path.exists(path):
    try:
        with open(path, "r", encoding="utf-8-sig") as stream:
            existing = json.load(stream)
    except (OSError, json.JSONDecodeError):
        existing = {}
    if existing.get("status") == "ready" and status != "ready":
        late_path = path + ".latest_attempt.json"
        temporary = late_path + ".tmp"
        with open(temporary, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, late_path)
        raise SystemExit(0)

temporary = path + ".tmp"
with open(temporary, "w", encoding="utf-8") as stream:
    json.dump(payload, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
os.replace(temporary, path)
PY
}

block() {
  local reason="$1"
  local config_path="${2:-}"
  local fixed_frame="${3:-}"
  local required_topics="${4:-}"
  write_readiness blocked "${reason}" "${config_path}" "${fixed_frame}" "${required_topics}"
  echo "${display_kind} blocked: ${reason}" >&2
  exit 4
}

wait_for_sample() {
  local topic="$1"
  local output_file
  output_file="$(mktemp)"
  if ! python3 "${PROJECT_ROOT}/Scripts/sunray/wait_for_topic_sample.py" \
      --topic "${topic}" --timeout-s 60 --output "${output_file}" >/dev/null 2>&1; then
    rm -f "${output_file}"
    return 1
  fi
  rm -f "${output_file}"
}

assert_samples() {
  local config_path="$1"
  local fixed_frame="$2"
  local required_topics="$3"
  local topics=()
  local pids=()
  local topic
  for topic in ${required_topics//,/ }; do
    topics+=("${topic}")
    wait_for_sample "${topic}" &
    pids+=("$!")
  done
  local index
  for index in "${!pids[@]}"; do
    if ! wait "${pids[$index]}"; then
      block "topic_sample_unavailable:${topics[$index]}" "${config_path}" "${fixed_frame}" "${required_topics}"
    fi
  done
}

assert_topic_frame() {
  local topic="$1"
  local expected_frame="$2"
  local actual_frame
  actual_frame="$(timeout 6s rostopic echo -n 1 "${topic}/header/frame_id" 2>/dev/null | head -n 1 | sed 's/^data: //' | tr -d "'\"[:space:]")"
  [[ "${actual_frame}" == "${expected_frame}" ]]
}

stop_project_ue_bridge() {
  local port="${1:-}"
  local owner_id="${2:-}"
  local pid cmd
  while read -r pid; do
    [[ -n "${pid}" && -r "/proc/${pid}/cmdline" ]] || continue
    cmd="$(tr '\0' ' ' < "/proc/${pid}/cmdline")"
    [[ "${cmd}" == *"Scripts/UE5/stream_ros1_state_to_ue_udp.py"* ]] || continue
    if [[ -n "${port}" && "${cmd}" != *"--port ${port}"* ]]; then
      continue
    fi
    if [[ -n "${owner_id}" && "${cmd}" != *"--stream-id ${owner_id}"* ]]; then
      continue
    fi
    kill -TERM "${pid}" >/dev/null 2>&1 || true
    for _ in 1 2 3 4 5; do
      kill -0 "${pid}" >/dev/null 2>&1 || break
      sleep 0.1
    done
    kill -KILL "${pid}" >/dev/null 2>&1 || true
  done < <(pgrep -f '[s]tream_ros1_state_to_ue_udp.py' || true)
}

require_ros_master() {
  if ! timeout 5s rosnode list >/dev/null 2>&1; then
    block ros_master_unreachable
  fi
}

case "${display_kind}" in
  rviz_pointcloud)
    require_ros_master
    owner_id="${4:-}"
    [[ -n "${owner_id}" ]] || block "display_session_owner_missing"
    if [[ "${planner_profile}" == "fuel_single_exploration" ]]; then
      config_path="${PROJECT_ROOT}/Config/rviz/sunray_ros1_factory_fuel_pointcloud_review.rviz"
      required_topics="/mosim/goal4/livox_world_accumulated,/mosim/goal4/truth_path,/mosim/goal4/position_cmd_path,/mosim/goal4/body_axes"
      assert_samples "${config_path}" world "${required_topics}"
      assert_topic_frame /mosim/goal4/livox_world_accumulated world || \
        block "fixed_frame_mismatch:/mosim/goal4/livox_world_accumulated" "${config_path}" world "${required_topics}"
      write_readiness ready display_inputs_ready "${config_path}" world "${required_topics}"
      export MOSIM_DISPLAY_SESSION_ID="${owner_id}"
      exec rviz -d "${config_path}"
    elif [[ "${planner_profile}" != "none" ]]; then
      block "pointcloud_profile_not_supported:${planner_profile}"
    fi
    config_path="${PROJECT_ROOT}/Config/rviz/sunray_ros1_fastlio_accumulated_map_review.rviz"
    required_topics="/mosim/fastlio/laser_map_obstacles,/mosim/px4ctrl/truth_path,/mosim/px4ctrl/reference_path,/mosim/fastlio/uav_axes"
    assert_samples "${config_path}" camera_init "${required_topics}"
    assert_topic_frame /mosim/fastlio/laser_map_obstacles camera_init || \
      block "fixed_frame_mismatch:/mosim/fastlio/laser_map_obstacles" "${config_path}" camera_init "${required_topics}"
    write_readiness ready display_inputs_ready "${config_path}" camera_init "${required_topics}"
    export MOSIM_DISPLAY_SESSION_ID="${owner_id}"
    exec rviz -d "${config_path}"
    ;;
  rviz_gridmap)
    require_ros_master
    owner_id="${4:-}"
    [[ -n "${owner_id}" ]] || block "display_session_owner_missing"
    if [[ "${planner_profile}" == "fuel_single_exploration" ]]; then
      config_path="${PROJECT_ROOT}/Config/rviz/sunray_ros1_factory_fuel_grid3d_review.rviz"
      required_topics="/mosim/goal4/occupancy_object_review,/mosim/goal4/truth_path,/mosim/goal4/position_cmd_path,/mosim/goal4/body_axes"
      assert_samples "${config_path}" world "${required_topics}"
      assert_topic_frame /mosim/goal4/occupancy_object_review world || \
        block "fixed_frame_mismatch:/mosim/goal4/occupancy_object_review" "${config_path}" world "${required_topics}"
      write_readiness ready display_inputs_ready "${config_path}" world "${required_topics}"
      export MOSIM_DISPLAY_SESSION_ID="${owner_id}"
      exec rviz -d "${config_path}"
    elif [[ "${planner_profile}" != "none" ]]; then
      block "gridmap_profile_not_supported:${planner_profile}"
    fi
    config_path="${PROJECT_ROOT}/Config/rviz/sunray_ros1_fastlio_grid3d_review.rviz"
    required_topics="/mosim/fastlio/occupancy_object_review,/mosim/px4ctrl/truth_path,/mosim/px4ctrl/reference_path,/mosim/fastlio/uav_axes"
    assert_samples "${config_path}" camera_init "${required_topics}"
    assert_topic_frame /mosim/fastlio/occupancy_object_review camera_init || \
      block "fixed_frame_mismatch:/mosim/fastlio/occupancy_object_review" "${config_path}" camera_init "${required_topics}"
    write_readiness ready display_inputs_ready "${config_path}" camera_init "${required_topics}"
    export MOSIM_DISPLAY_SESSION_ID="${owner_id}"
    exec rviz -d "${config_path}"
    ;;
  rviz_stop)
    owner_id="${2:-}"
    [[ -n "${owner_id}" ]] || { echo "rviz_stop requires a display-session owner id" >&2; exit 2; }
    residual=0
    while read -r pid; do
      [[ -n "${pid}" && -r "/proc/${pid}/environ" ]] || continue
      if tr '\0' '\n' < "/proc/${pid}/environ" 2>/dev/null | grep -Fxq "MOSIM_DISPLAY_SESSION_ID=${owner_id}"; then
        kill -TERM "${pid}" >/dev/null 2>&1 || true
      fi
    done < <(pgrep -x rviz || true)
    sleep 0.25
    while read -r pid; do
      [[ -n "${pid}" && -r "/proc/${pid}/environ" ]] || continue
      if tr '\0' '\n' < "/proc/${pid}/environ" 2>/dev/null | grep -Fxq "MOSIM_DISPLAY_SESSION_ID=${owner_id}"; then
        residual=1
      fi
    done < <(pgrep -x rviz || true)
    exit "${residual}"
    ;;
  unreal_bridge)
    host_address="${2:-}"
    owner_id="${3:-}"
    run_id="${4:-}"
    metrics_output="${5:-}"
    if [[ -z "${host_address}" ]]; then
      echo "unreal_bridge requires the Windows host address" >&2
      exit 2
    fi
    if [[ -z "${owner_id}" ]]; then
      echo "unreal_bridge requires a display-session owner id" >&2
      exit 2
    fi
    if [[ -z "${run_id}" || -z "${metrics_output}" ]]; then
      echo "unreal_bridge requires run id and metrics output path" >&2
      exit 2
    fi
    stop_project_ue_bridge 5005
    cd "${PROJECT_ROOT}"
    # rospy will wait for the ROS master. Keep the display bridge alive when
    # Flight Console starts before Gazebo/ROS instead of requiring a restart.
    exec python3 -u Scripts/UE5/stream_ros1_state_to_ue_udp.py \
      --odom-topic /uav1/sunray/gazebo_pose \
      --position-cmd-topic /position_cmd \
      --link-states-topic /gazebo/link_states \
      --mavros-state-topic /uav1/mavros/state \
      --host "${host_address}" \
      --port 5005 \
      --rate-hz 100 \
      --source-timeout-s 0.5 \
      --run-id "${run_id}" \
      --metrics-output "${metrics_output}" \
      --stream-id "${owner_id}" \
      --vehicle-id uav1 \
      --scene-id factory \
      --map-id local_factoryenvironmentcollect \
      --controller-profile orchestrated \
      --planner-profile none
    ;;
  unreal_bridge_stop)
    owner_id="${2:-}"
    [[ -n "${owner_id}" ]] || { echo "unreal_bridge_stop requires a display-session owner id" >&2; exit 2; }
    stop_project_ue_bridge "" "${owner_id}"
    ;;
  *)
    echo "unsupported ROS1 display kind: ${display_kind:-missing}" >&2
    exit 2
    ;;
esac
