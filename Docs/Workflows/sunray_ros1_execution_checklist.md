# Sunray ROS1 Execution Checklist

> Short execution checklist for the current MoSim runtime lane. Use this after
> `Docs/Workflows/sunray_ros1_current_runtime_lane.md` when the task is to make
> real progress on the current ROS1/Sunray/Gazebo/RViz system.

Status: active current checklist, 2026-07-01 CST.

## 0. Current Supported C99 Single-Aircraft Baseline

The only supported Windows runtime route is the source-local graphical px4ctrl
C99 baseline. It has three completed evidence records:

| Demonstration | Passed evidence | What it proves |
| --- | --- | --- |
| Nominal takeoff, hover, land, disarm | `Results/sunray_ros1/sunray_ros1_graphical_c99_takeoff_hover_land_20260731_002/` | C99 adapter, MAVROS, PX4, FAST-LIO state chain, and Sunray/Gazebo complete the lifecycle |
| Bounded wind injection | `Results/sunray_ros1/sunray_ros1_graphical_c99_wind_hover_20260801_002/` | The same C99 lifecycle completes and Gazebo accepts the configured wind wrench |
| Rotor-1 efficiency 0.85 and reset | `Results/sunray_ros1/sunray_ros1_graphical_c99_motor_fault_recovery_20260731_002/` | The same C99 lifecycle completes and the physical actuator plugin acknowledges loss and recovery |

The entrypoints are deliberately small and terminal-visible:

```text
Scripts/cmd/00_准备C99单机环境.cmd
Scripts/cmd/01_运行C99单机起飞悬停降落.cmd
Scripts/cmd/02_运行C99风扰闭环.cmd
Scripts/cmd/03_运行C99电机故障恢复闭环.cmd
```

Run the preparation entry after a fresh clone or runtime-source change, then
run exactly one demonstration. A fresh run must create a new timestamped
directory under `Results/sunray_ros1/`; never substitute an old result bundle
for a new execution. Check `px4ctrl_build_backend.txt` for
`graphical_px4ctrl_c99`, then inspect the designated JSON status file named by
`Scripts/cmd/README.md`.

The baseline uses `PX4CTRL_HOVER_PERCENTAGE=0.456`, GPS removed, FAST-LIO to
PX4 external vision, and `/uav1/mavros/local_position/odom` as px4ctrl's only
state input. Gazebo truth only supports the simulation alignment adapter and
is never supplied directly to px4ctrl. The nominal record uses FAST-LIO
`0.02 m` filters; the wind and motor records use `0.5 m`, so they are not a
strict same-parameter performance comparison. QGC, UE, RViz, planners, and
multi-aircraft behavior are outside this C99 acceptance scope.

### 0.1 C99 Planner And Three-UAV Status

The project-local FUEL, Swarm-Formation, and Diff-Swarm wrappers are development
gates, not supported acceptance entrypoints yet. Their 2026-08-02 source-local
status is recorded at
`Results/sunray_ros1/c99_planner_runtime_closeout_20260802/C99_PLANNER_RUNTIME_CLOSEOUT.json`:

| Route | Local build | Runtime status | Stop condition |
| --- | --- | --- | --- |
| FUEL single-aircraft exploration | passed | blocked before an executable exploration trajectory | The generated C99 vertical position/velocity gains are fixed at `1.5/1.5`, while the selected runtime profile advertises `4/4`; the aircraft reaches about `3.53 m` rather than FUEL's `1.2 m` initialization height. |
| Swarm-Formation three-aircraft | passed | blocked before px4ctrl or formation launch | The three-aircraft PX4/MAVROS bootstrap is not stable. |
| Diff-Swarm three-aircraft | passed | blocked before px4ctrl or Diff-Planner launch | Shares the same three-aircraft PX4/MAVROS bootstrap blocker. |

Use `Scripts/sunray/run_c99_fuel_gate.sh` and
`Scripts/sunray/run_c99_multiuav_planner_gate.sh` only to reproduce the stated
blockers or after their separate controller/bootstrapping repairs. Do not alter
FAST-LIO map/filter parameters to mask either blocker, and do not claim planner,
avoidance, trajectory, or swarm-separation success from the local-build result.

### 0.2 C99 Diff-Swarm Staged Debug Route

`run_c99_multiuav_planner_gate.sh` remains the compatibility regression gate.
For C99/Diff-Swarm diagnosis, use the staged route instead of treating that
large runner as the only observable entrypoint:

```text
prepare_c99_diff_swarm_runtime.sh
run_c99_diff_swarm_components.sh
run_c99_diff_swarm_mission.sh
review_c99_diff_swarm_run.sh
stop_c99_diff_swarm_components.sh
```

The prepare stage records the resolved workspace and coordinate contract but
starts no runtime. The components stage remains in its own foreground terminal
after it writes `C99_DIFF_SWARM_COMPONENTS_READY.json`; it retains ownership of
Gazebo/PX4/MAVROS/px4ctrl/bridges/planner while the mission stage runs in a
second terminal. Review is read-only. Stop sends `SIGINT` only to the recorded
components runner, which performs its own cleanup. Use a new `RESULT_DIR` for
every staged attempt and do not start another Sunray runtime while that runner
is active.

The single-aircraft counterpart remains
`run_factory_l2_diff_single_c99_gate.sh`. The staged multi-aircraft route and
the single-aircraft gate are independent runtime checks; neither replaces RViz
review, MWORKS formal evidence, or generalized swarm-safety acceptance.

## 1. Goal

Before changing files or running live tools, write the local goal in one
sentence. It must name the evidence gate:

```text
source/runtime preflight
px4ctrl takeoff-hover-land
px4ctrl trajectory or figure-8
MID360 PointCloud2 / RViz review
FAST-LIO standalone review
EGO/EGOv2/Diff-Planner review
MWORKS generated-controller integration slice
```

If the task does not name a gate, choose only the smallest read-only probe that
clarifies the requested scope. Ask before starting a live gate; do not infer a
replacement action from a board or historical status.

## 2. Read Only The Needed Context

Default current context:

```text
AGENTS.md
Docs/Workflows/new_conversation_context.md
Docs/Design/架构.md
Docs/Workflows/sunray_ros1_current_runtime_lane.md
this checklist
```

Then load only the source/script/config needed for the selected gate.

Do not open archived ROS2, UE, or legacy agent workflow bodies during ordinary
Sunray execution.

## 3. Preflight

For a source/static check, inspect paths and run targeted tests only.

For every live Sunray/Gazebo/RViz run, first prove the process is inside the
current runtime lane. From Windows, use an explicit distro command, not bare
`wsl`:

```powershell
wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/check_sunray_ros1_runtime_preflight.sh'
```

The preflight must pass before launching Gazebo, PX4, MAVROS, RViz, FAST-LIO,
EGO, Diff-Planner, or swarm review. It checks Ubuntu-20.04, ROS1 Noetic,
Gazebo Classic, the Sunray/PX4 runtime workspaces, repo-local Sunray and
FAST-LIO sources, and the project-local Livox Gazebo plugin overlay. If the
Livox plugin is missing, build it explicitly:

```bash
PROJECT_ROOT=/mnt/c/Users/HP/Desktop/MoSim \
  bash Scripts/sunray/check_sunray_ros1_runtime_preflight.sh --build-livox
```

The local PX4 SITL build must also contain the complete Sunray Gazebo Classic
plugin bundle. Build it from the project source before the first launch:

```bash
cd /mnt/c/Users/HP/Desktop/MoSim
bash Scripts/sunray/build_local_px4_sitl.sh --build --jobs 2
```

The default build includes GPS, ground-truth, IMU, MAVLink, magnetometer,
barometer, motor, and multirotor-base plugins. Do not use
`--skip-gazebo-classic-plugins` for a reproducibility run. The plugin's
`src/simulation/gazebo/plugins/sunray/livox_laser_simulation/scan_mode/mid360-real-centr.csv`
scan schedule is a required source asset and is checked by preflight.

Failure classification:

| Symptom | Classification | Required Response |
|---|---|---|
| `lsb_release -rs` is not `20.04`, `/opt/ros/noetic/setup.bash` is missing, or `/usr/share/gazebo/setup.sh` is missing | wrong distro/runtime entry | stop; relaunch through `wsl -d Ubuntu-20.04`; do not debug planner/controller/plugin parameters |
| `gzserver --version` is unavailable or does not report Gazebo Classic | wrong Gazebo runtime | stop; this is not a Sunray ROS1 lane run |
| `src/simulation/gazebo/sunray`, `src/flight_stack/px4/PX4-Autopilot`, or the corresponding `build/` output is missing | local source/build blocker | stop and repair the project-local source or generated build workspace; do not substitute ROS2/x500 or an old WSL workspace |
| `src/simulation/gazebo/plugins/sunray/livox_laser_simulation` exists but `build/ros1/local_source_ws/devel/lib/liblivox_laser_simulation.so` is missing | plugin build blocker | use the source-local `--build-livox` preflight route; do not use a prior `Results/` workspace |
| `liblivox_laser_simulation.so` is missing | plugin overlay blocker | run the explicit `--build-livox` preflight or return a blocker |

