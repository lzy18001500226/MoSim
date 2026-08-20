#!/usr/bin/env bash
# Run one bounded Factory L2 ray-backend pacing measurement without QGC readiness.

set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "Usage: $0 RUN_ID ROS_MASTER_PORT" >&2
  exit 2
fi

RUN_ID="$1"
ROS_MASTER_PORT="$2"
# The original complete Factory model is the formal default. Lightweight
# overlays remain available only when an explicit diagnostic case is selected.
CASE_NAME="${FACTORY_L2_PACING_CASE:-gpu_full}"
if [[ ! "${RUN_ID}" =~ ^qgc-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$ ]]; then
  echo "RUN_ID must match qgc-[A-Za-z0-9][A-Za-z0-9._-]{0,95}" >&2
  exit 2
fi
if [[ ! "${ROS_MASTER_PORT}" =~ ^[1-9][0-9]{0,4}$ ]] || (( ROS_MASTER_PORT > 65535 )); then
  echo "ROS_MASTER_PORT must be a valid TCP port" >&2
  exit 2
fi
if (( ROS_MASTER_PORT == 11345 )); then
  echo "ROS_MASTER_PORT=11345 conflicts with the default Gazebo master port; choose another port" >&2
  exit 2
fi
case "${CASE_NAME}" in
  control|control_gpu_visual|gpu|gpu_full|gpu_full10x5|gpu_full2x2|gpu2x2) ;;
  gpu_full_physics400)
    echo "FACTORY_L2_PACING_CASE=gpu_full_physics400 is unsupported: PX4 Gazebo lockstep requires real_time_update_rate to be a positive multiple of 250 Hz; use gpu_full or gpu_full10x5" >&2
    exit 2
    ;;
  *)
    echo "FACTORY_L2_PACING_CASE must be control, control_gpu_visual, gpu, gpu_full, gpu_full10x5, gpu_full2x2, or gpu2x2, got ${CASE_NAME}" >&2
    exit 2
    ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CASE_DIR="${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}"
RUNTIME_DIR="${CASE_DIR}/runtime"
MEASUREMENT_PATH="${RUNTIME_DIR}/gpu_raw_cloud_pacing_measurement.json"
PROFILE_OUTPUT_PATH="${RUNTIME_DIR}/gpu_livox_profile.jsonl"
RESOURCE_SAMPLES_PATH="${RUNTIME_DIR}/gpu_pacing_resource_samples.jsonl"
LAUNCH_LOG="${CASE_DIR}/gpu_data_plane_launcher.log"
SUPERVISOR_LOG="${CASE_DIR}/gpu_data_plane_supervisor.log"
RESOURCE_SAMPLE_INTERVAL_S="${MOSIM_GPU_RESOURCE_SAMPLE_INTERVAL_S:-0}"
MEASUREMENT_INITIAL_WAIT_S="${MOSIM_GPU_MEASUREMENT_INITIAL_WAIT_S:-210}"
MEASUREMENT_DURATION_S="${MOSIM_GPU_MEASUREMENT_DURATION_S:-30}"
MEASUREMENT_TIMEOUT_S="${MOSIM_GPU_MEASUREMENT_TIMEOUT_S:-270}"
GAZEBO_READY_TIMEOUT_S="${MOSIM_GPU_GAZEBO_READY_TIMEOUT_S:-180}"

export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA
export ROS_MASTER_URI="http://127.0.0.1:${ROS_MASTER_PORT}"
export ROS_IP=127.0.0.1
export MOSIM_GPU_LIVOX_PROFILE_OUTPUT="${PROFILE_OUTPUT_PATH}"

if [[ ! "${RESOURCE_SAMPLE_INTERVAL_S}" =~ ^[0-9]+$ ]]; then
  echo "MOSIM_GPU_RESOURCE_SAMPLE_INTERVAL_S must be a non-negative integer" >&2
  exit 2
