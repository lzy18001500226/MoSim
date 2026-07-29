# Sunray ROS1 Execution Checklist

> Short execution checklist for the current MoSim runtime lane. Use this after
> `Docs/Workflows/sunray_ros1_current_runtime_lane.md` when the task is to make
> real progress on the current ROS1/Sunray/Gazebo/RViz system.

Status: active current checklist, 2026-07-01 CST.

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

If the task does not name a gate, choose the smallest gate that advances the
current board and state it before acting.

## 2. Read Only The Needed Context

Default current context:

```text
AGENTS.md
Docs/Workflows/new_conversation_context.md
Docs/Workflows/mainline_operations_board.md
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

Failure classification:

| Symptom | Classification | Required Response |
|---|---|---|
| `lsb_release -rs` is not `20.04`, `/opt/ros/noetic/setup.bash` is missing, or `/usr/share/gazebo/setup.sh` is missing | wrong distro/runtime entry | stop; relaunch through `wsl -d Ubuntu-20.04`; do not debug planner/controller/plugin parameters |
| `gzserver --version` is unavailable or does not report Gazebo Classic | wrong Gazebo runtime | stop; this is not a Sunray ROS1 lane run |
| `/opt/mosim_work/sunray_ws/Sunray` or PX4 SITL paths are missing | runtime workspace blocker | stop and repair the Sunray/PX4 workspace; do not substitute ROS2/x500 |
| `/opt/mosim_work/sunray_ws/Sunray/simulation/gazebo_plugin/livox_laser_simulation` is missing but `References/Sunray/simulation/gazebo_plugin/livox_laser_simulation` exists | plugin source path drift | use the repo-local source and project-local `Results/sunray_ros1/workspaces/sunray_livox_plugin_ws` build route |
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

For a self-service no-flight infrastructure check, use the root-level `cmd/`
Windows entrypoints instead of manually composing terminal commands:

```text
cmd/01_启动Sunray基础自检.cmd
cmd/02_启动Sunray基础可视化审核.cmd
cmd/00_停止Sunray基础仿真.cmd
```

The first entry proves only `Gazebo + PX4 + MAVROS + nonempty MID360` in a
grounded, unarmed state. The second retains the verified runtime for Gazebo
inspection until `Ctrl+C`; its terminal and per-run `STATUS.md` remain the
first error surface. The stop entry deliberately refuses to terminate a
non-foundation managed run. It is not a substitute for FAST-LIO, controller,
planner, or formation gates.

Before the first flight mission after a fresh GPS/SDF change, run the dedicated
GPS/EKF boot-only gate. It starts no controller, external-fusion node, arming,
or mission publisher, and it must leave an explicit state-chain result before
the takeoff-hover-land gate is allowed:

```powershell
wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/run_sunray_gps_state_chain_gate.sh'
```

Read `GPS_STATE_CHAIN_STATUS.json` first. A pass requires the project-local
nested GPS model, `EKF2_GPS_CTRL=7`, MAVROS global/home/local observations,
Gazebo-local passive agreement, and a matching PX4 ULog analysis. A missing
ULog or partial state observation is a blocker, not a reason to continue to
flight.

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

Use `cmd/启动Diff交互审核.cmd` as the normal Windows
double-click entry for manual Diff-Planner review. The implementation script is
`Scripts/sunray/start_diff_interactive_review.ps1`, but do not double-click the
`.ps1` file because Windows may open it as text instead of executing it. The
`.cmd` entry runs the Sunray ROS1 preflight, opens the point-cloud and 3D-grid
RViz windows, and sets the review defaults to:

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

Use `cmd/关闭Diff交互审核.cmd` to stop an active Diff-Planner
interactive review. `cmd/关闭所有RViz窗口.cmd` only closes RViz windows; it does not
stop Gazebo, PX4, MAVROS, Diff-Planner, px4ctrl, or the Goal4 adapter/helper
nodes. Before starting a new Diff review after a failed or abandoned run, stop
the previous Diff review first; otherwise stale ROS nodes can keep old
parameters such as `DIFF_CMD_MAX_Z=1.35` or `virtual_ceil_height=1.6` alive and
invalidate the new evidence.

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

or double-click the `cmd/` helper:

```text
cmd/build_g8_mworks_closeout.cmd
```

Only rerun G7B/G7C runtime gates when a generated controller or scoped
regression needs fresh evidence. The next mainline branch after user review is
controller-family expansion using G8 as the template; do not retune px4ctrl or
planner parameters while entering that branch unless a regression gate proves
the frozen runtime baseline changed.
