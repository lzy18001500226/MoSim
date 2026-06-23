# ROS2 Runtime Setup

> Last updated: 2026-06-04. Scope: WSL2 Ubuntu 22.04 runtime for UE scene
> mapping, RViz2 review, and FAST-LIO-family integration.

## Current Status

This workflow is not the current single-UAV Sunray review lane. On 2026-06-20
the user disabled the old Ubuntu-22.04 / ROS2 Humble / PX4 `x500_mid360`
experiment route after it was incorrectly used for current review work.

If the current task says Sunray, ROS1, Gazebo Classic, RViz, MID360 point
cloud, takeoff-hover-land, or figure-8 review, stop reading this file and use:

```text
Docs/Workflows/sunray_ros1_current_runtime_lane.md
Docs/Index/sunray_migration_index.md
```

This file is retained for historical/future ROS2 reference only and must not
be used as an escape hatch when the current ROS1/Sunray lane is blocked.

Current executable review work must use the ROS1/Sunray lane:

```text
Ubuntu-20.04 / ROS1 Noetic
-> References/Sunray
-> reviewed assembled Sunray150 + MID360 model and parameters
-> Gazebo Classic
-> RViz point cloud and trajectory/path review
```

Do not run or cite `x500_mid360`, `px4_mid360_obstacle_light`, or the disabled
FAST-LIO external-vision PX4 route as current MoSim evidence. Historical output
under `Results/px4_gazebo/` is explicitly disabled by
`Results/px4_gazebo/DISABLED_OLD_ROS2_PX4_EXPERIMENTS.md`.

## Decision

Ubuntu 22.04 ROS2 Humble is retained only for future/reference work such as
later generated-code/PX4 experiments or UE mapping research after explicit
reopening. It is not the active lane for the current Sunray/Gazebo/RViz audit.

FishROS remains an acceptable operator-facing installer, but its `install.py`
entrypoint is an interactive dispatcher. For unattended project setup, use the
official ROS2 Humble apt route and record the exact package state.

## External Paths

This workflow is a project infrastructure exception to the default filesystem
boundary. It may read or write:

```text
/etc/apt/
/usr/share/keyrings/
/opt/ros/humble/
/var/lib/apt/
/var/cache/apt/
~/.bashrc       # only if the user explicitly asks for permanent sourcing
```

Do not write passwords, tokens, or account data into tracked project files.

## Install Route

Primary automated route, based on official ROS2 Humble Ubuntu deb packages:

```bash
sudo apt install -y software-properties-common curl gnupg lsb-release
sudo add-apt-repository -y universe
sudo apt update

export ROS_APT_SOURCE_VERSION="$(
  curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest \
    | grep -F tag_name | awk -F'"' '{print $4}'
)"
curl -L -o /tmp/ros2-apt-source.deb \
  "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb

sudo apt update
sudo apt install -y \
  ros-humble-desktop \
  python3-colcon-common-extensions \
  python3-rosdep \
  python3-vcstool \
  python3-argcomplete \
  python3-pip
```

Use FishROS only when manual interactive installation is desired:

```bash
wget http://fishros.com/install -O fishros && bash fishros
```

## Source And Verify

Temporary source for the current shell:

```bash
source /opt/ros/humble/setup.bash
ros2 pkg prefix rviz2
rviz2 --help
colcon --help
```

`ros2 --version` is not a valid ROS2 Humble CLI check. Use package prefix,
`rviz2 --help`, or Python imports instead.

If a script uses `set -u`, temporarily disable nounset around ROS setup:

```bash
set +u
source /opt/ros/humble/setup.bash
set -u
```

Project preflight:

```bash
python3 Scripts/UE5/check_ros_mapping_runtime_env.py --write
```

Expected result after installation:

```text
ros_generation = ros2
ROS_DISTRO = humble
rviz2 is available
colcon is available
ROS2 mapping dry-runs pass
```

Prior validated host state on 2026-06-01:

```text
ROS_DISTRO=humble
ros2=/opt/ros/humble/bin/ros2
rviz2=/opt/ros/humble/bin/rviz2
colcon=/usr/bin/colcon
ROS apt key=/usr/share/keyrings/ros-archive-keyring.gpg
ROS apt source=/etc/apt/sources.list.d/ros2.list
source=deb [arch=amd64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu jammy main
apt update probe=passed with no NO_PUBKEY/EXPKEYSIG error
rosbridge_server=installed
rosbridge port 9090=listening after manual launch
```

Status summary from that 2026-06-01 infrastructure check: native ROS2
Humble/RViz2/colcon was working, and the ROS apt key problem was resolved by
the keyring/source pair above. Treat this as prior infrastructure evidence,
not a current live-host guarantee. Re-run the preflight or a targeted live
probe before claiming the current apt, rosbridge, or port state.

Set ROS runtime logs to a project-local path before launching ROS2 nodes:

```bash
export ROS_LOG_DIR=/mnt/c/Users/HP/Desktop/MoSim/Results/tmp/ros_logs
```

The project ROS2 wrappers set this automatically. Direct `ros2 launch` and
`rclpy.init()` calls can fail in restricted agent sandboxes if ROS tries to
write `/home/linux/.ros/log`.

## Gazebo WSL GPU And Model Lookup

For Gazebo GUI review and normal live Gazebo runtime in WSL, use the project
environment wrapper:

```bash
source Scripts/gazebo/setup_gazebo_wsl_env.sh
```

Default behavior:

- Uses WSLg OpenGL through NVIDIA D3D12 when available:
  `MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA`.
- Leaves `LIBGL_ALWAYS_SOFTWARE` unset. Do not use software rendering for GUI
  review unless explicitly debugging a headless or driver failure.
- Restricts Gazebo model lookup to project-local
  `Config/gazebo/models` through `GZ_SIM_RESOURCE_PATH` and
  `IGN_GAZEBO_RESOURCE_PATH`. Do not inherit global model/resource paths unless
  `MOSIM_GAZEBO_INHERIT_RESOURCE_PATHS=1` is explicitly needed for a bounded
  diagnostic.

Historical ROS2 single-UAV map review launch:

```bash
RESULT_DIR=Results/gazebo_ros2/gazebo_map_review_manual START_PAUSED=1 BACKGROUND=1 \
  bash Scripts/gazebo/launch_gazebo_map_review.sh
```

Use `MOSIM_GAZEBO_SOFTWARE_RENDERING=1` only as a fallback diagnostic. It is
not the normal path for performance or visual-review evidence.

## Historical Gazebo Execution Route

This section records the old ROS2/PX4/Gazebo route for future reference. It is
not the current Sunray ROS1 review lane. For current Sunray takeoff-hover-land,
8-shaped mission, Gazebo Classic animation, RViz trajectory/path, or MID360
point-cloud review, use `Docs/Workflows/sunray_ros1_current_runtime_lane.md`.

Historical ROS2/PX4 route details:

```text
scenario: Config/scenarios/system/sunray150_single_uav_competition_light.yaml
world:    Config/gazebo/worlds/sunray150_single_uav_competition_light.sdf
model:    Config/gazebo/models/sunray150_assembled/model.sdf
vehicle:  sunray150_assembled
control namespace/topic family: sunray150
```

Do not substitute the old block/primitive aircraft, `factory_minimal`, or a
global Gazebo model path when this lane is being validated. The visible vehicle
must remain the accepted assembled/textured Sunray150 mesh. Simplified rotor
links and collision primitives are physics/plugin internals only.

Architecture boundary, 2026-06-20:

```text
formal deployment route:
  MWORKS Sysblock -> GenerateModelCode -> generated C/C++ -> SIL
  -> PX4 Offboard adapter or PX4 module/uORB adapter
  -> PX4 SITL -> Gazebo plant/sensors -> ROS2 perception/planning/review

fixture route:
  ControllerOutput -> ROS2 actuator bridge -> Gazebo motor topic
```

The fixture route is retained for message, actuator-order, stale-command,
plant-sanity, point-cloud, local-map, and visual-review debugging. It must not
be reported as formal generated-controller deployment, PX4 integration, final
closed-loop acceptance, or competition controller performance.

### Disabled PX4-native single-UAV flight stages

The following PX4-native stages are historical/future-reference only. They are
not current Sunray ROS1 review commands, and must not be run unless the user
explicitly reopens the PX4/ROS2 route.

```bash
# 0. PX4 + Gazebo x500 + uXRCE-DDS baseline. No arm, no Offboard, no setpoints.
RESULT_DIR=Results/px4_gazebo/px4_gz_x500_baseline_current \
PX4_DIR=/mnt/c/Users/HP/Desktop/MoSim/Results/tmp/px4_gitwork/PX4 \
HEADLESS=1 TOPIC_WAIT_S=150 STARTUP_TIMEOUT_S=360 \
  bash Scripts/px4/run_px4_gz_x500_baseline.sh

# 1. Safe Offboard adapter topic smoke. No arm, no Offboard mode switch.
RESULT_DIR=Results/px4_gazebo/px4_offboard_adapter_live_smoke_current \
PX4_DIR=/mnt/c/Users/HP/Desktop/MoSim/Results/tmp/px4_gitwork/PX4 \
HEADLESS=1 TOPIC_WAIT_S=150 STARTUP_TIMEOUT_S=360 \
  bash Scripts/px4/run_px4_offboard_adapter_live_smoke.sh
```

The next scripts to add and run are, in order:

```text
Scripts/px4/run_px4_offboard_takeoff_hover_land.sh
Scripts/px4/run_px4_offboard_figure8_gate.sh
Scripts/px4/run_px4_generated_controller_matrix.sh
```

Required evidence for those gates:

```text
takeoff-hover-land:
  - vehicle_status, command_ack, local_position or odometry, land_detected;
  - input offboard_control_mode and trajectory_setpoint stream;
  - Gazebo truth pose;
  - metrics: XY drift, hover Z error, yaw drift, tilt, landing slide/spin,
    failsafe status.

figure8:
  - expected path and actual path in one frame;
  - start XY equals takeoff XY;
  - takeoff, settle, two continuous figure8 loops, settle, land;
  - RMSE, max error, velocity continuity, yaw stability, no post-landing slide.
```

Only after those PX4-native gates pass should the run restore the full obstacle
map and connect FAST-LIO/EGO as autonomous navigation components.

### Gazebo/ROS2 fixture and review stages

