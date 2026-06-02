# ROS2 Runtime Setup

> Last updated: 2026-06-01. Scope: WSL2 Ubuntu 22.04 runtime for UE scene
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

Current validated project commands:

```bash
DRY_RUN=1 MAX_FRAMES=2 RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros2.sh factoryenvironmentcollect
DRY_RUN=1 MAX_FRAMES=2 RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros2.sh derelictcorridormegascans
DRY_RUN=1 MAX_FRAMES=2 Scripts/UE5/run_fastlio_rviz_replay_ros2.sh factoryenvironmentcollect
DRY_RUN=1 MAX_FRAMES=2 START_RVIZ=0 Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh factoryenvironmentcollect
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
- `START_RVIZ=0 START_FASTLIO=0 LOOP=1 MAX_FRAMES=20 FPS=2
  Scripts/UE5/run_fastlio_rviz_replay_ros2.sh factoryenvironmentcollect`
  plus `REQUIRE_FASTLIO_OUTPUTS=0 Scripts/UE5/check_fastlio_ros2_topics.sh`
  passed for replay input topics.

Use RViz2 for manual visual review when a GUI window is appropriate.

## Runtime Boundary

Active point-cloud and map review must use RViz2 or an equivalent native
robotics viewer. Browser HTML is not accepted as runtime mapping evidence.

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
`Results/unreal_scene_mapping/SPARK_FASTLIO_ROS2_CANDIDATE.md/json`. Without a
local overlay it reports missing `pcl_ros`. The script can avoid sudo by
downloading the `ros-humble-pcl-ros` deb and extracting it under ignored
`Results/tmp/ros2_overlay_pcl_ros`; this makes `pcl_ros` visible only for the
current project workflow. The system install equivalent is:

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
FASTLIO_ROS2_LAUNCH_CMD='ros2 launch spark_fast_lio mapping_mit_campus.launch.yaml start_rviz:=false scene_id:=mosim robot_name:=base_link base_frame:=base_link map_frame:=ue_world' \
  START_FASTLIO=1 START_RVIZ=0 \
  Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh factoryenvironmentcollect
```

Important topic detail: `spark_fast_lio` publishes odometry on the relative
topic `odometry`, which appears as `/odometry` without a namespace. The older
FAST-LIO ROS1 examples commonly use `/Odometry`. When validating this candidate,
use:

```bash
FASTLIO_ODOMETRY_TOPIC=/odometry Scripts/UE5/check_fastlio_ros2_topics.sh
```

Keep `runtime_claimable=false` until a live run records FAST-LIO output topics,
not only replay input topics.

## References

- ROS2 Humble Ubuntu deb install:
  `https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html`
- ROS2 mirrors:
  `https://docs.ros.org/en/humble/Installation/ROS-2-Mirrors.html`
- FishROS installer:
  `http://fishros.com/install`
