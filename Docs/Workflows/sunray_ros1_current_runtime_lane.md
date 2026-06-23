# Sunray ROS1 Current Runtime Lane

> Current executable lane for single-thread Sunray150 review work. This file
> exists to prevent fallback to old ROS2/PX4/x500 or downloaded substitute
> stacks when the active task is Sunray ROS1/Gazebo/RViz review.

Status: active current lane, 2026-06-23 CST.

## 1. Active Lane

Current review work uses:

```text
Ubuntu-20.04 / ROS1 Noetic
-> References/Sunray
-> reviewed assembled Sunray150 + MID360 model
-> Gazebo Classic
-> RViz for trajectory/path and real MID360 PointCloud2 review
```

Current source roots:

```text
References/Sunray
References/Lab/FAST_LIO
References/Lab/ego-planner*
Scripts/sunray/
Config/rviz/sunray_ros1_*.rviz
Results/sunray_ros1/
```

Do not use the old Ubuntu-22.04 / ROS2 Humble / PX4 `x500_mid360` experiment
route for this lane. Do not use `Results/external_downloads/fast_lio_main.zip`
or a fresh online clone as the first source when `References/Lab/FAST_LIO`
exists.

## 2. Stop Rules

If this lane is blocked, stop on the blocker and diagnose it in this lane. Do
not substitute a different vehicle, middleware generation, runtime stack, or
sensor source to make progress appear successful.

Documentation corrections in this lane are a means to keep execution aligned,
not the terminal deliverable. After a doc fix, continue with the smallest
current evidence gate that can safely move the Sunray ROS1 review forward. If
local source and official docs do not explain a runtime failure, search
relevant blogs/community notes. If the remaining fix would change vehicle,
middleware, FAST-LIO source, sensor source, or control architecture, stop and
ask the user before proceeding.

Forbidden substitutes for current Sunray ROS1 review:

```text
x500_mid360
px4_mid360_obstacle_light
Ubuntu-22.04 / ROS2 Humble as the active review route
ROS2/PX4 FAST-LIO external-vision route
downloaded FAST-LIO replacing References/Lab/FAST_LIO
fake/static point cloud
empty PointCloud2 topic
headless numeric pass as Gazebo GUI/RViz visual acceptance
truth-feedback-only bridge as formal generated-controller deployment
UE screenshots as ROS/Gazebo/RViz runtime proof
```

Allowed diagnostics:

```text
inspect local source and generated SDF/launch files
inspect Gazebo, ROS, MAVROS, Sunray, Livox, and RViz logs
inspect official docs and local upstream examples
search relevant blogs/community notes when local source and official docs do
not explain the failure
return a precise blocker when the next step would change the agreed lane
```

Changing to ROS2/PX4/x500, downloading replacement source, or changing the
accepted vehicle/sensor architecture requires a separate explicit user/PMO
decision.

## 3. Runtime Debug Evidence

Every Sunray ROS1 runtime script or manual run should leave enough evidence to
continue without guessing, but it should not turn into open-ended logging. For
each bounded run, record:

```text
run command and key environment variables
result directory
phase start/end markers
topic names, message counts, rates, and one representative sample when relevant
stdout/stderr/log paths
final status: passed, failed, or blocker
```

Run Sunray/Gazebo/PX4/MAVROS missions serially. Do not launch two live
Gazebo/Sunray runs in parallel on the same WSL/ROS master because they share
ROS, Gazebo, MAVLink, and PX4 ports and can fail before MAVROS is ready. If a
run reports `sunray gazebo launch exited before MAVROS ready`, first check for
parallel or stale `roslaunch`, `gzserver`, `gzclient`, `px4`, `mavros`, and
`px4ctrl` processes before changing controller parameters.

During scripted shutdown, a successful run can still print a final
`roslaunch ... Killed` line while child processes are being cleaned up. Classify
the run from `PX4CTRL_BASIC_MISSION_METRICS.json` and `RUN_MANIFEST.json`, not
from that cleanup line alone.

For RViz/Gazebo visual problems, first separate data absence from display
semantics:

```text
1. Prove whether the underlying topic has nonempty data.
2. If data exists but the display is wrong, inspect RViz/Gazebo display
   settings and official docs for the narrow symptom.
3. If official docs do not explain it, search a narrow community/blog query and
   record the useful source in the run notes.
4. Apply one bounded display/config fix and rerun the smallest review gate, or
   return a blocker and ask the user if the fix would change architecture.
```

Example: a MID360 PointCloud2 topic that appears only for a few seconds in RViz
is not automatically a hardware or LiDAR-data failure. First check
PointCloud2 nonempty data and then RViz display settings such as decay time,
fixed frame, queue size, and color transformer. Color display is also a
display setting unless the task explicitly requires RGB/colorized point data.
For current review, keep raw `/uav1/livox/lidar` as the real-time scan layer
and use `/mosim/sunray/lidar_points_map_accumulated` as the long-lived,
map-frame, pseudo-colored review layer. If the raw PointCloud2 fields only
declare `x/y/z`, do not claim sensor-native RGB; use the accumulated review
topic or FAST-LIO/map outputs for map-style persistent visualization.

Current default visual review split, 2026-06-22:

FAST-LIO/PX4 EKF定位闭环、Gazebo-Z诊断策略、planner重跑顺序和
EGO/EGOv2/Diff-Planner既有复现边界，先按
`Docs/Design/MoSim_FASTLIO定位闭环与规划复现基础方案.md`
执行。该文档是当前所有 8字、螺旋、阶跃、EGO、EGO-Swarm 重跑的定位
基础，不得把旧的 Gazebo/PX4 辅助定位 planner 结果称为 FAST-LIO 定位
闭环结果。2026-06-22 FAST-LIO direct-control blocker 后，任何把
`/mosim/fastlio/odom_aligned` 作为控制状态源的尝试，必须先通过该文档
D-FL0 到 D-FL6 的输入源、Livox格式、外参坐标、静态定位、单轴运动、
独立定位误差和PX4 EKF融合门禁；否则 px4ctrl 必须继续使用
`/uav1/mavros/local_position/odom`。