Run these Gazebo stages only for model, sensor, visual review, local map, and
fixture diagnostics. Each stage may claim only its own evidence:

```bash
# 0. Static and dependency preflight.
python Scripts/quality/check_gazebo_ros2_smoke_contract.py
bash Scripts/gazebo/check_gazebo_ros2_dependencies.sh
DRY_RUN=1 bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh

# 1. Human visual map/model review.
RESULT_DIR=Results/gazebo_ros2/gazebo_map_review_manual START_PAUSED=1 BACKGROUND=1 \
  bash Scripts/gazebo/launch_gazebo_map_review.sh

# 2. Gazebo sensor + ROS2 bridge + TF + local voxel/grid smoke.
RESULT_DIR=Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_sensor_local_map_current \
RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_LOCAL_MAP=1 RUN_TOPIC_CHECK=1 RUN_RATE_CHECK=1 RUN_STATIC_TF=1 RUN_TF_CHECK=1 \
  bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh

# 3. ControllerOutput -> Actuators topic handoff only. Fixture, not PX4 deployment.
RESULT_DIR=Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_controller_output_node_handoff_current \
RUNTIME_GATE_PROFILE=controller_output_node_handoff \
RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_ACTUATOR_BRIDGE=1 RUN_CONTROLLER_OUTPUT_NODE=1 RUN_CONTROLLER_OUTPUT_FIXTURE=1 \
RUN_ACTUATOR_COMMAND_CHECK=1 RUN_LOCAL_MAP=0 RUN_TOPIC_CHECK=0 RUN_RATE_CHECK=0 RUN_STATIC_TF=0 RUN_TF_CHECK=0 \
BUILD_MOSIM_ROS2_MSGS=0 TIMEOUT_SECONDS=20 \
  bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh

# 4. FAST-LIO/planner input surface only. This is degraded while MID360 is gpu_lidar.
RESULT_DIR=Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_fastlio_planner_input_current \
RUNTIME_GATE_PROFILE=fastlio_planner_input \
RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_FASTLIO_PLANNER_INPUT_ADAPTER=1 RUN_TOPIC_CHECK=1 RUN_RATE_CHECK=1 \
RUN_STATIC_TF=1 RUN_TF_CHECK=1 TIMEOUT_SECONDS=20 \
  bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh

# 5. Hover-hold pre-acceptance only after the assembled-world service and truth
# topic are derived from the scenario, not hard-coded to factory_minimal.
RESULT_DIR=Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_hover_hold_closed_loop_pre_acceptance_current \
  bash Scripts/gazebo/run_sunray150_hover_hold_closed_loop.sh
```

Stage 2 can support live Gazebo/ROS2 point-cloud and local voxel/grid smoke.
Stage 3 can support only fixture command-topic conversion and echo. Stage 4 can
support only input-shape/topic/frame/rate handoff while the current sensor
source is a regular `gpu_lidar`. Stage 5 is a bounded truth-feedback
hover-hold pre-acceptance gate, not final controller performance, PX4
deployment, or final closed-loop acceptance.

### Current Gazebo Truth Source

For the light competition world, do not use the registered PosePublisher topic
as the current truth source. The discovered model/link PosePublisher topic
registers a publisher but did not emit samples in the current world during the
2026-06-17 probes. The accepted truth source is Gazebo transport state:

```text
topic: /world/sunray150_single_uav_competition_light/state
message surface: SerializedStepMap state
recorder: Scripts/gazebo/capture_gazebo_state_truth_topic.py
summary: GAZEBO_TRUTH_POSE_RECORDING.json
samples: gazebo_truth_pose.jsonl
entity selection: nearest assembled UAV body to initial pose (0,0,1.2)
current evidence: Results/gazebo_ros2/sunray150_single_uav_competition_light_truth_state_probe_20260617_002/GAZEBO_TRUTH_POSE_RECORDING.json
```

This source clears the truth-capture blocker for same-run estimator/planner
comparison. It does not prove hover, trajectory tracking, final plant
closed-loop behavior, or competition controller performance. While the
`MulticopterMotorModel` blocks remain disabled or replaced by truth/pose
feedback, all trajectory or avoidance results are scaffold/pre-acceptance and
must carry that label.

### Current MID360 Sensor Blocker

The current assembled model still uses a regular Gazebo `gpu_lidar`, not a
Livox scan-mode plugin:

```text
sensor type: gpu_lidar
shape:       500 x 40
topic:       /mosim/gazebo/lidar_points
rate:        10 Hz
fov:         horizontal 360 deg, vertical approximately -7 deg to 52 deg
range:       0.1 m to 40 m
points:      20,000 points/frame, about 200,000 points/s at 10 Hz
```

This is acceptable as a short-term live point-cloud/local-map review source for
density, scan range, FOV, ROS2 transport, and RViz/local-map integration. The
`40 m` maximum range is the conservative low-reflectivity review/planning limit
for this Gazebo lane. Do not convert it into a high-reflectivity maximum-range
claim, because the current Gazebo sensor does not model target reflectivity.
It is not a physically credible Livox MID360 source because the scan is still a
regular raster. The Sunray/YunZong reference MID360 route uses a Livox
simulation plugin and scan CSV such as `mid360-real-centr.csv`, with per-point
line/offset-time semantics and `samples=20000` at 10Hz. The current
`gazebo_fastlio_planner_input_adapter.py` row-buckets regular PointCloud2 rows
into a Livox-like `CustomMsg`; that is a compatibility smoke adapter, not a
replacement for a real MID360 non-repetitive scan pattern.

The review display must also not be confused with the sensor model. For RViz
review, use a native LiDAR display similar to the Sunray/EGO references:
`Style=Points`, `Size (Pixels)=1`, `Size (m)=0.003`, `Decay Time=0`, and a
dedicated review topic. The current LiDAR review surface is
`/mosim/review/lidar_points_map_accumulated`, a human-review-only accumulation
of multiple unfiltered map-frame LiDAR frames. It is deliberately separate from
`/mosim/planner/global_points`, which is filtered planner input for EGO.
If the visual still looks sparse, inspect the sidecar point counts before
changing the sensor: the 2026-06-16 run had `raw_point_count=20000` but only
`finite_point_count=4187` in the current scene. That means many rays returned
no finite hit; it does not mean the raw frame shape was reduced to 4187 points.

EGO local map review is a separate surface. The EGO port publishes
`/grid_map/occupancy` and `/grid_map/occupancy_inflate` as XYZ voxel-center
`PointCloud2` messages without `intensity`, so RViz must use `AxisColor` or a
derived display topic if colored voxels are required. The default manual review
does not display the raw EGO topics directly. It displays review-only z-filtered
topics `/mosim/review/occupancy_above_floor` and
`/mosim/review/occupancy_inflate_above_floor`, both generated by
`Scripts/ros/filter_pointcloud_by_z.py` from the corresponding EGO source
topic with `REVIEW_OCCUPANCY_MIN_Z=0.95`. Do not judge LiDAR range
or MID360 scan density from EGO occupancy topics because the EGO local map also
applies local update and max-ray-length limits.

Current FAST-LIO/EGO evidence, 2026-06-19:

```text
FAST-LIO source runtime gate:
  Results/gazebo_ros2/single_uav_spark_fastlio_localization_gate_20260619_024023/RUNTIME_STATUS.json
  /mosim/gazebo/lidar_points/points: 20000 PointCloud2 points/frame
  /mosim/spark_fastlio/livox/lidar: Livox CustomMsg point_num=5376
  /cloud_registered: real Spark FAST-LIO output in map, 33 recorded frames
  /odometry: 1911 records
  /path: 3 records
  truth eval: FASTLIO_TRUTH_ERROR_EVAL.json, origin-aligned RMSE=0.007244m
  boundary: FAST-LIO localization/map output only; no planner, no setpoint, no closed_loop

EGO bspline/local-map gate:
  Results/gazebo_ros2/single_uav_real_ego_bspline_gate_20260619_025648/REAL_EGO_BSPLINE_GATE.json
  inputs: /mosim/planner/odom and /mosim/planner/global_points
  /grid_map/occupancy_inflate: width=8280, recorder finite points=8237
  /planning/bspline: sampled, final_plan_success_true=true
  measured rates: raw LiDAR about 9.95Hz, planner cloud about 3.38Hz,
    EGO occupancy/inflate about 9.94Hz
  boundary: planner map/bspline surface only; no traj_server, controller output,
    actuator command, closed_loop, controller performance, or multi-UAV readiness
```

Do not compare a single raw LiDAR RViz display directly against FAST-LIO's
accumulated map. FAST-LIO `/cloud_registered` is the continuously updated
localization/mapping output from the source runtime. Raw Gazebo LiDAR is one
sensor frame; `/mosim/review/lidar_points_map_accumulated` is a review-only
multi-frame accumulation; EGO occupancy/inflate is a planner local-map product.
They answer different review questions and should be displayed in separate
RViz layouts when judging density, mapping growth, and planner obstacles.

The EGO local-map input must not be the same acceptance surface as raw LiDAR.
Use the raw Gazebo/MoSim LiDAR topics and
`/mosim/review/lidar_points_map_accumulated` for raw sensor density/FOV/color/
frequency review, and use the planner cloud only as the local-map obstacle
input. The project-owned adapter applies planner-cloud-only filtering before
publishing `/uav1/global_points` and `/mosim/planner/global_points`: points
below the configured map-frame ground threshold and points inside the
configured UAV self-filter cylinder are written as NaN. Raw LiDAR,
review-cloud, and FAST-LIO compatibility topics stay unchanged. EGO's
`cloudCallback` consumes finite XYZ points as obstacles; it does not
semantically classify ground or self returns. Therefore, a ground disk or body
blob under the UAV in `/grid_map/occupancy_inflate` is a planner-input
preprocessing fault, not an RViz styling problem. Debug it by checking the
adapter `planner_cloud_filter` sidecar and the `planner_cloud_map_frame`
sample before changing the visual display.

Manual review entrypoints:

```bash
# LiDAR-only review: raw LiDAR / planner input cloud density, intensity, rate, FOV.
bash Scripts/gazebo/open_real_lidar_only_rviz_review.sh

# EGO review: LiDAR plus EGO occupancy/inflated voxel windows, with
# planner-cloud-only ground/self filtering enabled by default.
bash Scripts/gazebo/open_real_ego_rviz_review.sh

# Gazebo animation review: accepted sunray150_assembled model, visible props,
# follow camera, figure-8/static-obstacle control chain.
bash Scripts/gazebo/run_sunray150_figure8_animation_review.sh

# Full single-UAV manual review: full obstacle world, Gazebo follow camera, and
# two RViz windows for LiDAR/path and occupancy/path review.
bash Scripts/gazebo/open_single_uav_figure8_full_review.sh
```

For tomorrow's review, keep Gazebo animation and RViz evidence separate:
Gazebo is the plant/animation surface; RViz is the point-cloud, FAST-LIO map,
EGO occupancy/inflate, bspline, and trajectory surface. The preferred review
setup is one Gazebo window plus two RViz windows: FAST-LIO/trajectory and
EGO occupancy/bspline. If only one RViz window is available, use tabs/layout
switching rather than overlaying raw LiDAR, accumulated FAST-LIO map, EGO
inflated voxels, and trajectory until scale and colors become ambiguous.

The default full single-UAV review entrypoint is
`Scripts/gazebo/open_single_uav_figure8_full_review.sh`. It launches the full
assembled obstacle world
`Config/gazebo/worlds/yunzong_planning_test_sunray150_assembled.sdf`, keeps the
accepted `sunray150_assembled` model, enables Gazebo camera follow by default,
and opens two RViz windows:

```text
Config/rviz2/mosim_real_ego_lidar_cloud_review.rviz
  /mosim/review/lidar_points_map_accumulated
  /mosim/review/actual_path
  /mosim/review/reference_path

Config/rviz2/mosim_figure8_local_map_review.rviz
  /mosim/local_occupancy_voxels
  /mosim/review/actual_path
  /mosim/review/reference_path
```

Gazebo and RViz can be independent WSLg child windows under the same Windows
`msrdc.exe` process. If Windows window enumeration only shows an RViz title
while Gazebo is still running, inspect the WSL X tree with
`xwininfo -root -tree` and raise/minimize child windows with `xdotool`. This is
a review-window operation only; it does not change simulation state.

Landing/ground handling for the current truth-feedback Gazebo controller:

- `takeoff_hold_setpoint_until_stable` may raise external setpoints to
  `pre_setpoint_hold_z` only before the first real airborne phase. It must not
  override a landing or post-land ground reference back to 1.2 m.
- Ground lock may latch only after the vehicle has actually become airborne
  (`position.z >= takeoff_xy_enable_altitude_m` or XY tracking entered), never
  during the initial pre-takeoff ground hold.
- Once post-flight ground lock is active, publish
  `ground_motor_command=0.0`, disable XY tracking, and hold the current ground
  XY position. This prevents the post-landing slide/spin failure where residual
  motor speed or a rebound to `pre_setpoint_hold_z` drives the vehicle across
  the floor.
- A complete review run must check the controller sidecar, not only the visual
  frame. The post-land sidecar should show final target altitude near 0.05 m,
  final velocity near zero, `ground_lock_latched=true`, and final motor command
  `[0.0, 0.0, 0.0, 0.0]`.

Current landing-fix evidence, 2026-06-19:

```text
short state-machine smoke:
  Results/gazebo_ros2/sunray150_takeoff_smoke_landing_lock_fix_20260619_173539/figure8_setpoint_tracker.json
  z_range.max=1.123855
  last command=[0.0, 0.0, 0.0, 0.0]

full obstacle visual review:
  Results/gazebo_ros2/sunray150_single_uav_figure8_full_review_landing_fix3_20260619_173750/figure8_setpoint_tracker.json
  z_range.max=1.104668
  last position=[-0.588337, 0.99251, 0.035999]
  last target_position=[-0.588337, 0.99251, 0.05]
  last raw_reference_position=[-0.6, 1.0, 0.05]
  last velocity=[0.0, 0.0, 0.0]
  last command=[0.0, 0.0, 0.0, 0.0]
  ground_lock_latched=true

same-run RViz/path sidecars:
  rviz_review_paths.json truth_points=4479, reference_points=1245
  review_fastlio_planner_input_adapter.json review_accumulated_last_point_count=44065
```

This evidence resolves the specific post-landing slide/spin regression for the
current truth-feedback figure-8 review lane. It does not by itself claim final
competition controller performance, FAST-LIO localization quality, planner
readiness, UE acceptance, or multi-UAV readiness.

The default EGO review filter is intentionally review-oriented:
`PLANNER_FILTER_GROUND_MIN_Z=0.95`, `PLANNER_SELF_FILTER_RADIUS_XY=1.0`,
`PLANNER_SELF_FILTER_Z_MIN=-0.8`, `PLANNER_SELF_FILTER_Z_MAX=0.8`,
`REVIEW_ACCUMULATED_FRAMES=5`, `REVIEW_ACCUMULATED_MAX_POINTS=100000`,
and `REVIEW_RECORDER_MAX_POINTS=100000`. Tune
these as runtime evidence parameters, not as hidden RViz fixes. These defaults
are conservative for the current hover-at-1.2m review pose: they suppress the
flat floor/platform and near-UAV returns from EGO input while preserving
obstacle columns above the ground threshold. Do not use long multi-second
accumulation to make the cloud look dense: it can slow the adapter/RViz and
make the cloud appear and disappear as display decay catches up with the
publish cadence. The 2026-06-16 stable review run
`Results/gazebo_ros2/sunray150_real_ego_review_density5_stable_20260616_008`
used 5 accumulated frames and recorded
`review_accumulated_cloud_map_frame.width=38940`; the adapter's last
accumulated point count was `38790`, roughly 5x the same-run finite scene hit
count of `7758`. Use that accumulated review topic for the human visual-density
claim rather than first-frame raw LiDAR counts.

The RViz review scripts run a generated zero-gravity copy of the world by
default (`REVIEW_WORLD_HOLD_MODE=zero_gravity`) so the uncommanded dynamic UAV
does not fall during a sensor/map review. This is review evidence only. Do not
use the zero-gravity generated world for dynamics, actuator, hover, controller,
or closed-loop claims.

The LiDAR RViz window must use
`/mosim/review/lidar_points_map_accumulated`, an unfiltered multi-frame
map-frame review cloud. `/mosim/review/lidar_points_map` remains the unfiltered
single-frame review topic. The EGO planner consumes the filtered
`/mosim/planner/global_points` surface. Do not use the filtered planner cloud
as the visual reference for MID360 density/color review.

The EGO grid RViz window must use the review topics above. If a yellow or low
voxel sheet appears, first confirm whether RViz is showing
`/mosim/review/occupancy_above_floor`,
`/mosim/review/occupancy_inflate_above_floor`, or a stale/raw
`/grid_map/occupancy*` display. A filtered inflated layer with minimum z around
`1.04 m` is EGO obstacle inflation around valid obstacle points, not direct raw
floor leakage. Changing EGO `obstacles_inflation`, resolution, or z-inflation
is an algorithm behavior change and needs a separate planner decision.

Trajectory visualization is a ROS/RViz review surface, not Gazebo world
geometry. The accepted pattern follows common planning demos such as
NeXTzhao/planning: publish the actual vehicle trajectory and reference/planner
trajectory as ROS path or marker topics, then render them in RViz. Do not make
Gazebo cylinder/entity segments the default trajectory evidence; they are heavy,
can be scaled or framed incorrectly, and can contaminate visual review. For the
current single-UAV figure-8 gate, use
`Scripts/ros/publish_gazebo_review_paths.py` to publish:

```text
/mosim/review/actual_path      nav_msgs/msg/Path, red actual UAV center path
/mosim/review/reference_path   nav_msgs/msg/Path, green figure-8 reference path
```

Gazebo remains the aircraft/world animation surface: it shows the assembled
Sunray150 model, propellers, map, takeoff, 8-shaped motion, and landing. RViz is
the trajectory, point-cloud, occupancy-grid, planner, and localization review
surface. A visual acceptance run should therefore inspect both surfaces when
trajectory quality is in scope: Gazebo for body attitude and scene animation,
RViz for path continuity, reference-vs-actual shape, point cloud, and local map.
Marker publication logs alone are not visual acceptance; screenshots or live
review must confirm the line is visible and tied to the UAV center.

Reference spec: Livox MID-360 official specs list detection range `40 m @ 10%
reflectivity` and `70 m @ 80% reflectivity`, close-proximity blind zone
`0.1 m`, FOV `horizontal 360 deg, vertical -7 deg to 52 deg`, point rate
`200,000 points/s`, and typical frame rate `10 Hz`:
`https://www.livoxtech.com/mid-360/specs`.

Until a Gazebo Fortress-compatible MID360/Livox source is implemented and
validated, do not claim:

- correct MID360 scan pattern;
- reflectivity-dependent MID360 detection range;
- physically credible FAST-LIO MID360 input;
- FAST-LIO localization quality from sensor realism;
- planner readiness;
- closed-loop autonomy.

ROS-MCP note: the project checkout supports both ROS and ROS2, but it talks to
the active ROS runtime through rosbridge. On this host, that means ROS2 Humble
plus `ros-humble-rosbridge-suite`. The WSL wrapper
`/home/linux/mcp-wrappers/ros_mcp.sh` auto-starts `rosbridge_websocket` in the
background when Codex starts ROS-MCP and port `9090` is absent, then reuses it
for later MCP calls.

Current project commands that exist in this checkout:

```bash
DRY_RUN=1 MAX_FRAMES=2 START_RVIZ=0 Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh factoryenvironmentcollect
DRY_RUN=1 Scripts/UE5/run_factory_fastlio_mid360_headless_ros2.sh
REVIEW_DRY_RUN=1 OPEN_UE=0 OPEN_RVIZ=0 Scripts/UE5/review_scene_mapping_loop.sh factoryenvironmentcollect
DRY_RUN=1 Scripts/UE5/check_fastlio_ros2_topics.sh
```

Current project-owned Gazebo+ROS2 fixture/pre-acceptance entry:

Use this lane only after the controller has a declared MWORKS reference or an
explicit behavior-equivalent validation backend, and label the claim precisely.
The Gazebo+ROS2 lane validates runtime transport, actuator handoff, sensor/map
integration, and bounded plant-response slices. It does not replace
MWORKS/Syslab controller-performance evidence and it does not prove formal
generated-controller deployment. Formal external deployment must follow
`Docs/Workflows/mworks_codegen_controller_runtime.md`: generated C/C++,
SIL, PX4 Offboard or PX4 module/uORB integration, then same-run PX4+Gazebo
gates.