fi
for measurement_value in "${MEASUREMENT_INITIAL_WAIT_S}" "${MEASUREMENT_DURATION_S}" "${MEASUREMENT_TIMEOUT_S}"; do
  if [[ ! "${measurement_value}" =~ ^[1-9][0-9]*$ ]]; then
    echo "GPU measurement wait, duration, and timeout must be positive integers" >&2
    exit 2
  fi
done
if (( MEASUREMENT_TIMEOUT_S < MEASUREMENT_INITIAL_WAIT_S + MEASUREMENT_DURATION_S )); then
  echo "MOSIM_GPU_MEASUREMENT_TIMEOUT_S must cover initial wait plus duration" >&2
  exit 2
fi
if [[ ! "${GAZEBO_READY_TIMEOUT_S}" =~ ^[1-9][0-9]*$ ]]; then
  echo "MOSIM_GPU_GAZEBO_READY_TIMEOUT_S must be a positive integer" >&2
  exit 2
fi

LAUNCH_PID=""
RESOURCE_SAMPLER_PID=""
collect_process_tree() {
  local root_pid="$1"
  local child_pid
  while IFS= read -r child_pid; do
    [[ "${child_pid}" =~ ^[0-9]+$ ]] || continue
    collect_process_tree "${child_pid}"
    printf '%s\n' "${child_pid}"
  done < <(pgrep -P "${root_pid}" 2>/dev/null || true)
}

collect_run_scoped_processes() {
  ps -eo pid=,args= | awk -v marker="${CASE_DIR}/" 'index($0, marker) { print $1 }'
}

stop_launcher() {
  if [[ -z "${LAUNCH_PID}" ]]; then
    return
  fi

  local -a launcher_process_tree=()
  local signal tree_pid alive
  mapfile -t launcher_process_tree < <(collect_process_tree "${LAUNCH_PID}")
  launcher_process_tree+=("${LAUNCH_PID}")
  while IFS= read -r tree_pid; do
    [[ "${tree_pid}" =~ ^[0-9]+$ ]] || continue
    launcher_process_tree+=("${tree_pid}")
  done < <(collect_run_scoped_processes)

  for signal in INT TERM KILL; do
    for tree_pid in "${launcher_process_tree[@]}"; do
      kill "-${signal}" "${tree_pid}" 2>/dev/null || true
    done
    for _ in $(seq 1 20); do
      alive=false
      for tree_pid in "${launcher_process_tree[@]}"; do
        if kill -0 "${tree_pid}" 2>/dev/null; then
          alive=true
          break
        fi
      done
      if [[ "${alive}" == false ]]; then
        break
      fi
      sleep 0.25
    done
    if [[ "${alive}" == false ]]; then
      break
    fi
  done
  wait "${LAUNCH_PID}" 2>/dev/null || true
  LAUNCH_PID=""
}
stop_resource_sampler() {
  if [[ -z "${RESOURCE_SAMPLER_PID}" ]] || ! kill -0 "${RESOURCE_SAMPLER_PID}" 2>/dev/null; then
    return
  fi
  kill -INT "${RESOURCE_SAMPLER_PID}" 2>/dev/null || true
  wait "${RESOURCE_SAMPLER_PID}" 2>/dev/null || true
  RESOURCE_SAMPLER_PID=""
}
cleanup_probe() {
  local exit_code=$?
  trap - EXIT
  stop_resource_sampler || true
  stop_launcher || true
  exit "${exit_code}"
}