```text
Controller-only missions such as takeoff-hover-land, figure-8, and spiral:
  do not require the EGO/grid RViz.
  default review window:
    Config/rviz/sunray_ros1_fastlio_accumulated_map_review.rviz
  show by default:
    /Laser_map                    -> FAST-LIO accumulated ikd-tree map
    /mosim/fastlio/uav_axes       -> current UAV body-frame XYZ axes from
                                     FAST-LIO odometry
    /mosim/px4ctrl/truth_path     -> controller actual trajectory
    /mosim/px4ctrl/reference_path -> controller reference trajectory
  diagnostic only, disabled by default:
    /path                         -> FAST-LIO raw odometry trajectory
    /Odometry                     -> current FAST-LIO pose marker
    /mosim/fastlio/uav_path       -> FAST-LIO/control-state center path

FAST-LIO direct localization mode:
  runner:
    Scripts/sunray/run_px4ctrl_basic_gate.sh
  environment:
    PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=true
    PX4CTRL_ODOM_SOURCE=mavros_local
  control state source:
    /uav1/mavros/local_position/odom after PX4 EKF fusion
  external odometry source sent to PX4:
    /mosim/fastlio/odom_aligned
  sensor source:
    /uav1/livox/lidar
    /uav1/livox/imu
  FAST-LIO launch:
    References/Lab/FAST_LIO/launch/mapping_mosim_sunray_livox_custom.launch
    through Scripts/sunray/pointcloud2_to_livox_custom_msg.py
  fallback:
    mapping_mosim_sunray_pointcloud2.launch is smoke/diagnostic fallback
    only, not the default localization path.
  aligned odometry timestamp:
    default to FAST-LIO measurement time and publish
    /mosim/fastlio/odom_aligned_delay for delay diagnostics. Replacing stamps
    with current ROS time is legacy/smoke-only unless a timing audit explicitly
    asks for it.
  frequency:
    keep current default MID360/FAST-LIO 10Hz settings unless a separate
    timing review explicitly reopens the 20Hz change.
  PX4 EKF external-vision parameters for the accepted Goal1 gate:
    EKF2_EV_CTRL=11
    EKF2_HGT_REF=3
    EKF2_EV_DELAY=0
    EKF2_EV_NOISE_MD=1
    EKF2_EVP_NOISE=0.03
    EKF2_EVA_NOISE=0.03
    Do not use EV_CTRL=15 as the default for this lane: in the 2026-06-23 A/B
    run it improved Z slightly but worsened XY, and this chain publishes
    vision_pose pose rather than a velocity-bearing MAVLink odometry stream.
  px4ctrl thrust mapping for the accepted Goal1 gate:
    thrust_model/estimate_enable=false
    thrust_model/hover_percentage=0.30
    The upstream online thrust estimator stays available, but the current
    Sunray/Gazebo baseline freezes it because online adaptation was observed
    to move the normalized thrust away from a reproducible hover mapping.
  current takeoff-hover-land command trim:
    --command-x-bias-m -0.025
    --command-y-bias-m -0.004
    --command-z-bias-m -0.092
    Treat this as a Sunray/Gazebo/EKF baseline trim, not as part of the
    px4ctrl algorithm core or a MWORKS controller port.
  boundary:
    Gazebo/Sunray truth remains evaluation-only and must not be fed into the
    controller in this mode. Raw FAST-LIO `/Odometry` is not a safe controller
    input because its `camera_init -> body` pose is the MID360/Livox body, not
    the UAV flight-control `base_link`. It must first pass through
    `Scripts/sunray/fastlio_odom_alignment_adapter.py`, which applies the
    accepted `base_link -> livox_mid360::base_link` mount transform and initial
    MAVROS-local alignment.
    The aligned odometry must pass a standalone localization-vs-truth gate
    before it is allowed to feed PX4 EKF. Point cloud, accumulated map, or RViz
    visual presence alone is not sufficient localization evidence. The first
    radar-localized controller test must keep px4ctrl on MAVROS local-position
    feedback, not direct FAST-LIO feedback.

FAST-LIO localization/map standalone review:
  config: Config/rviz/sunray_ros1_fastlio_accumulated_map_review.rviz
  fixed frame: camera_init
  show by default:
    /Laser_map    -> FAST-LIO accumulated ikd-tree map, published at a
                     throttled review rate
    /mosim/fastlio/uav_axes -> current UAV body-frame XYZ axes
  diagnostic only, disabled by default:
    /path         -> FAST-LIO odometry trajectory
    /Odometry     -> current FAST-LIO pose marker
    /mosim/fastlio/uav_path -> UAV center path derived from FAST-LIO odometry
    /cloud_registered -> current registered scan, not the accumulated map
    /uav1/livox/lidar -> raw MID360 scan

EGO/grid planning or obstacle-avoidance review only:
  config: Config/rviz/sunray_ros1_ego_grid_trajectory_review.rviz
  fixed frame: world
  show by default:
    /drone_0_ego_planner_node/grid_map/occupancy_inflate
    /mosim/goal4/truth_path
    /mosim/goal4/position_cmd_path
    /mosim/goal4/target_path
```

Do not use RViz `Decay Time` on `/cloud_registered` as proof of a FAST-LIO
accumulated map. In the local FAST-LIO source, `/cloud_registered` is the
current undistorted scan transformed to `camera_init`. The live accumulated
review map is `/Laser_map`, enabled through `publish/map_pub_en` and throttled
through `publish/map_pub_period` in
`References/Lab/FAST_LIO/launch/mapping_mosim_sunray_livox_custom.launch`.

Current MID360 model rule, 2026-06-22:

```text
SUNRAY_MID360_SENSOR_MODE=nested
```

is the default for current Sunray ROS1 MID360/FAST-LIO review. This restores
the original Sunray nested `model://livox_mid360` sensor model with a fixed
joint on the reviewed Sunray150 assembly. `inline` mode is diagnostic-only:
it places ray/IMU sensors directly in the vehicle `base_link` and can change
the raw scan/FAST-LIO accumulated-map visual semantics, including radial
star-like artifacts. Do not use `inline` output as current MID360 acceptance
evidence unless the task explicitly asks for that diagnostic.

If RViz or MAVROS logs report `Detected jump back in time ... Clearing TF
buffer`, treat short visual disappearance as a time/TF/display continuity
problem until proven otherwise. Separate it with
`Scripts/sunray/record_ros1_topic_continuity.py`: compare raw
`/uav1/livox/lidar`, bridge `/mosim/fastlio/livox/lidar`,
`/cloud_registered`, `/Odometry`, `/path`, and accumulated map-cloud wall-time
and header-time gaps. Do not change MID360/FAST-LIO scan rate as the first fix
for a display flash. In review runs with `KEEP_ALIVE=true`, keep the mission
node in review hold so `/mosim/sunray/truth_path`,
`/mosim/sunray/reference_path`, and
`/mosim/sunray/lidar_points_map_accumulated` continue publishing while the
user audits RViz.