```bash
# A. Source/static and local unit checks.
python Scripts/quality/check_gazebo_ros2_smoke_contract.py
python -m pytest Scripts/tests/test_pointcloud_to_local_voxel_map_core.py -q
python Scripts/quality/build_ue_truth_local_voxel_map_fixture.py
python -m pytest Scripts/tests/test_ue_truth_local_voxel_map_fixture.py -q
python Scripts/ros/controller_output_to_gazebo_actuators.py --command 0.5 0.5 0.5 0.5
bash Scripts/gazebo/check_gazebo_ros2_dependencies.sh
DRY_RUN=1 bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh

# B. Sensor/local-map smoke. No controller authority.
RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_ACTUATOR_BRIDGE=1 RUN_LOCAL_MAP=1 RUN_TOPIC_CHECK=1 RUN_RATE_CHECK=1 RUN_STATIC_TF=1 RUN_TF_CHECK=1 \
  bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh

# C. ControllerOutput -> actuator transport only. No hover or performance.
RESULT_DIR=Results/gazebo_ros2/sunray150_gazebo_ros2_actuator_handoff RUNTIME_GATE_PROFILE=actuator_handoff \
  RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_ACTUATOR_BRIDGE=1 RUN_CONTROLLER_COMMAND=1 RUN_ACTUATOR_COMMAND_CHECK=1 \
  RUN_LOCAL_MAP=0 RUN_TOPIC_CHECK=0 RUN_RATE_CHECK=0 RUN_STATIC_TF=0 RUN_TF_CHECK=0 \
  bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh
RESULT_DIR=Results/gazebo_ros2/sunray150_gazebo_ros2_controller_output_node_handoff RUNTIME_GATE_PROFILE=controller_output_node_handoff \
  RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_ACTUATOR_BRIDGE=1 RUN_CONTROLLER_OUTPUT_NODE=1 RUN_CONTROLLER_OUTPUT_FIXTURE=1 \
  RUN_ACTUATOR_COMMAND_CHECK=1 RUN_LOCAL_MAP=0 RUN_TOPIC_CHECK=0 RUN_RATE_CHECK=0 RUN_STATIC_TF=0 RUN_TF_CHECK=0 \
  BUILD_MOSIM_ROS2_MSGS=0 TIMEOUT_SECONDS=20 bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh

# C1. Simple plant sanity with same-run feedback. This is the current
# executable pre-MWORKS-runtime gate for takeoff, hover, and land.
RESULT_DIR=Results/gazebo_ros2/sunray150_takeoff_hover_land_plant_sanity_current \
  BUILD_MOSIM_ROS2_MSGS=0 bash Scripts/gazebo/run_sunray150_takeoff_hover_land_gate.sh

# C2. MWORKS CSV ControllerOutput replay. Interface bridge only. A blocked
# plant response here means open-loop replay is not a valid closed-loop
# deployment claim.
RESULT_DIR=Results/gazebo_ros2/mworks_controller_output_replay_gate_current \
  BUILD_MOSIM_ROS2_MSGS=0 bash Scripts/gazebo/run_mworks_controller_output_replay_gate.sh

# D. Perception/planner-input surfaces. No setpoint or controller output.
RESULT_DIR=Results/gazebo_ros2/sunray150_gazebo_ros2_fastlio_planner_input RUNTIME_GATE_PROFILE=fastlio_planner_input \
  RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_FASTLIO_PLANNER_INPUT_ADAPTER=1 RUN_TOPIC_CHECK=1 RUN_RATE_CHECK=1 \
  RUN_STATIC_TF=1 RUN_TF_CHECK=1 bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh
RESULT_DIR=Results/gazebo_ros2/sunray150_gazebo_ros2_spark_fastlio_localization RUNTIME_GATE_PROFILE=spark_fastlio_localization \
  RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_FASTLIO_PLANNER_INPUT_ADAPTER=1 RUN_SPARK_FASTLIO=1 \
  RUN_TOPIC_CHECK=1 RUN_RATE_CHECK=0 RUN_STATIC_TF=1 RUN_TF_CHECK=1 TIMEOUT_SECONDS=12 \
  bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh
RESULT_DIR=Results/gazebo_ros2/sunray150_gazebo_ros2_planner_handoff_without_setpoint_publication RUNTIME_GATE_PROFILE=planner_handoff_without_setpoint_publication \
  RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_FASTLIO_PLANNER_INPUT_ADAPTER=1 RUN_TOPIC_CHECK=1 RUN_RATE_CHECK=1 \
  RUN_STATIC_TF=1 RUN_TF_CHECK=1 RUN_LOCAL_MAP=0 RUN_SPARK_FASTLIO=0 RUN_CONTROLLER_COMMAND=0 \
  RUN_CONTROLLER_OUTPUT_NODE=0 RUN_CONTROLLER_OUTPUT_FIXTURE=0 RUN_ACTUATOR_COMMAND_CHECK=0 \
  bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh

# E. Planner-output surface without actuation. No controller output.
RESULT_DIR=Results/gazebo_ros2/sunray150_gazebo_ros2_ego_style_planner_output_without_actuation RUNTIME_GATE_PROFILE=ego_style_planner_output_without_actuation \
  RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_FASTLIO_PLANNER_INPUT_ADAPTER=1 RUN_EGO_STYLE_PLANNER_OUTPUT=1 \
  RUN_TOPIC_CHECK=1 RUN_RATE_CHECK=1 RUN_STATIC_TF=1 RUN_TF_CHECK=1 RUN_LOCAL_MAP=0 RUN_SPARK_FASTLIO=0 \
  RUN_CONTROLLER_COMMAND=0 RUN_CONTROLLER_OUTPUT_NODE=0 RUN_CONTROLLER_OUTPUT_FIXTURE=0 RUN_ACTUATOR_COMMAND_CHECK=0 \
  BUILD_MOSIM_ROS2_MSGS=0 TIMEOUT_SECONDS=20 bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh
RESULT_DIR=Results/gazebo_ros2/sunray150_gazebo_ros2_ego_style_planner_output_without_actuation_20260615_005 RUNTIME_GATE_PROFILE=ego_style_planner_output_without_actuation \
  RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_FASTLIO_PLANNER_INPUT_ADAPTER=1 RUN_FASTLIO_IMU_PASSTHROUGH=1 RUN_EGO_STYLE_PLANNER_OUTPUT=1 \
  RUN_TOPIC_CHECK=1 RUN_RATE_CHECK=1 RUN_STATIC_TF=1 RUN_TF_CHECK=1 RUN_LOCAL_MAP=0 RUN_SPARK_FASTLIO=0 \
  RUN_CONTROLLER_COMMAND=0 RUN_CONTROLLER_OUTPUT_NODE=0 RUN_CONTROLLER_OUTPUT_FIXTURE=0 RUN_ACTUATOR_COMMAND_CHECK=0 \
  BUILD_MOSIM_ROS2_MSGS=1 TIMEOUT_SECONDS=20 bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh
RESULT_DIR=Results/gazebo_ros2/sunray150_gazebo_ros2_command_acknowledgement_without_closed_loop RUNTIME_GATE_PROFILE=command_acknowledgement_without_closed_loop \
  RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_ACTUATOR_BRIDGE=1 RUN_CONTROLLER_OUTPUT_NODE=1 RUN_CONTROLLER_OUTPUT_FIXTURE=1 \
  RUN_ACTUATOR_COMMAND_CHECK=1 RUN_COMMAND_ACK_GUARD=1 RUN_LOCAL_MAP=0 RUN_TOPIC_CHECK=0 RUN_RATE_CHECK=0 \
  RUN_STATIC_TF=0 RUN_TF_CHECK=0 RUN_FASTLIO_PLANNER_INPUT_ADAPTER=0 RUN_SPARK_FASTLIO=0 RUN_CONTROLLER_COMMAND=0 \
  BUILD_MOSIM_ROS2_MSGS=0 TIMEOUT_SECONDS=20 bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh
RESULT_DIR=Results/gazebo_ros2/sunray150_gazebo_ros2_spark_fastlio_truth_eval RUNTIME_GATE_PROFILE=spark_fastlio_localization \
  RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_FASTLIO_PLANNER_INPUT_ADAPTER=1 RUN_SPARK_FASTLIO=1 RUN_FASTLIO_TRUTH_EVAL=1 \
  RUN_GAZEBO_TRUTH_POSE=1 RUN_TOPIC_CHECK=1 RUN_RATE_CHECK=0 RUN_STATIC_TF=1 RUN_TF_CHECK=1 TIMEOUT_SECONDS=20 \
  bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh
bash Scripts/gazebo/run_sunray150_hover_hold_closed_loop.sh

# F. Current light-world truth-state refresh before figure-8/avoidance.
SCENARIO=Config/scenarios/system/sunray150_single_uav_competition_light.yaml \
RESULT_DIR=Results/gazebo_ros2/sunray150_single_uav_competition_light_sensor_local_map_truth_current \
RUNTIME_GATE_PROFILE=sensor_local_map \
RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_LOCAL_MAP=1 RUN_TOPIC_CHECK=1 RUN_RATE_CHECK=1 \
RUN_STATIC_TF=1 RUN_TF_CHECK=1 RUN_GAZEBO_TRUTH_POSE=1 BUILD_MOSIM_ROS2_MSGS=0 \
TIMEOUT_SECONDS=80 bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh

# G. Current single-UAV Gazebo figure-8 + static-obstacle + same-run map gate.
# The reference publisher is synchronized to Gazebo truth time by default. Do
# not revert this to wall-clock timing; wall-clock timing can feed late-mission
# setpoints to a newly taking-off vehicle when WSL/Gazebo runs slower than
# real time.
RESULT_DIR=Results/gazebo_ros2/single_uav_figure8_truthsynced_config_gate_current \
ENABLE_SAME_RUN_MAP_REVIEW=1 TIMEOUT_SECONDS=150 \
  bash Scripts/gazebo/run_sunray150_figure8_obstacle_gate.sh
```

Generated-controller checks, when generated-runtime authority is in scope, are
separate from the Gazebo runtime lane:

```bash
python Scripts/mworks/check_codegen_runtime.py \
  --code-dir Results/generated_mworks/<controller_codegen_dir> \
  --model-name <GeneratedControllerModelName> \
  --compile --run-smoke

python Scripts/mworks/check_codegen_sil_equivalence.py \
  --code-dir Results/generated_mworks/<controller_codegen_dir> \
  --model-name <GeneratedControllerModelName> \
  --mworks-reference-json Results/<mworks_reference>.json \
  --input-sequence <comma-separated-nonzero-inputs> \
  --json-out Results/<sil_equivalence>.json
```

The first command proves generated C runtime shape only. The second proves SIL
equivalence only for the supplied reference and input sequence. Neither command
proves Gazebo plant response, planner readiness, or competition controller
performance by itself.

Stable files:

```text
Config/scenarios/system/sunray150_gazebo_ros2_smoke.yaml
Config/gazebo/worlds/factory_minimal.sdf
Config/gazebo/models/sunray150/model.sdf
Config/gazebo/sensors/mid360_lidar_imu.sdf
Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh
Scripts/gazebo/check_gazebo_ros2_dependencies.sh
Scripts/gazebo/setup_gazebo_ros2_dependencies.sh
Scripts/gazebo/run_sunray150_hover_hold_closed_loop.sh
Scripts/ros/mosim_msgs/msg/ControllerOutput.msg
Scripts/ros/controller_output_to_gazebo_actuators.py
Scripts/ros/controller_output_to_gazebo_actuators_node.py
Scripts/ros/gazebo_fastlio_planner_input_adapter.py
Scripts/ros/gazebo_fastlio_imu_passthrough.py
Scripts/ros/ego_style_planner_output_node.py
Scripts/ros/gazebo_truth_hover_hold_controller.py
Scripts/gazebo/capture_gazebo_state_truth_topic.py
Scripts/ros/pointcloud_to_local_voxel_map_ros2.py
Scripts/quality/build_ue_truth_local_voxel_map_fixture.py
Scripts/tests/test_pointcloud_to_local_voxel_map_core.py
Scripts/tests/test_ue_truth_local_voxel_map_fixture.py
Scripts/tests/test_gazebo_ros2_smoke_contract.py
Scripts/tests/test_controller_output_to_gazebo_actuators.py
Scripts/quality/build_gazebo_ros2_runtime_status.py
Scripts/quality/evaluate_fastlio_truth_error.py
Scripts/quality/evaluate_gazebo_hover_hold_closed_loop.py
Scripts/tests/test_fastlio_truth_error_eval.py
Scripts/tests/test_gazebo_hover_hold_closed_loop.py
```

The runner writes runtime status for every attempt and a manifest only after a
passed gate. `BLOCKER.json` is present only for blocked or dry-run attempts and
is removed after a later successful gate in the same result directory.

```text
Results/gazebo_ros2/sunray150_gazebo_ros2_smoke/PREFLIGHT.json
Results/gazebo_ros2/sunray150_gazebo_ros2_smoke/TOPIC_CONTRACT.json
Results/gazebo_ros2/sunray150_gazebo_ros2_smoke/RUNTIME_STATUS.json
Results/gazebo_ros2/sunray150_gazebo_ros2_smoke/RUN_MANIFEST.json
Results/gazebo_ros2/sunray150_single_uav_competition_light_sensor_local_map_truth_20260618_007/RUNTIME_STATUS.json
Results/gazebo_ros2/sunray150_single_uav_competition_light_sensor_local_map_truth_20260618_007/RUN_MANIFEST.json
Results/gazebo_ros2/sunray150_gazebo_ros2_actuator_handoff/RUN_MANIFEST.json
Results/gazebo_ros2/sunray150_gazebo_ros2_actuator_handoff/RUNTIME_STATUS.json
Results/gazebo_ros2/sunray150_gazebo_ros2_controller_output_node_handoff/RUN_MANIFEST.json
Results/gazebo_ros2/sunray150_gazebo_ros2_controller_output_node_handoff/RUNTIME_STATUS.json
Results/gazebo_ros2/sunray150_gazebo_ros2_fastlio_planner_input/RUN_MANIFEST.json
Results/gazebo_ros2/sunray150_gazebo_ros2_fastlio_planner_input/RUNTIME_STATUS.json
Results/gazebo_ros2/sunray150_gazebo_ros2_fastlio_planner_input/fastlio_planner_input_adapter.json
Results/gazebo_ros2/sunray150_gazebo_ros2_spark_fastlio_localization/RUN_MANIFEST.json
Results/gazebo_ros2/sunray150_gazebo_ros2_spark_fastlio_localization/RUNTIME_STATUS.json
Results/gazebo_ros2/sunray150_gazebo_ros2_spark_fastlio_localization/fastlio_runtime/FASTLIO_RUNTIME_RECORDING.json
Results/gazebo_ros2/sunray150_gazebo_ros2_planner_handoff_without_setpoint_publication/RUN_MANIFEST.json
Results/gazebo_ros2/sunray150_gazebo_ros2_planner_handoff_without_setpoint_publication/RUNTIME_STATUS.json
Results/gazebo_ros2/sunray150_gazebo_ros2_planner_handoff_without_setpoint_publication/fastlio_imu_passthrough.json
Results/gazebo_ros2/sunray150_gazebo_ros2_planner_handoff_without_setpoint_publication/forbidden_topic_presence.json
Results/gazebo_ros2/sunray150_gazebo_ros2_ego_style_planner_output_without_actuation/RUN_MANIFEST.json
Results/gazebo_ros2/sunray150_gazebo_ros2_ego_style_planner_output_without_actuation/RUNTIME_STATUS.json
Results/gazebo_ros2/sunray150_gazebo_ros2_ego_style_planner_output_without_actuation/EGO_STYLE_PLANNER_OUTPUT_GATE.json
Results/gazebo_ros2/sunray150_gazebo_ros2_ego_style_planner_output_without_actuation/ego_style_planner_output.trace.jsonl
Results/gazebo_ros2/sunray150_gazebo_ros2_command_acknowledgement_without_closed_loop/RUN_MANIFEST.json
Results/gazebo_ros2/sunray150_gazebo_ros2_command_acknowledgement_without_closed_loop/RUNTIME_STATUS.json
Results/gazebo_ros2/sunray150_gazebo_ros2_command_acknowledgement_without_closed_loop/command_ack_guard_report.json
Results/gazebo_ros2/sunray150_gazebo_ros2_command_acknowledgement_without_closed_loop/stale_controller_output_report.json
Results/gazebo_ros2/sunray150_gazebo_ros2_spark_fastlio_truth_eval/RUN_MANIFEST.json
Results/gazebo_ros2/sunray150_gazebo_ros2_spark_fastlio_truth_eval/RUNTIME_STATUS.json
Results/gazebo_ros2/sunray150_gazebo_ros2_spark_fastlio_truth_eval/FASTLIO_TRUTH_ERROR_EVAL.json
Results/gazebo_ros2/sunray150_gazebo_ros2_spark_fastlio_truth_eval/GAZEBO_TRUTH_POSE_RECORDING.json
Results/gazebo_ros2/sunray150_gazebo_ros2_spark_fastlio_truth_eval/fastlio_runtime/FASTLIO_RUNTIME_RECORDING.json
Results/gazebo_ros2/sunray150_gazebo_ros2_hover_hold_closed_loop_pre_acceptance_005/RUN_MANIFEST.json
Results/gazebo_ros2/sunray150_gazebo_ros2_hover_hold_closed_loop_pre_acceptance_005/RUNTIME_STATUS.json
Results/gazebo_ros2/sunray150_gazebo_ros2_hover_hold_closed_loop_pre_acceptance_005/GAZEBO_HOVER_HOLD_CLOSED_LOOP_EVAL.json
Results/gazebo_ros2/sunray150_gazebo_ros2_hover_hold_closed_loop_pre_acceptance_005/hover_hold_controller.json
Results/gazebo_ros2/sunray150_gazebo_ros2_hover_hold_closed_loop_pre_acceptance_005/GAZEBO_TRUTH_POSE_RECORDING.json
Results/gazebo_ros2/dependency_check/DEPENDENCY_STATUS.json
Results/gazebo_ros2/dependency_check/DEPENDENCY_SETUP_PLAN.json
Results/gazebo_ros2/dependency_check/DEPENDENCY_SETUP_RESULT.json
Results/gazebo_ros2/offline_ue_truth_local_voxel_map_fixture/UE_TRUTH_LOCAL_VOXEL_MAP_FIXTURE.json
```

Current 2026-06-15 dependency status is ready for the bounded Gazebo+ROS2
sensor/local-map, FAST-LIO truth-error, and hover-hold pre-acceptance lanes:

```text
ros2=/opt/ros/humble/bin/ros2
colcon=/usr/bin/colcon
gazebo_sim_cli_command="ign gazebo"
gazebo_sim_cli_kind=ign
gazebo_cli_version=6.16.0
ros_gz_bridge_prefix=/opt/ros/humble
DEPENDENCY_STATUS.status=ready
```

Current 2026-06-16 single-UAV assembled Gazebo+ROS2 runtime status:

```text
current main runtime world: Config/gazebo/worlds/yunzong_planning_test_sunray150_assembled.sdf
current visible vehicle model: Config/gazebo/models/sunray150_assembled/model.sdf
current vehicle_id: sunray150_assembled
current scene/map: yunzong_planning_test / yunzong_planning_test_collision_truth

sensor/local-map gate: passed
sensor/local-map evidence: Results/gazebo_ros2/sunray150_gazebo_ros2_smoke/RUNTIME_STATUS.json
LiDAR sample_point_count: 11520
local voxel sample_point_count: 1193
local grid size: 120x120
same-run TF: map -> sunray150_assembled/base_link/mid360_lidar
measured rates: IMU about 199.528Hz, LiDAR about 9.981Hz, local voxels about 3.997Hz
claim boundary: sensor/local-map runtime evidence only; no planner_ready, setpoint, command ack, closed_loop, controller performance, or multi-UAV readiness

ControllerOutput node handoff gate: passed
ControllerOutput node handoff evidence: Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_controller_output_node_handoff_verify_20260616_151729/RUNTIME_STATUS.json
claim boundary: ControllerOutput -> actuator_msgs/Actuators -> gz.msgs.Actuators topic handoff only; no hover, flight, closed_loop, controller performance, stale-command policy, or final command acknowledgement

FAST-LIO/planner input surface gate: passed
FAST-LIO/planner input evidence: Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_fastlio_planner_input_verify_20260616_151804/RUNTIME_STATUS.json
LiDAR sample_point_count: 11520
Spark Livox-like sample point_num: 7209
same-run TF: map -> sunray150_assembled/base_link/mid360_lidar
claim boundary: input topic/frame/rate/shape only; no physical MID360 realism while source remains gpu_lidar, no FAST-LIO localization success, no planner_ready, no setpoint, no closed_loop, no controller performance, and no multi-UAV readiness

Gazebo truth-feedback hover-hold pre-acceptance gate: current light-world truth
source is the Gazebo transport state topic, not the old PosePublisher topic.
Old assembled-world blocker
`Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_hover_hold_closed_loop_verify_20260616_152301/BLOCKER.json`
used `/world/yunzong_planning_test_sunray150_assembled/dynamic_pose/info`
and remains historical only. For current light-world runs use:

```text
truth topic: /world/sunray150_single_uav_competition_light/state
truth recorder: Scripts/gazebo/capture_gazebo_state_truth_topic.py
accepted probe: Results/gazebo_ros2/sunray150_single_uav_competition_light_truth_state_probe_20260617_002/GAZEBO_TRUTH_POSE_RECORDING.json
```

Historical Factory hover-hold evidence:
Results/gazebo_ros2/sunray150_gazebo_ros2_hover_hold_closed_loop_pre_acceptance_005/RUNTIME_STATUS.json
This is not current assembled Sunray150/YunZong evidence because it used the old Factory world/model identity.
```

`Scripts/gazebo/check_gazebo_ros2_dependencies.sh` remains the read-only
dependency snapshot route. `Scripts/gazebo/setup_gazebo_ros2_dependencies.sh`
is the guarded setup route and is plan-only by default; it may install
`gz-fortress`, `ros-humble-ros-gz-bridge`, and `ros-humble-ros-gz-sim` only
when both guards are set:

```bash
EXECUTE=1 MOSIM_ALLOW_WSL_PACKAGE_INSTALL=1 bash Scripts/gazebo/setup_gazebo_ros2_dependencies.sh
```

The current smoke world targets `gazebo.backend=fortress_ignition6` and uses
Fortress-compatible `ignition-gazebo-*` system plugin names. The runner accepts
either new-style `gz sim` or Fortress `ign gazebo`; the exact selected CLI is
recorded in `PREFLIGHT.json`.

For WSL headless runs, keep the server render path on Ogre unless a later gate
proves Ogre2 stable on this host:

```text
GAZEBO_RENDER_ENGINE_SERVER=ogre
```

This avoids the observed Ogre2 crash in the current Fortress lane. It is a
Gazebo infrastructure setting, not a simulation-quality claim.

Current 2026-06-15 bounded runtime smoke status:

```text
RUNTIME_STATUS.status=runtime_smoke_passed
RUN_MANIFEST.quality_status=runtime_smoke_passed
LiDAR topic=/mosim/gazebo/lidar_points/points
LiDAR frame is scenario-derived; current assembled lane uses sunray150_assembled/base_link/mid360_lidar
LiDAR sample_point_count=11520
local voxels topic=/mosim/local_occupancy_voxels frame=map point_count=401
local grid topic=/mosim/local_occupancy_grid frame=map size=120x120
static TF is scenario-derived; current assembled lane uses map -> sunray150_assembled/base_link/mid360_lidar
rates: IMU about 198.647Hz, LiDAR about 9.954Hz, local voxels about 4.557Hz
```

The Gazebo LiDAR scan topic and point-cloud topic are distinct. The scanner
surface is `/mosim/gazebo/lidar_points`, but the ROS2 `PointCloud2` gate uses
`/mosim/gazebo/lidar_points/points`. The runtime status builder checks
`PointCloud2.width * PointCloud2.height` / sample point count so a nonempty
transport sample is required.

For the current EGO-style planner output gate, the runner should build and
source both local project ROS2 packages when `BUILD_MOSIM_ROS2_MSGS=1`:

```text
Scripts/ros/mosim_msgs
Scripts/ros/mosim_setpoint_adapter
```

That avoids a false blocker when the planner output path needs the project-owned
`ControllerOutput` / setpoint adapter chain. This gate is still no-actuation
and no-closed-loop only.

The current planner gate uses `input_wait_s: 60.0` because the live Gazebo
LiDAR/global-point stream may not emit a usable first frame immediately after
the adapter starts. The gate should wait for the first valid planner cloud and
odom inputs before starting the publish-duration countdown.

For human review, use the map-review recorder instead of static MWORKS plots
or browser/demo point clouds:

```bash
RESULT_DIR=Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_map_review RUNTIME_GATE_PROFILE=sensor_local_map \
  RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_LOCAL_MAP=1 RUN_MAP_REVIEW_CAPTURE=1 \
  RUN_TOPIC_CHECK=1 RUN_RATE_CHECK=1 RUN_STATIC_TF=1 RUN_TF_CHECK=1 TIMEOUT_SECONDS=18 \
  bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh
```

The recorder subscribes to live Gazebo/ROS2 topics and writes a JSON summary
plus PNG previews. It must not be confused with the offline UE-truth local-map
fixture.

Do not claim FAST-LIO localization, planner handoff, closed-loop success,
controller performance, or multi-UAV readiness from this smoke. It proves only
that the bounded Gazebo process, ros_gz bridge, sensor topics, same-run static
TF, and local voxel/grid adapter can run together.

Current bounded EGO-style planner output evidence:

```text
RUNTIME_STATUS.status=runtime_smoke_passed
RUNTIME_STATUS.gate_passed=true
RUNTIME_STATUS.gate_profile=ego_style_planner_output_without_actuation
EGO_STYLE_PLANNER_OUTPUT_GATE.status=planner_output_surface_passed
input topics=/mosim/planner/odom, /mosim/planner/global_points
output topics=/position_cmd, /mosim/planner/position_cmd, /mosim/planner/setpoint, /mosim/planner/setpoint_adapter_status
counts: odom=2128, global_points=1713, position_cmd=900, mosim_position_cmd=900
measured position_cmd rate about 4.999Hz
cloud frame=map
cloud shape=360x32
cloud finite bounds x=[-8.132, 8.016], y=[-9.013, 8.083], z=[0.948, 2.905]
forbidden controller/actuator topics absent
claim boundary: same-run planner output and setpoint-surface publication only
```

This gate is the current visible planner-output step for the single-UAV lane.
It does not prove `planner_ready`, trajectory tracking, controller output,
actuator command, or closed-loop success. Keep it separate from the later
command-acknowledgement and hover-hold gates.

Current 2026-06-15 bounded actuator handoff status:

```text
RUNTIME_STATUS.gate_profile=actuator_handoff
RUNTIME_STATUS.gate_passed=true
RUN_MANIFEST.quality_status=actuator_handoff_passed
controller command type=normalized_motor_speed
expected velocity=[4000, 4000, 4000, 4000]
ROS2 echo topic=/sunray150/gazebo/command/motor_speed
ROS2 echo velocity matches expected=true
Gazebo echo topic=/sunray150/gazebo/command/motor_speed
Gazebo echo velocity matches expected=true
```

This actuator handoff proves only that the bounded controller-output payload
is visible on the ROS2 actuator topic and the Gazebo transport actuator topic
through `ros_gz_bridge`. It does not prove hover, flight, closed-loop control,
controller performance, planner handoff, or command acknowledgement from a
flight-control state machine.

Current 2026-06-15 bounded ControllerOutput node handoff status:

```text
RUNTIME_STATUS.gate_profile=controller_output_node_handoff
RUNTIME_STATUS.gate_passed=true
RUN_MANIFEST.quality_status=controller_output_node_handoff_passed
controller output topic=/mosim/sunray150/controller_output
controller output message=mosim_msgs/msg/ControllerOutput
fixture command type=normalized_motor_speed
fixture command=[0.5, 0.5, 0.5, 0.5]
adapter node status=published
adapter node velocity=[4000, 4000, 4000, 4000]
ROS2 echo topic=/sunray150/gazebo/command/motor_speed
ROS2 echo velocity matches expected=true
Gazebo echo topic=/sunray150/gazebo/command/motor_speed
Gazebo echo velocity matches expected=true
```

This node handoff proves that a real ROS2 `ControllerOutput` message can be
published, consumed by `controller_output_to_gazebo_actuators_node.py`, and
observed as matching actuator velocity on both the ROS2 actuator topic and the
Gazebo transport actuator topic. It is still a topic/node handoff gate only. It
does not prove hover, flight, stale-command handling, mode/arming semantics,
planner handoff, closed-loop behavior, controller performance, or final
flight-control command acknowledgement.

Current controller-output bridge:

```text
mosim_msgs/msg/ControllerOutput
  -> Scripts/ros/controller_output_to_gazebo_actuators.py
  -> actuator_msgs/msg/Actuators.velocity[]
  -> ros_gz_bridge
  -> gz.msgs.Actuators.velocity[]
  -> Config/gazebo/models/sunray150/model.sdf MulticopterMotorModel plugins
```

The scenario records this under `ros2.controller_adapter`. The adapter supports
`motor_speed`, `normalized_motor_speed`, and
`mworks_signed_visual_motor_speed`; signed MWORKS visual speeds are validated
against `mworks_spin_command_sign=[1,-1,1,-1]` and converted to nonnegative
Gazebo motor-speed magnitudes. The adapter itself does not start ROS2, Gazebo,
or publish motor commands; the runner uses its generated `ros_cli_yaml` only
when `RUN_CONTROLLER_COMMAND=1` is set for the bounded actuator-handoff gate.

Current 2026-06-18 MWORKS CSV replay bridge:

```text
source CSV=Results/mworks_model_hygiene/20260612_rotor1_loss15_param_smoke/raw/rotor1_loss15_linear_mpc_online_fault_allocation_param_smoke.csv
converter=Scripts/ros/mworks_csv_to_controller_output_replay.py
runtime gate=Scripts/gazebo/run_mworks_controller_output_replay_gate.sh
latest evidence=Results/gazebo_ros2/mworks_controller_output_replay_gate_20260618_r4/
adapter status=published
published ControllerOutput samples=41
last normalized command=[0.059111, 0.056752, 0.054495, 0.056754]
last Gazebo actuator velocity=[472.889, 454.015, 435.960, 454.035]
plant response status=blocked
blockers=plant_z_response_below_min, plant_max_z_response_below_min
```