mkdir -p "${CASE_DIR}"
(
  # The launch PID is assigned by the left side of the tee pipeline, so the
  # cleanup trap must live in this same subshell to own the runtime process tree.
  trap cleanup_probe EXIT

  mkdir -p "${RUNTIME_DIR}"
  {
  printf 'run_id=%s\n' "${RUN_ID}"
  printf 'case_name=%s\n' "${CASE_NAME}"
  printf 'ros_master_uri=%s\n' "${ROS_MASTER_URI}"
  printf 'mesa_d3d12_default_adapter_name=%s\n' "${MESA_D3D12_DEFAULT_ADAPTER_NAME}"
  printf 'mosim_gpu_livox_output_mode=%s\n' "${MOSIM_GPU_LIVOX_OUTPUT_MODE:-pcl}"
  printf 'mosim_gpu_livox_profile_interval_frames=%s\n' "${MOSIM_GPU_LIVOX_PROFILE_INTERVAL_FRAMES:-0}"
  printf 'mosim_gpu_livox_profile_output=%s\n' "${MOSIM_GPU_LIVOX_PROFILE_OUTPUT}"
  printf 'mosim_gpu_resource_sample_interval_s=%s\n' "${RESOURCE_SAMPLE_INTERVAL_S}"
  printf 'mosim_gpu_resource_samples=%s\n' "${RESOURCE_SAMPLES_PATH}"
  printf 'measurement_initial_wait_s=%s\n' "${MEASUREMENT_INITIAL_WAIT_S}"
  printf 'measurement_duration_s=%s\n' "${MEASUREMENT_DURATION_S}"
  printf 'measurement_timeout_s=%s\n' "${MEASUREMENT_TIMEOUT_S}"
  printf 'started_at=%s\n' "$(date --iso-8601=seconds)"

  set +u
  source /opt/ros/noetic/setup.bash
  set -u
  env MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA glxinfo -B > "${RUNTIME_DIR}/renderer_glxinfo.txt" 2>&1 || true
  nvidia-smi --query-gpu=name,driver_version,utilization.gpu,memory.used,memory.total --format=csv,noheader \
    > "${RUNTIME_DIR}/renderer_nvidia_smi_before.txt" 2>&1 || true

  cd "${PROJECT_ROOT}"
  bash Scripts/sunray/run_factory_l2_realtime_ab_case.sh "${CASE_NAME}" "${RUN_ID}" > "${LAUNCH_LOG}" 2>&1 &
  LAUNCH_PID=$!
  printf 'launcher_pid=%s\n' "${LAUNCH_PID}"

  master_deadline=$((SECONDS + 240))
  while (( SECONDS < master_deadline )); do
    if timeout 3s rosnode list > "${RUNTIME_DIR}/gpu_roscore_probe.log" 2>&1; then
      printf 'ros_master_ready_at_wall_s=%s\n' "${SECONDS}"
      break
    fi
    if ! kill -0 "${LAUNCH_PID}" 2>/dev/null; then
      set +e
      wait "${LAUNCH_PID}"
      launcher_exit=$?
      set -e
      printf 'launcher_exit_before_ros_master=%s\n' "${launcher_exit}"
      exit 4
    fi
    sleep 1
  done

  if ! timeout 3s rosnode list > "${RUNTIME_DIR}/gpu_roscore_probe.log" 2>&1; then
    printf 'ros_master_timeout_s=240\n'
    exit 5
  fi

  wait_for_topic_message() {
    local topic="$1"
    local probe_path="$2"
    local deadline=$((SECONDS + GAZEBO_READY_TIMEOUT_S))
    while (( SECONDS < deadline )); do
      if ! kill -0 "${LAUNCH_PID}" 2>/dev/null; then
        printf 'gazebo_ready_launcher_exited=topic:%s\n' "${topic}"
        return 1
      fi
      if timeout 5s rostopic echo -n 1 "${topic}" > "${probe_path}" 2>&1; then
        printf 'gazebo_ready_topic=%s wall_s=%s\n' "${topic}" "${SECONDS}"
        return 0
      fi
      sleep 1
    done
    printf 'gazebo_ready_timeout_s=%s topic=%s\n' "${GAZEBO_READY_TIMEOUT_S}" "${topic}"
    return 1
  }

  # ROS master readiness only proves that roscore is alive. Wait for the
  # simulator and sensor messages before starting the pacing window, otherwise
  # a slow planner/Gazebo startup is misreported as an empty cloud.
  printf 'gazebo_ready_wait_timeout_s=%s\n' "${GAZEBO_READY_TIMEOUT_S}"
  wait_for_topic_message /clock "${RUNTIME_DIR}/gazebo_clock_ready.txt" || exit 9
  wait_for_topic_message /gazebo/model_states "${RUNTIME_DIR}/gazebo_model_states_ready.txt" || exit 9
  wait_for_topic_message /gazebo/performance_metrics "${RUNTIME_DIR}/gazebo_performance_metrics_ready.txt" || exit 9
  wait_for_topic_message /uav1/livox/lidar "${RUNTIME_DIR}/livox_lidar_ready.txt" || exit 9
  printf 'gazebo_and_livox_ready=true\n'

  if (( RESOURCE_SAMPLE_INTERVAL_S > 0 )); then
    python3 "${PROJECT_ROOT}/Scripts/sunray/sample_factory_l2_runtime_resources.py" \
      --output "${RESOURCE_SAMPLES_PATH}" \
      --root-pid "${LAUNCH_PID}" \
      --interval-s "${RESOURCE_SAMPLE_INTERVAL_S}" \
      > "${RUNTIME_DIR}/gpu_pacing_resource_sampler.log" 2>&1 &
    RESOURCE_SAMPLER_PID=$!
    printf 'resource_sampler_pid=%s\n' "${RESOURCE_SAMPLER_PID}"
  fi

  # QGC, planner, and PX4 acceptance are outside this probe's scope. The
  # measurement begins once Gazebo itself publishes clock, metrics, and raw
  # PointCloud2, so a downstream planner blocker cannot erase pacing evidence.
  set +e
  timeout "${MEASUREMENT_TIMEOUT_S}s" python3 "${PROJECT_ROOT}/Scripts/sunray/measure_gazebo_raw_cloud_pacing.py" \
    --output "${MEASUREMENT_PATH}" \
    --duration-s "${MEASUREMENT_DURATION_S}" \
    --initial-wait-s "${MEASUREMENT_INITIAL_WAIT_S}" \
    --min-rtf 0.95 \
    > "${RUNTIME_DIR}/gpu_raw_cloud_pacing_measurement.stdout.log" 2>&1
  measurement_exit=$?
  set -e
  printf 'measurement_exit=%s\n' "${measurement_exit}"

  nvidia-smi --query-gpu=name,driver_version,utilization.gpu,memory.used,memory.total --format=csv,noheader \
    > "${RUNTIME_DIR}/renderer_nvidia_smi_after.txt" 2>&1 || true
  if [[ -f "${MEASUREMENT_PATH}" ]]; then
    python3 - "${MEASUREMENT_PATH}" <<'PY'
import json
import pathlib
import sys

payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
performance = payload.get("gazebo_performance_metrics") or {}
print(f"measurement_status={payload.get('status')}")
print(f"clock_rtf={payload.get('wall_clock_measurement', {}).get('clock_real_time_factor')}")
print(f"gazebo_rtf={performance.get('real_time_factor')}")
print(f"raw_points={payload.get('raw_cloud', {}).get('latest_point_count')}")
print(f"raw_rate_hz={payload.get('raw_cloud', {}).get('wall_rate_hz')}")
PY
  else
    printf 'measurement_artifact=missing\n'
    exit 6
  fi
  if [[ "${MOSIM_GPU_LIVOX_PROFILE_INTERVAL_FRAMES:-0}" != "0" ]]; then
    if [[ ! -s "${PROFILE_OUTPUT_PATH}" ]]; then
      printf 'gpu_livox_profile_artifact=missing\n'
      exit 7
    fi
    tail -n 1 "${PROFILE_OUTPUT_PATH}"
  fi
  if (( RESOURCE_SAMPLE_INTERVAL_S > 0 )); then
    stop_resource_sampler
    if [[ ! -s "${RESOURCE_SAMPLES_PATH}" ]]; then
      printf 'gpu_pacing_resource_samples=missing\n'
      exit 8
    fi
    tail -n 1 "${RESOURCE_SAMPLES_PATH}"
  fi
    exit "${measurement_exit}"
  }
) > >(tee "${SUPERVISOR_LOG}")