Current time-source rule: Sunray ROS1 Gazebo/RViz/FAST-LIO review runs must
default to Gazebo `/clock` via `USE_SIM_TIME=true`. On 2026-06-20, the
baseline `USE_SIM_TIME=false` audit showed Windows/WSL wall time itself jumping
back by about 2s every few dozen seconds; TF then logged `Detected jump back in
time ... Clearing TF buffer`, causing RViz point-cloud/path flashes. The
bounded `USE_SIM_TIME=true` rerun passed takeoff-hover-land and produced
monotonic `/clock`, `/uav1/livox/lidar`, `/cloud_registered`, `/Odometry`,
and `/uav1/livox/imu` header times, with no TF jump-back log hits. Keep MID360
and FAST-LIO at the matched 10Hz setting unless a separate load/timing review
approves a 20Hz sensor experiment. `simulator_mavlink poll timeout` may still
appear as a Gazebo/PX4 realtime scheduling warning; do not classify it as the
RViz TF-clear root cause unless paired with new timing evidence.

Use `Scripts/sunray/record_ros1_time_tf_audit.py` when this symptom returns.
The audit records `/use_sim_time`, `/clock` monotonicity, `rospy.Time.now()`,
header-time monotonicity for LiDAR/IMU/FAST-LIO/path topics, TF child-frame
monotonicity, and relevant warning counts from run logs.

Current physics/IMU frequency boundary, 2026-06-21:

```text
requested experiment:
  SUNRAY_GAZEBO_MAX_STEP_SIZE_S=0.0025
  SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ=400

observed result:
  Results/sunray_ros1/sunray_ros1_pid_hover_400hz_bias2_kp85_kv42_kvi03_zkvi06_retry_20260621_042402/
  gzserver exited with code 134/core dumped shortly after spawning
  sunray150_with_mid360; no mission gate data was produced.

latest confirmation:
  Results/sunray_ros1/sunray_ros1_pid_hover_400hz_freqgate_kp10_kv52_20260621_061852/
  gzserver again exited with code 134/core dumped; MAVROS did not connect.
```

Do not block PID tuning on this 400Hz attempt. The current stable Sunray
control-tuning baseline uses:

```text
SUNRAY_GAZEBO_MAX_STEP_SIZE_S=0.001
SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ=1000
Sunray control_loop_hz=200
MID360/FAST-LIO kept out of the controller loop unless explicitly in scope
```

The 0.001s max step is a smaller physics step than the requested 0.0025s
400Hz configuration; it is the current stable tuning lane, not a shortcut to
lower fidelity. The latest stable frequency/hover audit is:

```text
Results/sunray_ros1/sunray_ros1_pid_hover_freqaudit_1000phys_200ctrl_20260621_062308/
MAVROS IMU output observed around 50Hz; 400Hz flight-controller IMU output is
not yet runtime-proven in this lane.
```

Current MAVROS/PX4 local-position frequency diagnosis, 2026-06-21:

```text
accepted hover baseline:
  Results/sunray_ros1/sunray_ros1_pid_hover_tune_g040_kvi02_imu400_20260621_070126/
  status=passed
  steady hover XY RMSE=0.019479m, XY max=0.035077m
  steady hover Z RMSE=0.013807m, Z max=0.021920m

LOCAL_POSITION_NED 100Hz isolated test:
  Results/sunray_ros1/sunray_ros1_freq_localpos100_20260621_102346/
  status=blocked
  /uav1/mavros/local_position/pose observed about 100Hz
  /uav1/mavros/imu/data stayed about 50Hz
  steady hover XY RMSE=0.031636m, XY max=0.040562m
  steady hover Z RMSE=0.052150m, Z max=0.095345m

LOCAL_POSITION_NED 100Hz same-PID bias-calibration recheck:
  Results/sunray_ros1/sunray_ros1_freq_localpos100_biascal_recheck_20260621_110720/
  status=blocked
  same Sunray PID params as the accepted hover baseline and
  --enable-hover-bias-calibration enabled
  /uav1/mavros/local_position/pose observed about 100Hz
  /uav1/mavros/local_position/velocity_local observed about 100Hz
  /uav1/mavros/imu/data stayed about 50Hz
  steady hover XY RMSE=0.027991m, XY max=0.047998m
  steady hover Z RMSE=0.017018m, Z max=0.028607m
  blocker: steady_hover_xy_rmse_above_max:0.028

LOCAL_POSITION_NED 125Hz isolated test:
  Results/sunray_ros1/sunray_ros1_freq_localpos125_20260621_102813/
  status=blocked
  /uav1/mavros/local_position/pose observed 125Hz
  /uav1/mavros/local_position/velocity_local observed 125Hz
  /uav1/mavros/imu/data stayed about 50Hz
  steady hover XY RMSE=0.030262m, XY max=0.038436m
  steady hover Z RMSE=0.066040m, Z max=0.120905m

LOCAL_POSITION_NED 200Hz request:
  Results/sunray_ros1/sunray_ros1_freq_localpos200_20260621_103104/
  status=blocked
  requested 200Hz but /uav1/mavros/local_position/pose and velocity_local
  were still observed at about 125Hz
  /uav1/mavros/imu/data stayed about 50Hz
  steady hover XY RMSE=0.028799m, XY max=0.041427m
  steady hover Z RMSE=0.060860m, Z max=0.107197m

LOCAL_POSITION_NED 100Hz hover-only variant A:
  Results/sunray_ros1/sunray_ros1_freq100_hoveronly_variantA_20260621_113103/
  status=blocked
  mission=takeoff_hover_land, no FAST-LIO, no UE, no MWORKS interface, no 8字
  /uav1/mavros/local_position/pose observed near 100Hz with min 0.008s,
  max 0.012s, std dev about 0.002s in sampled windows
  /uav1/mavros/local_position/velocity_local observed near 100Hz, but the
  audit also recorded multiple later `no new messages` windows
  /uav1/mavros/imu/data stayed near 50Hz and showed early interval spikes
  including min 0.000s, max 0.040s to 0.152s before later windows stabilized
  steady hover XY RMSE=0.048335m, XY max=0.052363m
  steady hover Z RMSE=0.009909m, Z max=0.016350m
  blocker: steady_hover_xy_rmse_above_max:0.048,
           steady_hover_xy_above_max:0.052
```