Interpretation: the MWORKS CSV bridge can publish and drive the Gazebo actuator
interface, but it is not a valid Gazebo closed-loop deployment by itself. The
replay is open-loop from Gazebo's point of view because the original CSV already
contains controller decisions made against the MWORKS plant state. Final Gazebo
deployment must use same-run Gazebo feedback or generated controller code
wrapped behind the `ControllerOutput` ABI.

Current simple same-run feedback gate:

```text
script=Scripts/gazebo/run_sunray150_takeoff_hover_land_gate.sh
controller=Scripts/ros/gazebo_truth_takeoff_hover_land_controller.py
claim=bounded Gazebo plant sanity: takeoff, hover, land
not claimed=MWORKS controller deployment, competition controller performance, planner_ready, final closed_loop acceptance, multi-UAV readiness
```

Use this simple gate before porting the MWORKS controller logic so plant
geometry, motor direction, thrust scale, start height, and `ControllerOutput`
transport are known-good in the same run.

Current 2026-06-15 bounded FAST-LIO/planner input-shape status:

```text
RUNTIME_STATUS.gate_profile=fastlio_planner_input
RUNTIME_STATUS.gate_passed=true
RUN_MANIFEST.quality_status=fastlio_planner_input_passed
adapter status=active
adapter report=Results/gazebo_ros2/sunray150_gazebo_ros2_fastlio_planner_input/fastlio_planner_input_adapter.json
Gazebo LiDAR input=/mosim/gazebo/lidar_points/points
Gazebo IMU input=/mosim/gazebo/imu
FAST-LIO outputs=/mosim/fastlio/livox/lidar, /mosim/fastlio/livox/imu
Sunray-compatible outputs=/uav1/livox/lidar, /uav1/livox/imu
planner input-shape outputs=/uav1/global_points, /mosim/planner/global_points, /uav1/sunray/gazebo_pose, /mosim/planner/odom
LiDAR sample_point_count=11520
same-run TF=map -> sunray150/base_link/mid360_lidar
adapter tf_lookup_failures=0
measured rates: fastlio_imu about 198.533Hz, fastlio_lidar about 9.931Hz, planner_global_points about 9.910Hz, planner_odom about 10.016Hz
```

This input-shape gate proves only that Gazebo MID360 LiDAR/IMU can be
republished into MoSim and Sunray-compatible FAST-LIO/planner input topics with
the expected frames and rates. It does not launch FAST-LIO, does not launch a
planner, does not publish setpoints, and does not prove localization, planner
readiness, command acknowledgement, closed-loop control, controller
performance, or multi-UAV readiness.

Current 2026-06-15 bounded Spark FAST-LIO output-surface status:

```text
RUNTIME_STATUS.gate_profile=spark_fastlio_localization
RUNTIME_STATUS.gate_passed=true
RUN_MANIFEST.quality_status=spark_fastlio_localization_passed
Spark launch=Scripts/ros/mosim_scene_replay/launch/spark_fast_lio_mosim.launch.py
Spark config=Config/ros2/mosim_spark_fast_lio_mid360.yaml
input topics=/mosim/spark_fastlio/livox/lidar and /mosim/fastlio/livox/imu
output topics=/cloud_registered, /odometry, /path
/cloud_registered frame=map point_count=2024
/odometry frame=map
/path frame=map
runtime recorder counts: registered_cloud=36, odometry=73, path=4
```

The Spark launch separates ROS frame ids from Spark's visualization-frame
enum. `common.base_frame` remains the ROS frame id
`sunray150/base_link`, while `common.visualization_frame` must be one of
`base`, `lidar`, or `imu`; the current scenario uses `visualization_frame:
base`. Do not pass a ROS frame id such as `sunray150/base_link` as
`common.visualization_frame`.

This output-surface gate proves that the local ROS2-compatible Spark FAST-LIO
candidate can consume the Gazebo MID360/Livox-style adapter topics and publish
nonempty FAST-LIO-family outputs. It does not prove localization quality,
truth-error bounds, planner readiness, setpoint publication, command
acknowledgement, closed-loop behavior, controller performance, or multi-UAV
readiness. The next FAST-LIO slice should compare `/odometry` against same-run
Gazebo truth or produce an explicit blocker explaining why the current
artifacts cannot support that evaluation.

Current 2026-06-15 bounded planner handoff without setpoint publication
status:

```text
RUNTIME_STATUS.gate_profile=planner_handoff_without_setpoint_publication
RUNTIME_STATUS.gate_passed=true
RUN_MANIFEST.quality_status=planner_handoff_without_setpoint_publication_passed
required planner input topics=/uav1/global_points, /mosim/planner/global_points, /uav1/sunray/gazebo_pose, /mosim/planner/odom
forbidden setpoint/controller/actuator topics all absent=true
forbidden evidence=Results/gazebo_ros2/sunray150_gazebo_ros2_planner_handoff_without_setpoint_publication/forbidden_topic_presence.json
FAST-LIO IMU passthrough topic=/mosim/fastlio/livox/imu rate about 198.612Hz
FAST-LIO IMU passthrough counts=32674 received, 32674 MoSim-published, 32674 Sunray-published
LiDAR sample_point_count=11520
same-run TF=map -> sunray150/base_link/mid360_lidar
```

This gate proves that the current Gazebo MID360 LiDAR/IMU stream can feed the
MoSim/Sunray planner input-topic surface while the setpoint, controller-output,
and actuator-command surfaces remain absent. It intentionally does not publish
planner setpoints and does not launch or validate a planner. It also does not
prove FAST-LIO localization quality, command acknowledgement, closed-loop
behavior, controller performance, or multi-UAV readiness.

The observed low-rate blocker on `/mosim/fastlio/livox/imu` was caused by
coupling IMU republish to the heavier LiDAR/PointCloud2 adapter path. The
current runner starts `Scripts/ros/gazebo_fastlio_imu_passthrough.py` as a
separate high-rate IMU process when the FAST-LIO/planner input adapter is in
scope, and the point-cloud adapter no longer owns the IMU output path. Keep
the IMU passthrough separate unless a later runtime profile proves equivalent
cadence without LiDAR-path coupling.

The adapter report/trace write path is intentionally throttled. Do not put
per-message JSON file writes back into the IMU callback path; that previously
dragged the republished IMU rate down to about 50Hz.

The active Gazebo+ROS2 smoke lane uses
`input_frame_policy=transform_input_frame_to_map_with_tf`: the input
`PointCloud2.header.frame_id` is expected to be the Gazebo sensor/body frame
derived from the scenario `vehicle_id` (`sunray150_assembled/base_link/
mid360_lidar` in the current assembled lane), and the local-map adapter may
publish `map` frame voxel/grid outputs only after a same-run TF chain from
that input frame to `map` is available. The old no-TF mode is limited to debug
or already-map input clouds; it must not relabel sensor/body-frame points as
`map`.

YunZong/Sunray reference boundary:

```text
References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/
References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/sunray150_with_mid360.sdf
References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/meshes/150.dae
References/Sunray/simulation/sunray_simulator/models/sensor_models/livox_mid360/
References/Sunray/simulation/sunray_simulator/models/sensor_models/livox_mid360/livox_mid360.sdf
References/Sunray/simulation/sunray_simulator/models/sensor_models/livox_mid360/scan_mode/mid360.csv
References/Sunray/simulation/sunray_simulator/worlds/
References/Sunray/General_Module/sunray_planner_utils/
References/Sunray/External_Module/ego-planner-swarm/
References/Sunray/External_Module/FUEL/
References/Sunray/sunray_formation/
```

These paths are useful reference/baseline material for Sunray150 geometry,
MID360 scan conventions, Gazebo scenes, RViz layouts, EGO/FUEL parameters,
formation patterns, and topic naming. Many YunZong/Sunray Gazebo assets are
directly reusable as reference structure, but reuse must happen through a
MoSim-owned adapter/contract. Do not blindly copy the ROS1 launch/MAVROS/PX4/
Gazebo Classic stack into the current Fortress/ROS2 lane. Port only the model,
sensor, topic, parameter, planner, or review contract that matches the current
bounded gate.

Practical reuse order for the current MoSim route:

```text
1. Reuse SDF/model/world/MID360 assets or parameters where the file format and
   coordinate convention can be verified locally.
2. Reuse RViz layouts, EGO/FUEL planner configs, and formation package behavior
   as reference contracts for future ROS2/Gazebo gates.
3. Wrap every reused command path behind MoSim `ControllerOutput` or an
   explicitly named MoSim adapter; never let upstream MAVROS/PX4/ROS1 topics
   silently own MoSim command authority.
4. Keep Gazebo Classic launch files as migration references unless a dedicated
   compatibility gate ports them to the current Fortress/ROS2 lane.
```

The offline UE-truth local voxel fixture is a separate source/static bridge
check. It uses existing UE scene-truth LiDAR frames and each local known-map
origin to exercise the local voxel/grid core without ROS2 transport:

```bash
python Scripts/quality/build_ue_truth_local_voxel_map_fixture.py
```

Current output:

```text
Results/gazebo_ros2/offline_ue_truth_local_voxel_map_fixture/UE_TRUTH_LOCAL_VOXEL_MAP_FIXTURE.json
Results/gazebo_ros2/offline_ue_truth_local_voxel_map_fixture/UE_TRUTH_LOCAL_VOXEL_MAP_FIXTURE.md
```

This fixture is useful for regression and data-shape review, but it is not
runtime evidence. It does not start UE, MWORKS, ROS2, Gazebo, RViz, FAST-LIO,
sockets, or GUI actions, and it must not be used to claim live `PointCloud2`,
TF, Gazebo runtime, planner readiness, closed-loop success, or multi-UAV
readiness.

Headless smoke evidence already passed for Factory:

- short ROS2 mapping publisher run created `/velodyne_points`,
  `/mosim/local_known_map_cloud`, `/mosim/local_occupancy_grid`,
  `/mosim/local_plan`, `/mosim/replay_odometry`, `/mosim/uav_path`, and
  `/tf`;
