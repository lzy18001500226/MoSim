#!/usr/bin/env bash
set -euo pipefail

# Run the Factory Mid360/FAST-LIO ROS2 headless gate.
# This script is intentionally non-GUI: it verifies input streams first, then
# records FAST-LIO output topics and evaluates odometry against replay truth.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
SCENE_ID="${SCENE_ID:-factoryenvironmentcollect}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
ROS_LOG_DIR="${ROS_LOG_DIR:-${PROJECT_ROOT}/Results/tmp/ros_logs}"
LIVOX_UNDERLAY_SETUP="${LIVOX_UNDERLAY_SETUP:-${PROJECT_ROOT}/Results/tmp/spark_fast_lio_ros2_ws/install/livox_ros_driver2/share/livox_ros_driver2/local_setup.bash}"
FASTLIO_IMPORT_SETUP="${FASTLIO_IMPORT_SETUP:-${PROJECT_ROOT}/Results/tmp/fast_lio_ros2_import_ws/install/fast_lio/share/fast_lio/local_setup.bash}"
DENSE_LIDAR_SETUP="${DENSE_LIDAR_SETUP:-${PROJECT_ROOT}/Results/tmp/mosim_dense_lidar_cpp_ws/install/mosim_dense_lidar_cpp/share/mosim_dense_lidar_cpp/local_setup.bash}"
OUT_DIR="${OUT_DIR:-${PROJECT_ROOT}/Results/unreal_scene_mapping/${SCENE_ID}/fastlio_runtime_cpp_livox_headless_$(date +%Y%m%d_%H%M%S)}"
DURATION_SECONDS="${DURATION_SECONDS:-20}"
PROBE_SECONDS="${PROBE_SECONDS:-5}"
MAX_FRAMES="${MAX_FRAMES:-160}"
LIDAR_RATE_HZ="${LIDAR_RATE_HZ:-10.0}"
IMU_RATE_HZ="${IMU_RATE_HZ:-200.0}"
TRUTH_RATE_HZ="${TRUTH_RATE_HZ:-20.0}"
SCAN_DURATION_S="${SCAN_DURATION_S:-0.09}"
STARTUP_PRELOAD_SECONDS="${STARTUP_PRELOAD_SECONDS:-12}"
DRY_RUN="${DRY_RUN:-0}"
PROBE_SECONDS_FLOAT="$(python3 -c 'import sys; print(f"{float(sys.argv[1]):.6f}")' "${PROBE_SECONDS}")"
FIRST_MESSAGE_TIMEOUT_SECONDS="${FIRST_MESSAGE_TIMEOUT_SECONDS:-45}"
MIN_LIVOX_POINTS="${MIN_LIVOX_POINTS:-15000}"

cd "${PROJECT_ROOT}"
mkdir -p "${OUT_DIR}" "${ROS_LOG_DIR}"
export ROS_LOG_DIR

if [[ "${SCENE_ID}" != "factoryenvironmentcollect" ]]; then
  echo "Only factoryenvironmentcollect is currently wired for this headless gate." >&2
  exit 2
fi

MWORKS_RAW="${MWORKS_RAW:-Results/unreal_scene_mapping/${SCENE_ID}/mworks_smoke/raw/sunray150_ue_${SCENE_ID}_linear_mpc_smoke.csv}"
DEFAULT_LIVOX_FRAMES="Results/unreal_scene_mapping/${SCENE_ID}/livox_like_lidar_frames_mworks_body.jsonl"
DEFAULT_TRUTH_DATASET="Results/unreal_scene_mapping/${SCENE_ID}/fastlio_mworks_truth_dataset.jsonl"
if [[ ! -f "${DEFAULT_LIVOX_FRAMES}" ]]; then
  DEFAULT_LIVOX_FRAMES="Results/unreal_scene_mapping/${SCENE_ID}/livox_like_lidar_frames.jsonl"
fi
if [[ ! -f "${DEFAULT_TRUTH_DATASET}" ]]; then
  DEFAULT_TRUTH_DATASET="Results/unreal_scene_mapping/${SCENE_ID}/fastlio_replay_dataset.jsonl"