Conclusion: 100Hz is fixed as the current mainline frequency for this lane, but
the 100Hz result must be judged through a hover-only gate before it is allowed
to feed 8字, spiral, FAST-LIO, or planner work. The 100Hz same-PID/
bias-calibrated recheck is better than the 125Hz isolated test overall and is
much better in Z, so it is wrong to conclude that "100Hz is worse than 125Hz"
as a general rule. The narrower conclusion is that "only overriding
`LOCAL_POSITION_NED` to 100Hz" initially degraded steady-hover XY RMSE from
about 0.0195m to about 0.0280m in the cleaner bias-calibrated recheck, and up
to about 0.0483m in the later hover-only variant A, under the old all-axis
hover-bias calibration and short simulated hover window.

The likely cause is mixed-rate state assembly, not the 100Hz target itself:
`/uav1/mavros/local_position/pose` and velocity were raised to 100Hz/125Hz, but
`/uav1/mavros/imu/data` stayed near 50Hz. Variant A proves that the 100Hz
pose/velocity target can be reached, but it also records velocity receive gaps
and IMU interval spikes, so timing alignment remains unproven. Earlier 100Hz
pose audits also showed arrival/timestamp jitter (`min: 0.000s`, `max` up to
about 0.02-0.03s), while 125Hz appeared more regular in some sampled windows.
`TF_REPEATED_DATA` warnings appear in the accepted baseline and in the
high-rate runs, so they are timing-risk evidence but not by themselves a
sufficient explanation for the 100Hz/125Hz metric difference.

Do not choose 125Hz as the long-term preference merely because one raw rate
sample looked more regular: 125Hz does not divide the 200Hz Sunray control loop
cleanly, while 100Hz does. The current frequency work is therefore a 100Hz
hover-only alignment pass, not a broader FAST-LIO, UE, MWORKS, or trajectory-
control task.

100Hz hover-only alignment plan:

```text
scope:
  takeoff_hover_land only
  no FAST-LIO feedback, no UE, no MWORKS interface, no 8字/spiral
  keep SUNRAY_GAZEBO_MAX_STEP_SIZE_S=0.001
  keep SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ=1000
  keep Sunray control_loop_hz=200

variant A:
  MAVROS_STREAM_RATE_HZ=100
  PX4_MAVLINK_STREAM_NAMES=LOCAL_POSITION_NED
  MAVROS_SET_STREAM_GROUPS=position
  MAVROS_SET_MESSAGE_IDS=32:LOCAL_POSITION_NED
  enable hover-bias calibration
  run frequency audit long enough to inspect pose/velocity/IMU jitter

variant B, only if A still misses XY RMSE:
  keep 100Hz local-position target
  inspect whether the relevant attitude/IMU MAVLink/MAVROS streams can be
  aligned without broad rate-limit patching
  add a timing audit that records pose, velocity, IMU header-time and
  wall-time gaps before changing PID gains
  do one bounded hover-only run and compare to the accepted baseline

variant B result:
  Results/sunray_ros1/sunray_ros1_freq100_hover_ctrlxyzpos_zbias_imu100_20260621_122127/
  status=passed
  runner=Scripts/sunray/run_freq100_hover_ctrlxyzpos_zbias_imu100_once.sh
  scope=takeoff_hover_land only; no FAST-LIO, no UE, no MWORKS interface,
  no 8字/spiral
  MAVROS_STREAM_RATE_HZ=100
  PX4_MAVLINK_STREAM_NAMES=HIGHRES_IMU ATTITUDE ATTITUDE_QUATERNION
  LOCAL_POSITION_NED
  MAVROS_SET_STREAM_GROUPS=raw_sensors position extra1
  MAVROS_SET_MESSAGE_IDS=105:HIGHRES_IMU 30:ATTITUDE
  31:ATTITUDE_QUATERNION 32:LOCAL_POSITION_NED
  MAVROS_PATCH_RATE_LIMITS=true
  /uav1/mavros/imu/data observed near 100Hz
  /uav1/mavros/local_position/pose observed near 100Hz
  /uav1/mavros/local_position/velocity_local observed near 100Hz before later
  post-mission no-new-message windows
  steady hover XY RMSE=0.018093m, XY max=0.030072m
  steady hover Z RMSE=0.011865m, Z max=0.032544m
  time/TF audit: /clock monotonic, no TF jump-back log hits

acceptance:
  steady hover XY RMSE <= 0.020m
  steady hover XY max <= 0.050m
  steady hover Z RMSE <= 0.020m
  steady hover Z max <= 0.050m
  /uav1/mavros/local_position/pose observed near 100Hz
  /uav1/mavros/local_position/velocity_local observed near 100Hz
  /uav1/mavros/imu/data observed near 100Hz for the IMU-aligned candidate

accepted 100Hz hover-only baseline:
  Results/sunray_ros1/sunray_ros1_freq100_hover_ctrlxyzpos_zbias_20260621_120304/
  status=passed
  command path=Sunray CTRL_XyzPos/CTRL_Traj -> attitude + thrust
  MAVROS local-position request=100Hz
  hover-bias calibration axes=z only
  hover-bias calibration max step=0.02m
  initial_hover_s=14.0, so the 8s steady-hover evaluation tail is not only a
  takeoff/settling transient in Gazebo simulated time
  steady hover XY RMSE=0.013740m, XY max=0.022972m
  steady hover Z RMSE=0.013731m, Z max=0.028969m
  /uav1/mavros/local_position/pose observed near 100Hz
  /uav1/mavros/imu/data still observed near 50Hz, with some audit gaps/spikes

current accepted rule:
  keep 100Hz as the lane frequency
  do not prefer the IMU-aligned 100Hz candidate for the current trajectory
  baseline unless a new hover-only gate beats the Z-only local-position
  baseline; the 2026-06-21 afternoon spiral check made hover and spiral worse
  keep Sunray custom CTRL_XyzPos/CTRL_Traj as the hover baseline command path
  keep Z-only hover-bias calibration with max step 0.02m for the 100Hz hover
  baseline
  do not promote 200Hz as a default: prior LOCAL_POSITION_NED 200Hz request was
  observed at only about 125Hz in this lane
  do not re-enable all-axis hover-bias calibration for the 100Hz hover baseline
  without a new hover-only A/B gate
```

Current persistent Linux-local workspace correction, 2026-06-21 afternoon:

```text
problem:
  the earlier stable /tmp/mosim_sunray_build_20260620_114615/Sunray workspace
  disappeared after WSL cleanup/restart, and running Gazebo/PX4 directly from
  /mnt/c/Users/HP/Desktop/MoSim/References/Sunray caused PX4 startup failure.

current default runtime workspace:
  /opt/mosim_work/sunray_ws/Sunray

current runner change:
  Scripts/sunray/run_sunray_ros1_native_mission_gate.sh now defaults SUNRAY_WS
  to /opt/mosim_work/sunray_ws/Sunray.

build note:
  sunray_msgs and sunray_uav_control were rebuilt in the persistent workspace.
  A separate Gazebo-package rebuild attempt was blocked by Windows Anaconda
  protobuf leakage into WSL CMake, but the current mission gate runs because
  the active launcher environment uses the existing Gazebo/PX4/Sunray runtime
  libraries and a clean PATH.

do not:
  do not move the main runtime back to /tmp or /mnt/c unless a fresh runtime
  gate proves PX4/Gazebo/MAVROS startup and mission metrics.
```

