# ROS2 Runtime Setup

> Last updated: 2026-06-04. Scope: WSL2 Ubuntu 22.04 runtime for UE scene
> mapping, RViz2 review, and FAST-LIO-family integration.

## Decision

Ubuntu 22.04 uses ROS2 Humble for MoSim UE mapping/runtime work. Do not spend
more time trying to install ROS1 Noetic directly on this host.

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