fi
LIVOX_FRAMES="${LIVOX_FRAMES:-${DEFAULT_LIVOX_FRAMES}}"
TRUTH_DATASET="${TRUTH_DATASET:-${DEFAULT_TRUTH_DATASET}}"
FASTLIO_CONFIG_DIR="${PROJECT_ROOT}/Config/ros2"
FASTLIO_CONFIG_FILE="mosim_fast_lio_ros2_mid360.yaml"

for required in "${ROS_SETUP}" "${LIVOX_UNDERLAY_SETUP}" "${FASTLIO_IMPORT_SETUP}" "${DENSE_LIDAR_SETUP}" "${MWORKS_RAW}" "${LIVOX_FRAMES}" "${TRUTH_DATASET}" "${FASTLIO_CONFIG_DIR}/${FASTLIO_CONFIG_FILE}"; do
  if [[ ! -e "${required}" ]]; then
    echo "Missing required artifact: ${required}" >&2
    exit 3
  fi
done

if [[ "${DRY_RUN}" == "1" ]]; then
  cat <<EOF
{
  "schema": "mosim.factory_fastlio_mid360_headless_dryrun.v1",
  "scene_id": "${SCENE_ID}",
  "output_dir": "${OUT_DIR#${PROJECT_ROOT}/}",
  "mworks_raw": "${MWORKS_RAW}",
  "livox_frames": "${LIVOX_FRAMES}",
  "truth_dataset": "${TRUTH_DATASET}",
  "fastlio_config": "Config/ros2/${FASTLIO_CONFIG_FILE}",
  "phases": ["dense_lidar_cpp", "mworks_imu_truth", "livox_input_probe", "fast_lio", "runtime_record", "truth_evaluation"],
  "claim": "dry-run only; no ROS2 process was launched"
}
EOF
  exit 0
fi

set +u
source "${ROS_SETUP}"
source "${LIVOX_UNDERLAY_SETUP}"
source "${FASTLIO_IMPORT_SETUP}"
source "${DENSE_LIDAR_SETUP}"
set -u

PIDS=()
cleanup() {
  for pid in "${PIDS[@]:-}"; do
    kill "${pid}" >/dev/null 2>&1 || true
  done
  wait >/dev/null 2>&1 || true
}
trap cleanup EXIT

wait_for_topic_once() {
  local topic="$1"
  local msg_type="$2"
  local out_name="$3"
  if ! timeout "${FIRST_MESSAGE_TIMEOUT_SECONDS}" ros2 topic echo \
      "${topic}" "${msg_type}" \
      --once \
      --qos-reliability reliable \
      --no-arr \
      --truncate-length 32 \
      >"${OUT_DIR}/${out_name}.stdout" 2>"${OUT_DIR}/${out_name}.stderr"; then
    echo "Timed out waiting for first ${topic} message; see ${OUT_DIR}/${out_name}.stderr" >&2
    return 4
  fi
}

ros2 run mosim_dense_lidar_cpp dense_lidar_replay_node --ros-args \
  -p lidar_jsonl:="${PROJECT_ROOT}/${LIVOX_FRAMES}" \
  -p topic:=/mosim/lidar_points \
  -p livox_topic:=/mosim/livox/lidar \
  -p frame_id:=base/mid360_link \
  -p rate_hz:="${LIDAR_RATE_HZ}" \
  -p scan_duration_s:="${SCAN_DURATION_S}" \
  -p max_frames:="${MAX_FRAMES}" \
  -p stats_interval_s:=5.0 >"${OUT_DIR}/dense_lidar_cpp.log" 2>&1 &
PIDS+=("$!")

wait_for_topic_once /mosim/livox/lidar livox_ros_driver2/msg/CustomMsg first_livox_message
sleep "${STARTUP_PRELOAD_SECONDS}"