Current 100Hz baseline optimization snapshot, 2026-06-21 afternoon:

```text
accepted hover rerun:
  Results/sunray_ros1/sunray_ros1_freq100_hover_ctrlxyzpos_zbias_20260621_145401/
  status=passed
  steady hover XY RMSE=0.015055m, XY max=0.027700m
  steady hover Z RMSE=0.010766m, Z max=0.020147m
  claim: takeoff-hover-land is inside the 2cm-RMSE / 5cm-max hover boundary.

current 100Hz figure-8 rerun:
  Results/sunray_ros1/sunray_ros1_freq100_figure8_zbias_bestshape_20260621_145804/
  status=blocked only by strict time-sync max
  shape/nearest-path RMSE XY=0.015984m, P95=0.029277m, max=0.044131m
  time-sync RMSE XY=0.021114m, P95=0.038649m, max=0.054273m
  diagnosis: the >5cm violation is one local about-1.15s peak window; shape
  tracking is inside 5cm. The lead=0.15s candidate did not help and also pushed
  shape max above 5cm, so keep lead=0.20s for now.

current 100Hz spiral baseline rerun:
  Results/sunray_ros1/sunray_ros1_freq100_spiral_zbias_bestshape_20260621_150258/
  status=blocked
  time-sync XYZ RMSE=0.043044m, P95=0.069046m, max=0.090257m
  diagnosis: Z error dominates; local-position/truth Z disagreement and
  vertical trajectory response are the main source, not a gross XY shape failure.

best current 100Hz spiral candidate:
  Results/sunray_ros1/sunray_ros1_freq100_spiral_zbias_smoothz_bestshape_20260621_152158/
  status=blocked but much improved
  change: --spiral-z-profile smoothstep, PID unchanged
  time-sync XYZ RMSE=0.030710m, P95=0.050262m, max=0.064932m
  time-sync XY P95=0.038772m, XY max=0.051318m
  time-sync Z P95=0.043973m, Z max=0.062382m
  decision: keep this as the current 100Hz spiral tuning candidate, but do not
  call it a strict pass because P95 is just above 5cm and max remains about
  6.5cm.

rejected / not-promoted candidates:
  Results/sunray_ros1/sunray_ros1_freq100_spiral_zbias_imu100_bestshape_20260621_150754/
    IMU-aligned 100Hz made hover worse and did not solve spiral.
  Results/sunray_ros1/sunray_ros1_freq100_spiral_zbias_thetaramp_bestshape_20260621_151241/
    theta_ramp improved strongly but was slightly worse than smoothstep in P95/max.
  Results/sunray_ros1/sunray_ros1_freq100_spiral_zbias_thetaramp_p48_20260621_151715/
    longer period did not materially improve strict max.
  Results/sunray_ros1/sunray_ros1_freq100_spiral_zbias_smoothz_zlead03_20260621_152622/
    Z-only lead 0.3s did not improve.
  Results/sunray_ros1/sunray_ros1_freq100_spiral_zbias_smoothz_kvz34_20260621_153051/
    higher Kv_z worsened P95/max and is not adopted.

next optimization boundary:
  hover is acceptable.
  figure-8 is close enough for visual review but still has strict time-sync max
  debt.
  spiral still needs either a better estimator/feedback consistency gate or a
  targeted trajectory/controller improvement. Do not restart broad random PID
  sweeps, and do not switch to FAST-LIO/EGO/UE as a substitute for this control
  debt.
```

Reopening the 400Hz physics target requires a separate Gazebo startup
diagnosis. It is a frequency/runtime blocker, not proof that the PID,
trajectory, or MWORKS controller path failed.

Current low-level interface audit, 2026-06-21:

```text
actual current command path:
  Scripts/sunray/sunray_ros1_mission_node.py
  -> /uav1/sunray/uav_control_cmd
  -> References/Sunray/General_Module/sunray_uav_control/uav_control/UAVControl.cpp
  -> PosControlPID::ctrl_update(control_loop_hz)
  -> /uav1/mavros/setpoint_raw/attitude
  -> PX4 attitude/rate/motor pipeline
  -> Gazebo Classic plant

current output type:
  SET_ATTITUDE_TARGET attitude/orientation + normalized thrust

not the current output type:
  not PX4 raw local position/velocity/acceleration control
  not body-rate + thrust control
  not direct actuator/motor control
```

`UAVControl.cpp::send_attitude_setpoint()` sets the
`IGNORE_ROLL_RATE | IGNORE_PITCH_RATE | IGNORE_YAW_RATE` mask and publishes
orientation plus thrust on `/uav1/mavros/setpoint_raw/attitude`. The
`/uav1/mavros/setpoint_raw/local` publisher exists, but in the current mission
path it is used for Offboard/default setpoint handling, not as the trajectory
tracking controller. The Sunray `CTRL_Traj` path already carries desired
position, velocity, and acceleration into `PosControlPID`, but Sunray consumes
those fields internally and converts them into attitude plus thrust.

PX4-supported lower-level candidates for the current ROS1/MAVROS lane:

| Candidate | Interface | Expected benefit | Risk | Gate |
|---|---|---|---|---|
| L1 raw local trajectory setpoint | `/uav1/mavros/setpoint_raw/local` with position + velocity + acceleration feedforward | Uses PX4 `mc_pos_control` trajectory feedforward directly and avoids Sunray's attitude/thrust conversion as the first comparison | PX4 internal position controller differs from Sunray PID; may change baseline behavior | First run only `takeoff_hover_land`, compare against accepted hover baseline before any 8字/spiral |
| L2 body-rate + thrust | `/uav1/mavros/setpoint_raw/attitude` with `IGNORE_ATTITUDE` and body rates + thrust | Bypasses PX4 attitude loop and can reduce attitude-tracking lag if we implement a proper angular-rate controller | Requires a real attitude/rate controller design and saturation/anti-windup; unsafe as a quick patch | Source design and hover-only gate before trajectory work |
| L3 direct actuator/motor | MAVROS actuator or PX4 actuator-level path | Maximum control authority for generated controller work | Bypasses PX4 safety/control allocation assumptions; high risk for the current Sunray ROS1 baseline | Not in the current frequency/error-prevalidation goal |