For a live Sunray/Gazebo/RViz run, verify the selected script and expected
result directory first. Prefer current `Scripts/sunray/` entrypoints:

```text
Scripts/sunray/probe_sunray_ros1_topics.sh
Scripts/sunray/run_sunray_ros1_native_mission_gate.sh
Scripts/sunray/run_px4ctrl_basic_gate.sh
Scripts/sunray/run_mid360_fastlio_10hz_gate.sh
Scripts/sunray/start_sunray_ros1_gui_review.sh
Scripts/sunray/start_mid360_fastlio_review.sh
```

Use `Scripts/gazebo/` only when a current Sunray ROS1 workflow explicitly
points there. Do not choose old ROS2/Gazebo scripts by name similarity.

The older no-flight foundation wrappers are now under
`Scripts/cmd/Archive/legacy_unverified/`. They are retained only for trace-back
and are not a substitute for the C99 baseline in section 0.

The dedicated GPS/EKF boot-only gate is an optional nested-GPS compatibility
diagnostic. It starts no controller, external-fusion node, arming, or mission
publisher. It is not a prerequisite for, and must not configure, the formal
FAST-LIO external-vision flight baseline:

```powershell
wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/run_sunray_gps_state_chain_gate.sh'
```

Read `GPS_STATE_CHAIN_STATUS.json` only when validating the nested GPS model.
A pass requires `EKF2_GPS_CTRL=7`, MAVROS global/home/local observations,
Gazebo-local passive agreement, and a matching PX4 ULog analysis. It does not
authorize flight and does not replace the formal localization state chain.

For the source-local single-aircraft flight baseline, use the explicit
FAST-LIO entry instead. It freezes `SUNRAY_GPS_SENSOR_MODE=removed`,
`EKF2_GPS_CTRL=0`, `EKF2_BARO_CTRL=0`, `EKF2_EV_CTRL=15`,
`EKF2_HGT_REF=3`, and the recorded Gazebo runtime
`PX4CTRL_HOVER_PERCENTAGE=0.456`; FAST-LIO odometry is aligned with Gazebo
truth for the simulated altitude channel, then enters PX4 external vision.
`px4ctrl` still reads only `/uav1/mavros/local_position/odom`.

For the MWORKS graphical-C99 deployment gate, rebuild the controller with
`graphical_px4ctrl_c99` and launch the corresponding runtime profile. The
adapter consumes the exported desired acceleration and attitude commands, while
the recorded Gazebo `0.456` hover-thrust map remains the sole normalized-thrust
calibration. Do not send the graphical model's fixed `0.37` normalization
directly to MAVROS.

```powershell
wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/prepare_local_ros1_workspace.sh --profile controller --build --verify --jobs 1 --px4ctrl-backend graphical_px4ctrl_c99'
wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && PX4CTRL_CORE_PROFILE=graphical_c99 bash Scripts/sunray/run_px4ctrl_fastlio_hover_gate.sh'
```

Classify this gate from `PX4CTRL_BASIC_MISSION_METRICS.json`, not from an
empty mission stdout file. This entry accepts the completed
arm/takeoff/hover/land/disarm lifecycle as the source-local reproducibility
criterion. `px4ctrl_build_backend.txt` must report
`PX4CTRL_BUILD_BACKEND=graphical_px4ctrl_c99`, and `px4ctrl.log` must contain
`runtime_loaded_symbol=MosimPx4ctrlGeneratedGraphStepScalar`. Hover metrics
remain recorded for review but do not block this functional baseline.

### Source-local quick reproduction

Run these commands in order from Windows PowerShell. They build only from
project-owned `src/` trees, then run the single-aircraft functional baseline:

```powershell
wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/build_local_px4_sitl.sh --build --jobs 2'
wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/prepare_local_ros1_workspace.sh --profile foundation --build --verify --jobs 1'
wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/prepare_local_ros1_workspace.sh --profile flight_adapter --build --verify --jobs 1'
wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/prepare_local_ros1_workspace.sh --profile perception --build --verify --jobs 1'
wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/prepare_local_ros1_workspace.sh --profile controller --build --verify --jobs 1 --px4ctrl-backend graphical_px4ctrl_c99'
wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/check_sunray_ros1_runtime_preflight.sh'
wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && PX4CTRL_CORE_PROFILE=graphical_c99 bash Scripts/sunray/run_px4ctrl_fastlio_hover_gate.sh'
```

The last command creates one timestamped directory under
`Results/sunray_ros1/`. Check its `PX4CTRL_BASIC_MISSION_METRICS.json` for
`"status": "passed"`. The flight entry cleans up its own Gazebo/PX4/ROS
processes after landing. Use `Scripts/cmd/停止所有仿真.cmd` only when an abnormal
run has left managed processes behind.

Before MAVROS starts, the base runner writes
`mavros_runtime_config_resolution.json`. It must resolve
`sunray_simulator` to the declared runtime workspace, have the same plugin-list
hash as `Config/gazebo/mavros/px4_pluginlists.yaml`, and whitelist
`home_position` without blacklisting it. This file is the first diagnostic
surface for a missing MAVROS home topic.

Live wait budget: ordinary live probes should wait about 1-2 minutes. A single
blocking command must not wait more than 5 minutes unless the user explicitly
authorizes a longer unattended run for that incident. For controller A/B,
trajectory, planner, FAST-LIO, or swarm batches that need more time, split the
work into one mission/one controller cases, or run in the background and poll
logs/results in short intervals. If useful evidence cannot appear inside this
budget, stop with the partial result directory and a clear blocker/next probe.

When a Windows-side helper generates a WSL shell script, write it with LF line
endings or avoid the generated script and run the command through
`wsl -d Ubuntu-20.04 --exec bash -lc '...'` directly. A CRLF-generated script
can turn the final command into a path ending with `\r`, for example
`run_px4ctrl_ego_single_gate.sh\r`, and fail before runtime evidence is
created. Always save wrapper stdout/stderr into the run directory when starting
background runtime work so early launch failures are visible.

When an ExperimentProfile exists for the selected gate, prepare a formal run
directory before live execution:

```powershell
python Scripts/quality/prepare_experiment_run.py Config/profiles/experiments/<profile>.json --run-id <run_id>
```

Use `Config/profiles/README.md` for the full profile-backed evidence flow.

## 4. Evidence To Save

Every bounded run should leave:

```text
run command and key environment variables
formal result directory under Results/runs/<run_id>/ when an ExperimentProfile exists
domain result directory under Results/sunray_ros1/ for diagnostic or review-specific bundles
RUN_MANIFEST or equivalent manifest
metrics JSON or blocker JSON
topic counts/rates and one representative sample when relevant
Gazebo/RViz screenshot or review manifest when visual review is claimed
stdout/stderr/log paths
final status: passed, failed, or blocker
```

Chat summary alone is not evidence.

For profile-backed runs, close the evidence with:

```powershell
python Scripts/quality/check_run_evidence.py Results/runs/<run_id>
```

## 5. Debug Loop

When something fails:

```text
1. inspect the exact failing log/manifest/metric
2. add narrow logs/prints/checkpoints only around the failing surface
3. inspect local source and official docs
4. if still unclear, search targeted community/blog notes and record the useful source
5. apply one bounded fix and rerun the smallest gate
6. stop and ask the user if the fix would change vehicle, middleware, sensor source, control architecture, or accepted evidence authority
```

Do not switch to ROS2, x500, UE screenshots, fake point clouds, downloaded
FAST-LIO, or truth-feedback-only shortcuts to make the run look successful.

## 6. Review Boundary

Visual review must use real Gazebo/RViz windows or captured evidence tied to
the exact run. A headless numeric pass can be a preflight result, but it is not
Gazebo/RViz visual acceptance.

For point-cloud review, prove nonempty PointCloud2 data before tuning RViz
display settings. If data exists but the display looks wrong, debug RViz
fixed frame, decay time, queue size, color transformer, and accumulated-map
topic selection before blaming the sensor.