- short ROS2 launch workflow run using
  `Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh` built the generated
  scene-specific `Results/tmp/mosim_scene_replay_ros2_ws_<scene>` package and
  launched both replay publishers with `START_RVIZ=0`, `START_FASTLIO=0`,
  `MAX_FRAMES=3`, `LOOP=0`;
- `START_RVIZ=0 START_FASTLIO=0 LOOP=1 MAX_FRAMES=20 FPS=2`
  with `Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh` plus
  `REQUIRE_FASTLIO_OUTPUTS=0 Scripts/UE5/check_fastlio_ros2_topics.sh` passed
  for replay input topics.

Use RViz2 for manual visual review when a GUI window is appropriate.

## Runtime Boundary

Active point-cloud and map review must use RViz2 or an equivalent native
robotics viewer. Browser HTML is not accepted as runtime mapping evidence.

## Department Dispatch Gate

When work is dispatched to `MoSim｜ROS2感知定位与规划运行部`, the department must
plan its local task graph before live work and record:

```text
department_local_goal
critical_path_steps
parallelizable_slices
subagent_plan
subagent_plan_reason
subagents_used
verification_gates
manual_review_or_blocker_triggers
```

This is not a requirement to use at least one sub-agent. Disposable sub-agents,
when available, are only for bounded read-only source/log/schema review or
other independent slices; live ROS2 graph execution, process cleanup, and
runtime acceptance remain with the ROS2 department owner.

Every live ROS2 task must also declare `expected_engineering_outputs` and run
the task-specific runtime preflight before launching a graph:

```text
ROS2 environment/source status
stale MoSim/FAST-LIO/planner process check
expected source-window and topic contract
forbidden topic list
probe_count budget
cleanup plan
```

Return/blocker packets for ROS2 runtime work must include concrete runtime
evidence, not only JSON packet/progress metadata:

```text
ros2_preflight_before
probe_count
source_window_evidence
topic_evidence
FAST-LIO or planner evidence when in scope
forbidden_topic_absence
cleanup_summary
actual_engineering_outputs
claim_boundary
```

If a task says existing-evidence-only or no-rerun, do not launch ROS2. If a
live probe shows source timestamp regression, FAST-LIO callback loop-back,
missing required topics, stale cleanup failure, or an exhausted one-probe
budget, stop and return a `status=blocked` packet. Do not repeat live probes to
get a better result unless PMO sends a new task packet.

ROS2 runtime cleanup must stay scoped to the current ROS graph and the exact
replay/FAST-LIO helper processes launched by that task. Do not include
MWORKS, Sysplorer, Syslab, MCP wrapper, Codex, browser, or general desktop
process names in ROS2 cleanup/preflight kill patterns. If a preflight scan
matches those non-ROS processes, record the risk and stop or narrow the runner
before live work; do not continue with a broad cleanup pattern.

For Ubuntu 22.04, the preferred operator layout is:

```text
UE / MoSimSceneLibrary
  -> rendered scene, UAV body, camera, trajectory/local debug overlays

RViz2 planning/grid window
  -> /mosim/local_occupancy_grid, /mosim/local_known_map_cloud,
     /mosim/local_plan, /mosim/replay_odometry, /mosim/uav_path, TF

RViz2 point-cloud/FAST-LIO window
  -> /velodyne_points, /cloud_registered, /Odometry, /path, TF
```

## FAST-LIO Note

The current local `References/Lab/FAST_LIO` package is ROS1/Catkin-oriented.
On Ubuntu 22.04, prefer a ROS2 FAST-LIO/FAST-LIO2 port if available. If no
compatible port exists locally, keep the MoSim replay publishers on ROS2 and
record FAST-LIO as blocked or degraded until a ROS2-compatible package is added
or a containerized ROS1 bridge route is explicitly approved.

The local FAST-LIO-family compatibility scan is:

```bash
source /opt/ros/humble/setup.bash
python3 Scripts/UE5/check_fastlio_family_compatibility.py --write
```

Latest local evidence is saved at
`Results/unreal_scene_mapping/FASTLIO_FAMILY_COMPATIBILITY.md/json` and reports
`ros2_candidate_count=0`, `ros1_catkin_only_count=3`, and
`can_claim_fastlio_ros2_runtime=false` for `FAST_LIO`, `FAST-LIVO2`, and
`Point-LIO-point-lio-with-grid-map`.

Do not fabricate FAST-LIO output topics. `/cloud_registered`, `/Odometry`, and
`/path` must come from a real FAST-LIO-family runtime before localization is
claimed. `/mosim/replay_odometry` is only replay reference pose for RViz2 review
and must not be counted as FAST-LIO localization output.

## ROS2 FAST-LIO2 Candidate

Current candidate for the native ROS2 route is MIT SPARK `spark-fast-lio`, a
ROS2 / `ament_cmake` FAST-LIO2-family package. Keep it under ignored
`Results/tmp`, not tracked source, until it is reviewed as a formal dependency.

Preflight without installing packages:

```bash
Scripts/UE5/prepare_spark_fastlio_ros2_candidate.sh
```

Current preflight result is saved at
`Results/unreal_scene_mapping/SPARK_FASTLIO_ROS2_CANDIDATE.md/json`. The
candidate currently builds successfully under
`Results/tmp/spark_fast_lio_ros2_ws`; the runnable executable is
`Results/tmp/spark_fast_lio_ros2_ws/install/spark_fast_lio/lib/spark_fast_lio/spark_lio_mapping`.
If dependencies are missing on a clean machine, the script can avoid sudo by
downloading known ROS2 deb packages and extracting them under ignored
`Results/tmp/ros2_overlay_pcl_ros`; this makes those packages visible only for
the current project workflow. The system install equivalent is:

```bash
sudo apt install -y ros-humble-pcl-ros
```

After that dependency is available, or after the local overlay has been
prepared, build the candidate:

```bash
BUILD=1 Scripts/UE5/prepare_spark_fastlio_ros2_candidate.sh
```

The build can take longer than the default 60 second interactive timeout
because PCL/OpenNI CMake discovery is slow on WSL. The script writes a
`building` status before invoking `colcon`, keeps the build directory by
default, and supports resumed attempts. Use `CLEAN_BUILD=1` only when a full
reconfigure is needed.

Then source the generated workspace before running MoSim with FAST-LIO enabled:

```bash
source Results/tmp/spark_fast_lio_ros2_ws/install/setup.bash
FASTLIO_ROS2_LAUNCH_CMD='set +u; source /opt/ros/humble/setup.bash; source Results/tmp/spark_fast_lio_ros2_ws/install/setup.bash; ros2 launch spark_fast_lio mapping_mit_campus.launch.yaml start_rviz:=false scene_id:=mosim robot_name:=base base_frame:=base map_frame:=ue_world' \
START_FASTLIO=1 START_RVIZ=0 MAX_FRAMES=120 LOOP=1 FPS=10 \
FASTLIO_LIDAR_TOPIC=/mosim/lidar_points \
FASTLIO_IMU_TOPIC=/mosim/forward/imu \
FASTLIO_LIDAR_FRAME=base/velodyne_link \
FASTLIO_IMU_FRAME=base/forward_imu_optical_frame \
Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh factoryenvironmentcollect
```

Important topic detail: `spark_fast_lio` publishes odometry on the relative
topic `odometry`, which appears as `/odometry` without a namespace. The older
FAST-LIO ROS1 examples commonly use `/Odometry`. When validating this candidate,
use:

```bash
FASTLIO_ODOMETRY_TOPIC=/odometry Scripts/UE5/check_fastlio_ros2_topics.sh
```

Important frame detail: this candidate accepts visualization frame values such
as `imu`, `lidar`, and `base`; `base_link` triggered an invalid visualization
frame crash in the current run. Use `base_frame:=base` and MoSim sensor frames
under `base/...` until the candidate launch/config is reviewed further.

Current live runtime status: `spark_lio_mapping` starts, subscribes through the
configured MoSim topic remaps, and real runtime recordings now exist for
`/cloud_registered`, `/odometry`, and `/path`. A 2026-06-01 fix made the MoSim
FAST-LIO ROS2 replay stamp sequence monotonic across `LOOP=1` replay cycles to
avoid FAST-LIO IMU/LiDAR loopback clearing. The current MoSim launch uses
identity LiDAR/IMU extrinsics in
`Scripts/ros/mosim_scene_replay/launch/spark_fast_lio_mosim.launch.py`; the
upstream MIT launch transform is not valid for the synthetic MoSim sensor
frames.

Keep the claim boundary precise: ROS2 runtime and FAST-LIO output topics are
working. Latest evaluations:

```text
Factory:  status=failed_error_threshold, rmse=9.761 m, max_error=18.547 m
Derelict: status=pass, rmse=0.814 m, max_error=1.938 m
Thresholds: max_position_rmse_m=1.0, max_position_error_m=3.0
```

Derelict is a real ROS2 FAST-LIO runtime numeric pass with quality warnings
(`Not enough IMU data` appears in the runtime log and odometry timestamps are
partly nonmonotonic). Factory remains degraded and cannot be claimed.

Runtime evidence lives under:

```text
Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_scan099/
Results/unreal_scene_mapping/derelictcorridormegascans/fastlio_runtime_scan099/
```

Before answering the current FAST-LIO state, prefer the latest route-specific
`*_CURRENT` gate and its linked runtime directory over older summary,
candidate, preflight, or blocker files. For example, the Factory current Gate B
state is recorded in:

```text
Results/unreal_scene_mapping/factoryenvironmentcollect/REALSTACK_MINILOOP_GATE_CURRENT.md
Results/unreal_scene_mapping/factoryenvironmentcollect/realstack_miniloop_gate_current.json
```

That gate may prove headless runtime credibility for a manual UE/RViz review,
but it still does not claim final controller integration, planner performance,
or final product acceptance. Keep older files such as source compatibility
scans, build-phase candidate notes, ROS1 bundle JSON, or Mid360 blocker reports
as route/date-specific history unless they match the active route being
reviewed.

## References

- ROS2 Humble Ubuntu deb install:
  `https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html`
- ROS2 mirrors:
  `https://docs.ros.org/en/humble/Installation/ROS-2-Mirrors.html`
- FishROS installer:
  `http://fishros.com/install`
- Livox MID-360 official specs:
  `https://www.livoxtech.com/mid-360/specs`