Bounded L1 raw-local check result: the raw-local/PX4-position-hold candidate
was tried in
`Results/sunray_ros1/sunray_ros1_freq100_hover_interface_px4xyzpos_ctrltraj_20260621_114321/`
and did not improve the hover baseline. It produced steady hover XY
RMSE=0.050126m, XY max=0.062266m, Z RMSE=0.008448m, Z max=0.020757m. Therefore
L1 raw local is not promoted as the current baseline. Next executable rule: do
not start with L2 or L3. Body-rate/thrust or direct actuator/motor control need
a separate controller design and hover-only gate before any trajectory work.

Current PID acceptance boundary:

```text
takeoff-hover-land steady hover:
  XY RMSE <= 0.02m, XY max <= 0.05m
  Z RMSE <= 0.02m, Z max <= 0.05m

figure-8 and spiral:
  report RMSE, P95, and max separately
  target <= 0.05m; do not hide max failures behind shape-only or p95-only pass
```

Current FAST-LIO bridge rule: Sunray's Gazebo MID360 PointCloud2 header can use
wall-clock time while `/uav1/livox/imu` uses Gazebo simulation time. The
FAST-LIO `livox_ros_driver/CustomMsg` bridge must stamp LiDAR frames from the
latest `/uav1/livox/imu` header and must wait for the first IMU stamp before
publishing. If this is violated, `fastlio_mapping.log` reports
`IMU and LiDAR not Synced` and `/cloud_registered`, `/Odometry`, and `/path`
remain empty even though raw `/uav1/livox/lidar` is nonempty.

## 4. Minimum Evidence Gates

### Environment And Source

Before claiming runtime progress, record:

```text
ROS_DISTRO=noetic
Sunray source path under References/Sunray
FAST-LIO source path under References/Lab/FAST_LIO when FAST-LIO is in scope
Gazebo Classic launch path
result directory under Results/sunray_ros1/
```

### MID360 Point Cloud

Topic existence is not enough. A valid MID360 gate requires:

```text
/uav1/livox/lidar type sensor_msgs/PointCloud2
PointCloud2.data nonempty
width * height > 0
point_step and row_step consistent with data length
/uav1/livox/imu present when IMU evidence is in scope
Gazebo log showing Livox plugin load when debugging plugin startup
```

FAST-LIO localization evidence additionally requires:

```text
/mosim/fastlio/livox/lidar type livox_ros_driver/CustomMsg
/cloud_registered nonempty PointCloud2, frame camera_init
/Odometry nonempty nav_msgs/Odometry
/path nonempty nav_msgs/Path
FAST-LIO log has no sustained IMU/LiDAR time-sync errors
```

Known current timing issue: the Livox plugin may publish only after a long
Gazebo startup delay. Short probes around 30-40 seconds can falsely report
missing MID360. Use the bounded long-wait probe before changing architecture:

```bash
bash Scripts/sunray/probe_sunray_ros1_topics.sh
```

Latest accepted long-wait proof:

```text
Results/sunray_ros1/sunray_ros1_topic_probe_longwait_20260620_181942/
```

That probe observed `/uav1/livox/lidar` with nonempty `PointCloud2.data` and
`/uav1/livox/imu`. Use it as timing evidence, not as a mission-completion
claim.

### Takeoff Hover Land

A valid takeoff-hover-land gate needs:

```text
Sunray native control interface in ROS1
Gazebo truth or local pose samples
max height, hover error, XY drift, final height, landing slip
MID360 status if point-cloud review is bundled into the same run
```

Current accepted hover baseline, 2026-06-21:

```text
run:
  Results/sunray_ros1/sunray_ros1_pid_hover_tune_g040_kvi02_imu400_20260621_070126/

Sunray PID parameters:
  quad_mass=0.67
  hov_percent=0.37
  Kp_xy=10.0
  Kv_xy=5.2
  Kvi_xy=0.2
  Kp_z=3.0
  Kv_z=3.0
  Kvi_z=0.6

steady hover:
  XY RMSE=0.019479 m
  XY max=0.035077 m
  Z RMSE=0.013807 m
  Z max=0.021920 m
  status=passed
```

This proves the accepted assembled Sunray150+MID360 plant can take off, hover,
and land inside the current 2cm-RMSE/5cm-max hover boundary. It does not prove
figure-8, spiral climb, FAST-LIO feedback, or MWORKS generated-controller
deployment.

Current accepted px4ctrl + FAST-LIO/PX4-EKF Goal1 baseline, 2026-06-23:

```text
run:
  Results/sunray_ros1/sunray_ros1_fastlio_goal3_ev11_noise003_trim4_zm092_takeoff_hover_land/

runner:
  Scripts/sunray/run_px4ctrl_basic_gate.sh

localization/control boundary:
  FAST-LIO input:
    /uav1/livox/lidar
    /uav1/livox/imu
  FAST-LIO aligned odometry:
    /mosim/fastlio/odom_aligned
  PX4 EKF external vision input:
    /uav1/mavros/vision_pose/pose via Sunray external_fusion
  px4ctrl formal state source:
    /uav1/mavros/local_position/odom
  evaluation truth:
    /uav1/sunray/gazebo_pose only

PX4 EKF parameters:
  EKF2_EV_CTRL=11
  EKF2_HGT_REF=3
  EKF2_EV_DELAY=0
  EKF2_EV_NOISE_MD=1
  EKF2_EVP_NOISE=0.03
  EKF2_EVA_NOISE=0.03

px4ctrl parameters:
  mass=0.67
  hover_percentage=0.30
  thrust_model/estimate_enable=false
  Kp_xy=11.0
  Kv_xy=6.5
  Kp_z=4.0
  Kv_z=4.0
  command bias:
    x=-0.025 m
    y=-0.004 m
    z=-0.092 m

steady hover, last 8s:
  XY RMSE=0.016542 m
  XY max=0.027968 m
  Z RMSE=0.019270 m
  Z max=0.033854 m
  status=passed

FAST-LIO aligned odometry vs Gazebo/Sunray truth:
  XYZ RMSE=0.009498 m
  XY RMSE=0.009116 m
  Z RMSE=0.002669 m
```

This is the first accepted takeoff-hover-land gate where FAST-LIO feeds PX4
EKF and px4ctrl consumes the PX4/MAVROS fused local state. It does not prove
figure-8, spiral, EGO, EGOv2, Diff-Planner, swarm, MWORKS generated code, or
direct FAST-LIO controller feedback.

### Figure-8