For current Sunray ROS1 FAST-LIO/Livox point-cloud review, every enabled or
diagnostic point-cloud display should default to `Size (m): 0.02`. For grid
review, keep point-cloud/map and occupancy-grid windows separate. Goal4 /
Diff-Planner planner-input accumulated-cloud review is the current exception:
use `POINTCLOUD_REVIEW_VOXEL_SIZE_M=0.08` and RViz `Size (m): 0.08` for
`/mosim/goal4/livox_world_accumulated`. The grid window may use a
`PointCloud2` RViz display only for occupancy voxel centers rendered as boxes,
and must not enable raw Livox, FAST-LIO accumulated map, registered scan, or
filtered point-cloud overlays by default.

For Goal4 / Diff-Planner world-cloud input, keep the ground gate at
`POINTCLOUD_MIN_WORLD_Z_M=0.50` for ordinary controller or trajectory gates
unless the run is explicitly a ground-filter diagnostic. The manual Diff
interactive map-review entry is the current exception: it may use
`POINTCLOUD_MIN_WORLD_Z_M=0.20` to keep the lower half of pillar obstacles
visible, but only with clean review accumulation quality gates enabled. The
live `/uav1/livox_world` topic remains the planner input and failure evidence.
The review-only accumulated topics may skip low-height, stale-odom,
high-roll/pitch, high-yaw-rate, or high-speed frames so that transient scan
distortion does not become permanent RViz map pollution; every skipped frame
must be counted in the accumulator JSON. Do not hide raw/live failures: if the
live cloud itself is geometrically wrong, preserve that evidence and debug the
sensor, frame, timestamp, or odometry chain.
Only no-odom, stale-odom, or clearly absurd XY odometry may suppress a
world-cloud publish by default.
Do not change controller gains or trajectory settings while diagnosing a
Goal4 map/point-cloud display issue unless a metrics gate has first shown that
the flight-control loop itself is the failing surface.

For px4ctrl runs that consume `/uav*/mavros/local_position/odom`, do not assume
`nav_msgs/Odometry.twist.twist.linear` is already in the world/map frame. The
current Sunray/PX4/MAVROS lane has shown MAVROS local odom twist matching truth
and position derivative only after rotating the body/base_link velocity by the
odom quaternion. Runners must keep `PX4CTRL_ODOM_VELOCITY_FRAME=body` unless a
new source-specific audit proves world/map velocity semantics. A planner command
that is smooth in position, velocity, Z, and jump metrics can still produce
large px4ctrl attitude commands if this velocity frame is wrong; diagnose the
state field semantics before tuning Diff-Planner, map parameters, or controller
gains.

For Goal4 / Diff-Planner interactive review, update targets with RViz
`2D Nav Goal` only. It publishes `/move_base_simple/goal`, and the Goal4
adapter converts it to `/goal_with_id` at the configured target height.
Manual review defaults to direct final-goal publication:
`DIFF_CLICK_MAX_GOAL_DISTANCE_XY=0` disables adapter-side staged goal splitting
and distance clamping. For tens-of-meters maps, navigation limits should come
from the planner map/horizon/replanning behavior, not from an artificial RViz
goal step limit.
`DIFF_CLICK_STATIC_PATH_GUARD=false` is the default and must remain false for
normal review: the click adapter may validate readiness and reject a final
target inside static obstacle inflation, but it must not run a coarse A*
planner or publish intermediate static waypoints before Diff-Planner sees the
final goal. If a direct start-to-goal line crosses an obstacle, that is input
for Diff-Planner's own local target, map, and replanning logic; adapter-side
static-path staging is diagnostic-only and requires an explicit run note.
When the local map has insufficient view coverage, use the mission-level
in-place yaw scan gate instead of XY goal segmentation. In the normal Diff
interactive review entry, `DIFF_INTERACTIVE_YAW_SCAN_ENABLE=true` commands the
vehicle to hold its current position and sweep yaw before the first interactive
goal is released; `DIFF_INTERACTIVE_YAW_SCAN_AFTER_GOAL=true` repeats the same
map warm-up after each reached goal before the next queued RViz target is
forwarded. This is a LiDAR visibility preparation step only: the adapter still
publishes the final target directly to Diff-Planner. During the yaw scan the
PositionCommand safety adapter may be disabled; the default interactive entry
does not re-enable it immediately after the scan, so the mission node can keep
holding the scanned yaw until a queued goal is actually forwarded and the
planner command stream takes over.
Do not use `Publish Point` as a normal target input because it can only select
rendered point-cloud/geometry surfaces and can place goals inside obstacles.
`/clicked_point` is diagnostic-only unless the run explicitly enables it.