ros2 run mosim_dense_lidar_cpp mworks_state_imu_replay_node --ros-args \
  -p mworks_raw_csv:="${PROJECT_ROOT}/${MWORKS_RAW}" \
  -p world_frame:=ue_world \
  -p body_frame:=base_link \
  -p imu_frame:=base/forward_imu_optical_frame \
  -p imu_topic:=/mosim/forward/imu \
  -p truth_odom_topic:=/mosim/truth/odometry \
  -p imu_rate_hz:="${IMU_RATE_HZ}" \
  -p truth_rate_hz:="${TRUTH_RATE_HZ}" \
  -p max_rows:="${MAX_FRAMES}" \
  -p stats_interval_s:=5.0 >"${OUT_DIR}/state_publisher.log" 2>&1 &
PIDS+=("$!")

wait_for_topic_once /mosim/forward/imu sensor_msgs/msg/Imu first_imu_message

ros2 run mosim_dense_lidar_cpp livox_imu_probe_node --ros-args \
  -p livox_topic:=/mosim/livox/lidar \
  -p imu_topic:=/mosim/forward/imu \
  -p duration_s:="${PROBE_SECONDS_FLOAT}" \
  -p min_points:="${MIN_LIVOX_POINTS}" \
  -p min_livox_rate_hz:=8.0 \
  -p min_imu_rate_hz:=150.0 \
  -p max_latest_time_delta_s:=0.2 >"${OUT_DIR}/probe_cpp.stdout.json" 2>"${OUT_DIR}/probe_cpp.stderr.log"

python3 - "${OUT_DIR}" <<'PY'
import json
import pathlib
import sys

out = pathlib.Path(sys.argv[1])
raw = (out / "probe_cpp.stdout.json").read_text(encoding="utf-8")
json_lines = [line for line in raw.splitlines() if line.strip().startswith("{")]
if not json_lines:
    raise SystemExit("C++ Livox/IMU probe produced no JSON report")
report = json.loads(json_lines[-1])
(out / "LIVOX_CUSTOMMSG_PROBE.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
if not all(report.get("acceptance", {}).values()):
    raise SystemExit(3)
PY

ros2 launch fast_lio mapping.launch.py \
  rviz:=false \
  config_path:="${FASTLIO_CONFIG_DIR}" \
  config_file:="${FASTLIO_CONFIG_FILE}" >"${OUT_DIR}/fast_lio.launch.log" 2>&1 &
PIDS+=("$!")

sleep 3

python3 Scripts/UE5/record_fastlio_ros2_runtime.py \
  --scene-id "${SCENE_ID}" \
  --output-dir "${OUT_DIR}" \
  --duration-seconds "${DURATION_SECONDS}" \
  --odom-topic /Odometry \
  --path-topic /path \
  --cloud-topic /cloud_registered >"${OUT_DIR}/recorder.stdout.json" 2>"${OUT_DIR}/recorder.stderr.log"

python3 Scripts/UE5/evaluate_fastlio_runtime.py \
  --scene-id "${SCENE_ID}" \
  --truth-dataset "${TRUTH_DATASET}" \
  --odometry-jsonl "${OUT_DIR}/fastlio_odometry.jsonl" \
  --output-json "${OUT_DIR}/FASTLIO_RUNTIME_EVALUATION.json" \
  --output-md "${OUT_DIR}/FASTLIO_RUNTIME_EVALUATION.md" \
  --align-start-time \
  --align-start-position \
  --align-start-yaw || true

python3 - "${OUT_DIR}" <<'PY'
import json
import pathlib
import sys

out = pathlib.Path(sys.argv[1])
summary = {
    "schema": "mosim.factory_fastlio_mid360_headless_summary.v1",
    "output_dir": str(out),
    "probe": json.loads((out / "LIVOX_CUSTOMMSG_PROBE.json").read_text(encoding="utf-8")) if (out / "LIVOX_CUSTOMMSG_PROBE.json").exists() else {},
    "recording": json.loads((out / "FASTLIO_RUNTIME_RECORDING.json").read_text(encoding="utf-8")) if (out / "FASTLIO_RUNTIME_RECORDING.json").exists() else {},
    "evaluation": json.loads((out / "FASTLIO_RUNTIME_EVALUATION.json").read_text(encoding="utf-8")) if (out / "FASTLIO_RUNTIME_EVALUATION.json").exists() else {},
}
(out / "HEADLESS_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
PY