A valid figure-8 gate needs:

```text
Sunray native control interface in ROS1
actual trajectory and reference trajectory in the same frame
shape metrics and time-synchronized tracking metrics recorded separately
landing and safety metrics
MID360 nonempty PointCloud2 if the task asks for point-cloud/RViz review
```

Shape-only pass is a review aid. It is not final controller-performance proof.

Current accepted figure-8 baseline, 2026-06-21:

```text
run:
  Results/sunray_ros1/sunray_ros1_pid_figure8_g040_kvi02_kp95_kv52_ramp4_lead02_p42_imu400_20260621_074338/

Sunray PID parameters:
  quad_mass=0.67
  hov_percent=0.37
  Kp_xy=9.5
  Kv_xy=5.2
  Kvi_xy=0.2
  Kp_z=3.0
  Kv_z=3.0
  Kvi_z=0.6

trajectory:
  figure8_amp_x=0.65 m
  figure8_amp_y=0.30 m
  figure8_period=42 s
  laps=2
  ramp=4 s
  trajectory_time_lead=0.2 s

metrics:
  steady hover XY RMSE=0.010503 m
  steady hover XY max=0.022656 m
  steady hover Z RMSE=0.012808 m
  steady hover Z max=0.020612 m
  time-sync RMSE XY=0.020897 m
  time-sync P95 XY=0.039585 m
  time-sync max XY=0.048874 m
  nearest-path/shape RMSE XY=0.016477 m
  nearest-path/shape P95 XY=0.031710 m
  nearest-path/shape max XY=0.045985 m
  status=passed
```

This proves the current Sunray native PID baseline can run the accepted
figure-8 inside the current 5cm strict time-sync max boundary. It does not
prove MWORKS generated-controller deployment, FAST-LIO feedback, planner
readiness, UE acceptance, or multi-UAV readiness.

Current spiral-climb tuning status, 2026-06-21:

```text
best current review run:
  Results/sunray_ros1/sunray_ros1_pid_spiral_kp95_kv52_z306_kviz08_r05_h035_p44_lead02_imu400_20260621_081504/

status:
  blocked, not accepted as final controller pass

Sunray PID parameters:
  quad_mass=0.67
  hov_percent=0.37
  Kp_xy=9.5
  Kv_xy=5.2
  Kvi_xy=0.2
  Kp_z=3.0
  Kv_z=3.0
  Kvi_z=0.8

trajectory:
  spiral_radius=0.50 m
  spiral_height=0.35 m
  spiral_period=44 s
  trajectory_time_lead=0.2 s

metrics:
  steady hover XY RMSE=0.010779 m
  steady hover XY max=0.022108 m
  steady hover Z RMSE=0.014847 m
  steady hover Z max=0.022895 m
  time-sync RMSE XY=0.020528 m
  time-sync P95 XY=0.039316 m
  time-sync max XY=0.054630 m
  time-sync RMSE Z=0.021299 m
  time-sync P95 Z=0.044380 m
  time-sync max Z=0.058130 m
  time-sync RMSE XYZ=0.029581 m
  time-sync P95 XYZ=0.049744 m
  time-sync max XYZ=0.062085 m

remaining blockers:
  strict max XYZ remains above 0.05 m
  XY max and Z max both exceed 0.05 m on the worst samples
  P95 is already inside 0.05 m, so the remaining violation is a peak-error
  / transition / vertical-dynamics problem, not a gross path-shape failure
```

Do not continue by shrinking the scenario until it becomes meaningless. The
next useful work is either a source-backed peak-error diagnosis for the Sunray
PID trajectory follower, or the generated-controller interface route below.

### Gazebo/RViz Review

Visual acceptance requires actual Gazebo/RViz windows or captured evidence from
the current run:

```text
Gazebo Classic vehicle animation with assembled Sunray150
RViz trajectory/path display
RViz MID360 PointCloud2 display when point cloud is in scope
RViz accumulated map-frame point-cloud display when the user asks why points
only persist for a short time or asks for colored map-style point-cloud review
review manifest or screenshots/logs pointing to the exact run
```

Headless gate output does not equal Gazebo GUI animation acceptance.

## 5. MID360 Structure Boundary

Do not collapse these into one value:

```text
mechanical mount pose
Gazebo/Sunray ray sensor local pose
Livox point-cloud coordinate origin
Livox built-in IMU position
FAST-LIO extrinsic_T
```

Current Sunray ROS1 rule:

- Keep the assembled visible MID360 body from the reviewed Sunray150 assembly.
- Do not show the old default `test2.dae` sensor shell as an extra visual
  overlay.
- Keep the Livox sensor plugin and IMU plugin.
- Keep the Livox ray sensor local pose compatible with Sunray's working plugin
  behavior. Current evidence shows that forcing the ray pose to zero can yield
  empty PointCloud2.
- Configure FAST-LIO extrinsics separately from the mechanical mount pose.

Current IMU ownership:

```text
FAST-LIO localization
  -> LiDAR topic: /mosim/fastlio/livox/lidar or /uav1/livox/lidar
  -> IMU topic:   /uav1/livox/imu
  -> source:      MID360 internal IMU simulated by livox_mid360.sdf

PX4 / MAVLink / flight-control simulation
  -> IMU topic:   /imu
  -> source:      flight-controller/body IMU plugin on sunray150_with_mid360

Mission/control helper scripts
  -> use MAVROS/local pose, Gazebo truth, command topics, and review paths
  -> must not claim they use MID360 localization unless FAST-LIO odometry is
     explicitly wired into the closed-loop controller evidence gate
```

Current control-feedback source boundary:

```text
Current Gazebo/Sunray native mission runs:
  command path:
    Scripts/sunray/sunray_ros1_mission_node.py
    -> /uav1/sunray/uav_control_cmd
    -> sunray_uav_control
    -> /uav1/mavros/setpoint_raw/local
    -> PX4 SITL
    -> Gazebo Classic plant

  feedback path used by sunray_uav_control:
    /uav1/sunray/px4_state
    <- external_fusion_node
    <- /uav1/mavros/local_position/pose
    <- /uav1/mavros/local_position/velocity_local
    <- /uav1/mavros/imu/data
    <- PX4 estimator fed by the flight-controller/body IMU chain

  flight-controller/body IMU source:
    sunray150_with_mid360.sdf gazebo_imu_plugin
    -> /imu
    -> PX4 MAVLink imuSubTopic /imu

  MID360/FAST-LIO source:
    livox_mid360.sdf
    -> /uav1/livox/lidar
    -> /uav1/livox/imu
    -> FAST-LIO /cloud_registered, /Odometry, /path

Current status:
  FAST-LIO is a localization/review chain only unless a run explicitly launches
  external_fusion with position_topic:=/mosim/fastlio/odom_aligned, proves PX4
  receives/fuses the vision pose, and proves /uav1/sunray/px4_state follows
  FAST-LIO-backed state.
  Do not report FAST-LIO-controlled flight, MID360-localized control, or
  radar-IMU controller feedback from the current default mission scripts.
```