The prior Diff-Planner Windows helper now lives in
`Scripts/cmd/Archive/legacy_unverified/启动Diff交互审核.cmd`. It is a historical
review wrapper, not a current supported entrypoint. The implementation script
is `Scripts/sunray/start_diff_interactive_review.ps1`; use it only after a
separate planner acceptance task explicitly reopens the route. Its historical
review defaults were:

```text
DIFF_INTERACTIVE_REVIEW_HOLD_S=0
TOTAL_TIMEOUT_S=0
GOAL4_RECORD_HZ=100
GOAL4_RECORD_CMD_HZ=100
GOAL4_MAX_PATH_POINTS=0
GOAL4_PATH_PUBLISH_HZ=20
GOAL4_REVIEW_HOLD_PATH_PUBLISH_HZ=10
DIFF_CMD_SAFETY_MAX_POSITION_JUMP_M=0
DIFF_CMD_SAFETY_MAX_POSITION_JUMP_SPEED_MPS=3.0
DIFF_CMD_INVALID_Z_POLICY=clamp
DIFF_CMD_MIN_Z=0.95
DIFF_CMD_MAX_Z=1.15
DIFF_CLICK_STATIC_PATH_GUARD=false
DIFF_INTERACTIVE_YAW_SCAN_ENABLE=true
DIFF_INTERACTIVE_YAW_SCAN_AFTER_GOAL=true
DIFF_INTERACTIVE_YAW_SCAN_DELTA_RAD=3.141592653589793
DIFF_INTERACTIVE_YAW_SCAN_DURATION_S=6.0
DIFF_INTERACTIVE_YAW_SCAN_SETTLE_S=1.0
DIFF_INTERACTIVE_YAW_SCAN_REENABLE_CMD_ADAPTER=false
EGO_VIRTUAL_CEIL_HEIGHT=1.15
EGO_VISUALIZATION_TRUNCATE_HEIGHT=1.25
POINTCLOUD_MIN_WORLD_Z_M=0.20
OCCUPANCY_REVIEW_MIN_Z=0.20
POINTCLOUD_REVIEW_VOXEL_SIZE_M=0.08
POINTCLOUD_REVIEW_QUALITY_ODOM_TOPIC=/uav1/mavros/local_position/odom
POINTCLOUD_REVIEW_MIN_ODOM_Z_FOR_ACCUMULATION=0.85
POINTCLOUD_REVIEW_MAX_ACCUM_ROLL_PITCH_DEG=5.0
POINTCLOUD_REVIEW_MAX_ACCUM_YAW_RATE_DEG_S=30.0
POINTCLOUD_REVIEW_MAX_ACCUM_SPEED_XY_MPS=0.45
```

`DIFF_INTERACTIVE_REVIEW_HOLD_S=0` and `TOTAL_TIMEOUT_S=0` mean manual review
does not expire while RViz is still open. Do not leave RViz/Gazebo alive after
the mission node exits, because `/mosim/goal4/interactive_goal_ready` will be
false and new `2D Nav Goal` clicks will be queued instead of forwarded to
Diff-Planner.

`GOAL4_MAX_PATH_POINTS=0` means the red truth path and green command path are
not truncated during the review. The path sampling rate may be 100Hz, but
`nav_msgs/Path` publication is rate-limited because each publish contains the
whole accumulated path. Do not use a fixed absolute command-position distance
gate to reject long interactive goals; Diff-Planner may legitimately publish a
far trajectory endpoint or terminal hold after replanning. Keep the command
jump guard as a velocity/discontinuity diagnostic unless a run explicitly
investigates adapter safety behavior.

Goal4 / Diff-Planner interactive review is currently a near-constant-altitude
gate, not a free 3D climb test. Target clicks are fixed at `z=1.0`; the planner
virtual ceiling and px4ctrl-facing command adapter must keep the reviewed
trajectory in the narrow height band above. If the raw planner still climbs
toward the ceiling, treat that as a planner/map-parameter problem before tuning
px4ctrl.

The matching Diff stop helper is archived beside it. Do not revive either
helper without first checking the active runtime source, result contract, and
planner acceptance state. Before a future Diff review after a failed or
abandoned run, stop the previous process set before restarting; otherwise stale
ROS nodes can keep old parameters such as `DIFF_CMD_MAX_Z=1.35` or
`virtual_ceil_height=1.6` alive and invalidate the new evidence.

Current single-UAV Diff-Planner freeze, 2026-06-29 CST:

```text
freeze_id: DIFF_SINGLE_GOAL4_BASELINE_20260629
evidence_dir: Results/sunray_ros1/review_diff_interactive_guard_20260629_002228
claim: single-UAV Diff-Planner interactive replanning through FAST-LIO/MID360
       world cloud, px4ctrl, MAVROS, PX4, Gazebo, and RViz review is accepted
       by user for Goal4 baseline freeze.
not_claimed: three-UAV Diff swarm, autonomous exploration, EGO/EGOv2,
             MWORKS codegen, final competition controller performance.
```

After this freeze, the next ROS1 runtime gate is Goal5 Diff-Planner three-UAV:

```text
entry:
  UAV_NUM=3 PLANNER_VARIANT=diff_planner \
  bash Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh

minimum mission:
  uav1/uav2/uav3 simultaneously take off
  -> each receives its scripted target
  -> Diff-Planner publishes per-UAV PolyTraj and position_cmd
  -> public trajectory relay feeds /broadcast_traj_from_planner into
     /broadcast_traj_to_planner for swarm trajectory awareness
  -> each UAV avoids obstacles/other UAVs, reaches, hovers, and lands

manual review:
  scripted targets are the primary gate; RViz hand-click is review-only and
  must not replace the three-UAV scripted acceptance.
```

Current Diff-Planner three-UAV freeze, 2026-06-29 CST:

```text
freeze_id: DIFF_SWARM_GOAL5_BASELINE_20260629
evidence_dir: Results/sunray_ros1/sunray_ros1_goal5_diff_planner_3uav_20260629_023923
status: passed
planner: Diff-Planner multi-UAV planner/traj_server engineering baseline
controller: original Fast-Drone-250 px4ctrl, one instance per UAV
spawn_mode: PRELOAD_GAZEBO_MODELS=false / dynamic spawn
targets:
  uav1: (1.0, -1.0, 1.0)
  uav2: (1.0,  1.0, 1.0)
  uav3: (2.0,  0.0, 1.0)
execute_target_error_m:
  uav1: 0.0057
  uav2: 0.0215
  uav3: 0.0315
min_inter_uav_distance_m: 0.9800
min_inter_uav_pair: uav1-uav3
mission_exit_code: 0
claim: Diff-Planner three-UAV scripted-target engineering baseline through
       px4ctrl, MAVROS, PX4, Gazebo, MID360/FAST-LIO world-cloud topics, and
       trajectory broadcast awareness is accepted for the current Goal5
       runtime gate.
target_safety_note: the accepted target set is intentionally conservative and
                    stays outside pillar radius plus inflation; targets such
                    as (2.5, +/-1.0, 1.0) are near obstacle centers and are
                    not valid as clean swarm acceptance points.
not_claimed: self-developed formation control, autonomous exploration,
             camera-first-person review, Point-LIO, MWORKS-generated
             controller, or PX4-native module deployment.
```

For G9 generated-controller regression on the same Goal5 gate, use dynamic
spawn as the accepted runtime route. Preloaded worlds are diagnostic only
unless a separate frame-alignment fix is proven, because a preloaded run can
make all three MID360 topics appear while shifting PX4/MAVROS local origins
away from the intended world-frame start points. If dynamic spawn shows
occasional MID360 startup absence, retry the startup gate instead of switching
to preload:

```bash
PX4CTRL_CORE_PROFILE=official_pid UAV_NUM=3 PLANNER_VARIANT=diff_planner \
GOAL5_STARTUP_ATTEMPTS=2 \
bash Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh
```

The retry wrapper must only retry startup/sensor/frame readiness exits
(`MAVROS`, local odom, or raw MID360 missing). It must not hide planner,
controller, takeoff, target-hold, separation, or mission failures. Each run
must retain `STARTUP_ATTEMPT_SUMMARY.json` with per-UAV MAVROS, odom, raw
LiDAR, and Gazebo `MoSimLivoxLoadEnter` evidence.

Historical G9 official-PID generated-family Goal5 runtime reinjection closeout,
2026-06-30 CST:

```text
evidence_dir: Results/sunray_ros1/g9_family_official_pid_diff_swarm_3uav_startupretry_20260630_225836
status: passed
mission_exit_code: 0
spawn_mode: PRELOAD_GAZEBO_MODELS=false / dynamic spawn
controller_core_profile: official_pid
startup_attempts: 1 of 2 used
raw MID360 topics: uav1/uav2/uav3 all present
Gazebo Livox load markers: 3
execute_target_error_m:
  uav1: 0.0269
  uav2: 0.0177
  uav3: 0.0391
min_inter_uav_distance_m: 0.9828
home odom minus first truth dxy:
  uav1: 0.0004 m
  uav2: 0.0014 m
  uav3: 0.0075 m
claim: the G9 `ATTITUDE_THRUST` generated-family px4ctrl switch can be
       reinjected into the accepted Sunray/PX4/MAVROS/Diff three-UAV gate for
       the official-PID profile.
not_claimed: PX4-native uORB deployment, BODYRATE_THRUST G9.6 route,
             online nonlinear NMPC, autonomous exploration, or UE authority.
```

Current G10-B/D/E generated-family Goal4/Goal5 runtime reinjection closeout,
2026-07-01 CST:

```text
Diff single-UAV:
  l1_awff:
    Results/sunray_ros1/g10_bde_l1_awff_diff_single_20260701_024916
    status: passed
    execute_target_error_m: 0.0277
  safety_filter:
    Results/sunray_ros1/g10_bde_safety_filter_diff_single_20260701_025540
    status: passed
    execute_target_error_m: 0.0151
  fault_allocation:
    Results/sunray_ros1/g10_bde_fault_allocation_diff_single_20260701_030032
    status: passed
    execute_target_error_m: 0.0345

Diff three-UAV:
  l1_awff:
    Results/sunray_ros1/g10_bde_l1_awff_diff_swarm_3uav_jump08_20260701_031015
    status: passed
    min_inter_uav_distance_m: 0.9778
  safety_filter:
    Results/sunray_ros1/g10_bde_safety_filter_diff_swarm_3uav_jump08_20260701_031532
    status: passed
    min_inter_uav_distance_m: 0.9711
  fault_allocation:
    Results/sunray_ros1/g10_bde_fault_allocation_diff_swarm_3uav_jump08_20260701_032031
    status: passed
    min_inter_uav_distance_m: 0.9773

Goal5 transition guard default:
  EGO_CMD_SAFETY_MAX_POSITION_JUMP_M=0.80
  meaning: accepted hover-hold -> planner-takeover envelope; this is a command
           continuity gate threshold, not a controller/planner tuning gain.
```

Current MWORKS generated-core closeout freeze, 2026-06-29 CST:

```text
freeze_id: G8_MWORKS_FULL_LOOP_BASELINE_20260629
evidence_dir: Results/sunray_ros1/g8_mworks_full_loop_closeout_20260629_115603
status: passed
generated_core_baseline: PX4CTRL_Core_CFunction_Sysblock
validated_chain:
  M1 I/O contract
  -> G5 C++ offline equivalence
  -> G6 C ABI equivalence
  -> M4A MWORKS CFunction check_model / GenerateModelCode
  -> generated-C four-way consistency
  -> G7A static ROS/Sunray ATTITUDE_THRUST adapter
  -> G7B single-UAV Gazebo original/generated A/B
  -> frozen Diff single-UAV baseline
  -> frozen Diff three-UAV baseline
  -> G7C generated-core three-UAV Diff smoke
claim: MWORKS CFunction generated px4ctrl_core is accepted as the current
       generated-core regression baseline for the ROS1/Sunray/PX4/MAVROS/
       px4ctrl/Diff-Planner loop.
not_claimed: advanced controller family implementation, PX4-native uORB module,
             MWORKS GUI synchronous real-time Gazebo co-simulation, autonomous
             exploration, UE/frontend authority, or final competition
             controller performance.
```

The G8 closeout package is file-level validation over already accepted evidence;
it does not start live MWORKS, ROS, Gazebo, PX4, MAVROS, FAST-LIO, Diff-Planner,
or RViz. Rebuild the closeout package with:

```powershell
python Scripts\sunray\px4ctrl_golden_slice\build_g8_mworks_full_loop_closeout.py
```

or use the archived historical helper only for trace-back:

```text
Scripts/cmd/Archive/legacy_unverified/build_g8_mworks_closeout.cmd
```

Only rerun G7B/G7C runtime gates when the current user scopes a generated
controller or regression that needs fresh evidence. Controller-family expansion
is historical planning context, not an automatic next step; do not retune
px4ctrl or planner parameters unless the current task explicitly requires it
and a regression gate proves the frozen runtime baseline changed.
