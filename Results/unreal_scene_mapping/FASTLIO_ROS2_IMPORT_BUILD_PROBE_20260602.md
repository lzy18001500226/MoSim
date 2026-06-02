# FAST-LIO ROS2 Import / Build Probe, 2026-06-02

Status: blocked but informative.

## External Candidate Import

Command:

```bash
git ls-remote --heads https://github.com/Ericsii/FAST_LIO_ROS2.git ros2
```

Result:

```text
timed out after 60s
```

Interpretation:

- `Ericsii/FAST_LIO_ROS2` branch `ros2` remains the preferred external
  candidate to evaluate because visible metadata suggests ROS2, Mid360, and
  `livox_ros_driver2` support.
- It is not local evidence yet. Do not claim it builds or runs in MoSim until
  it is imported, built, and evaluated in `Results/tmp/fastlio_ros2_candidates/`.

## Local Dependency Probe

Environment:

```text
ROS2 Humble: present at /opt/ros/humble
colcon: /usr/bin/colcon
local livox_ros_driver2: Scripts/ros/livox_ros_driver2
```

Important shell rule:

```bash
set +u
source /opt/ros/humble/setup.bash
set -u
```

Using `set -u` while sourcing ROS2 setup directly fails with
`AMENT_TRACE_SETUP_FILES: unbound variable`.

## Local spark-fast-lio Build Probe

Workspace:

```text
Results/tmp/spark_fastlio_build_probe_ws/
```

Command:

```bash
set +u
source /opt/ros/humble/setup.bash
set -u
colcon build --packages-select livox_ros_driver2 spark_fast_lio --event-handlers console_cohesion+
```

Result within the 60s interactive-command gate:

- `livox_ros_driver2` built and installed successfully in about 23.5s.
- `spark_fast_lio` started CMake/configuration.
- No immediate compiler or CMake error was seen before the 60s timeout.
- No residual `colcon`, `cmake`, `gmake`, or `spark_fast_lio` process remained.

Interpretation:

- ROS2 and `livox_ros_driver2` are available.
- The current local `spark-fast-lio` build is not proven complete.
- Even if it builds, it remains not Mid360-claimable until the Livox CustomMsg
  path is patched and runtime output topics pass truth-error gates.

## Next Action

1. Retry external candidate import when network is responsive.
2. If external import remains blocked, run a dedicated longer build/check task
   for local `spark-fast-lio`, but only as a patch candidate.
3. Do not open UE/RViz windows or tune display settings until a headless
   FAST-LIO runtime publishes nonzero registered cloud, odometry, and path.