External fusion integration gate before claiming radar-localized control:

```text
0. Prove the sensor-frame direction first. The MID360 visual shell orientation
   is not evidence of the ray/IMU frame direction. The local SDF removes the
   standalone Livox visual/collision shell and the Livox plugin publishes
   points/IMU in `livox_mid360::base_link`; therefore the test must verify
   point-cloud axes, FAST-LIO yaw, and UAV base axes against Gazebo truth.
1. Run FAST-LIO and prove /Odometry is nonempty nav_msgs/Odometry with stable
   frame convention and timing. Treat `/Odometry` as FAST-LIO
   `camera_init -> Livox body`, not UAV base_link.
2. Run `Scripts/sunray/fastlio_odom_alignment_adapter.py` and prove
   /mosim/fastlio/odom_aligned is `world -> base_link` after applying the
   accepted MID360 mount pose:
   -0.000005 0.032295 0.050167 0 0 4.712389.
3. Launch external_fusion with external_source:=0 and
   position_topic:=/mosim/fastlio/odom_aligned.
4. Record /uav1/mavros/vision_pose/pose and external_odom.fusion_success from
   /uav1/sunray/px4_state.external_odom.
5. Compare /mosim/fastlio/odom_aligned, /uav1/mavros/local_position/pose, and
   /uav1/sunray/uav_state in the same run. The error must be bounded before
   the mission can be called FAST-LIO-backed.
6. The first closed-loop test must be:
   PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=true
   PX4CTRL_ODOM_SOURCE=mavros_local
   MISSION=takeoff_hover_land
   This means FAST-LIO feeds PX4 EKF, while px4ctrl still consumes PX4/MAVROS
   fused local state.
7. Only after that, rerun figure-8 metrics. A pass before
   this gate is PX4/MAVROS-feedback control, not MID360/FAST-LIO-feedback
   control.
```

Current MID360 timing baseline:

```text
Gazebo planning_test physics: stable PID tuning currently uses
`max_step_size=0.001` and `real_time_update_rate=1000`.
The requested 400Hz experiment (`max_step_size=0.0025`,
`real_time_update_rate=400`) currently core-dumps during startup in this lane,
so it is a separate Gazebo startup/frequency blocker, not the active tuning
baseline.
Flight-controller/body IMU: PX4 `gazebo_imu_plugin` publishes `/imu` on every
Gazebo world update. This plugin does not support a separate `pubRate` or
`imuRate` SDF field, so any 400Hz flight-controller IMU claim requires `/imu`
and `/uav1/mavros/imu/data` `rostopic hz` evidence from the same run.
LiDAR ray sensor update_rate: 10Hz unless a separate 20Hz experiment is active.
MID360 internal IMU update_rate: 200Hz in both sensor <update_rate> and
gazebo_ros_imu_sensor <updateRateHZ>.
FAST-LIO scan_rate: 10Hz unless the LiDAR source and bridge are also moved to
20Hz in the same experiment.
```

Rationale: MID360's internal IMU should not be left at the old 100Hz Gazebo
seed when reviewing 20Hz LiDAR/FAST-LIO. A 20Hz LiDAR scan has a 50ms period;
with only about 80-100Hz effective IMU updates, FAST-LIO receives too few IMU
samples per scan for stable initialization and scan undistortion. Before
promoting any 20Hz LiDAR setting, prove `/uav1/livox/imu`, raw LiDAR, bridge,
`/cloud_registered`, `/Odometry`, and `/path` rates in the same run.

Current coordinate-frame split:

```text
sunray150_with_mid360 SDF include pose
  -> mechanical mount from UAV base_link to livox_mid360::base_link
  -> accepted MoSim assembly pose:
     -0.000005 0.032295 0.050167 0 0 4.712389

FAST-LIO mapping/extrinsic_T and mapping/extrinsic_R
  -> LiDAR point-cloud frame pose in MID360 internal IMU body frame
  -> current local FAST-LIO config value:
     extrinsic_T = [0.0, 0.0, 0.1]
     extrinsic_R = identity

Gazebo Livox ray sensor local pose
  -> local ray emitter pose inside the livox_mid360 model
  -> kept separate from the mechanical mount and FAST-LIO extrinsic
```

Do not write the mechanical mount pose into FAST-LIO `extrinsic_T`. Do not use
the FAST-LIO internal IMU extrinsic as the UAV base_link mount pose. If point
cloud direction, FAST-LIO odometry, or planner map alignment looks wrong, audit
these three transforms separately before changing controllers or planners.
The visible MID360 shell direction is not sufficient evidence: the accepted
assembled aircraft visual may show the connector facing the tail while the
simulated Livox ray/IMU frame still comes from the SDF/plugin `base_link`.
Validate the sensor frame by small controlled motion, not by visual appearance.

Detailed hardware/source index:

```text
Docs/Index/sunray_migration_index.md
Docs/Index/project_work_memory_index.md#42-mid-360
```

## 6. Claim Boundaries

This lane may prove:

```text
Sunray ROS1 mission execution
Gazebo Classic animation/review readiness
real nonempty MID360 PointCloud2 topic
trajectory/path review artifacts
FAST-LIO input/source readiness when the local ROS1 FAST_LIO path is actually used
```

It must not claim:

```text
final MWORKS controller deployment
formal generated C/C++ deployment
PX4 integration
ROS2 route success
planner_ready
final closed_loop acceptance
competition controller performance
multi-UAV readiness
UE scene/material acceptance
```

## 7. First Read Order For This Lane

When a task mentions current Sunray, ROS1, Gazebo Classic, RViz, MID360, or the
current single-thread visual review, read:

```text
1. AGENTS.md
2. Docs/Workflows/new_conversation_context.md
3. Docs/Workflows/sunray_ros1_current_runtime_lane.md
4. Docs/Index/sunray_migration_index.md only when source paths, FAST-LIO, EGO,
   or MID360 geometry/extrinsics are in scope
5. The specific Scripts/sunray/*.sh or *.py entry being executed
```

Do not start from `Docs/Workflows/ros2_runtime_setup.md` unless the user or PMO
explicitly reopens the ROS2/PX4 route.
