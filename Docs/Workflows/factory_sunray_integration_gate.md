# Factory Sunray Integration Gate

> Bounded gate for connecting the accepted Factory L2 Gazebo static scene base
> to the current ROS1/Sunray/Gazebo/PX4/MAVROS runtime lane.

Status: active workflow, 2026-07-01 CST.

## 1. Scope

Use this workflow after a UE-derived Gazebo static scene base has been accepted
through `Docs/Workflows/ue_to_gazebo_static_scene_import.md`.

Current accepted scene base:

```text
scene_profile: Config/gazebo/scene_profiles/factory_l2_static_sunray_scene.json
world: Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/worlds/factoryenvironmentcollect_l2_static_review.sdf
models: Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/models
optional_launch: Scripts/sunray/factory_l2_sunray_px4_gazebo.launch
```

Latest accepted FS1a evidence:

```text
Results/sunray_ros1/factory_l2_sunray_fs1a_aligned_20260701_235306/
```

This proves bounded single-UAV spawn, MAVROS connection, and nonempty MID360
PointCloud2 in the Factory L2 scene. It does not prove FS1b mission runtime,
planner behavior, UE Data Bridge, or final closed-loop acceptance.

Latest accepted FS1b/px4ctrl mission evidence:

```text
Results/sunray_ros1/factory_l2_px4ctrl_l1_awff_takeoff_hover_land_20260702_003341/
```

This proves bounded single-UAV takeoff-hover-land in the Factory L2 scene using
the current Sunray/PX4/MAVROS/px4ctrl authority route. It does not prove Diff
planner behavior, multi-UAV behavior, MWORKS/codegen regression in Factory, UE
Data Bridge, or full-system Factory acceptance.

Latest accepted single-UAV Diff planner evidence:

```text
Results/sunray_ros1/factory_l2_diff_single_l1_awff_20260702_005615/
```

This proves the Factory L2 scene can run the current single-UAV Diff planner
route through Sunray/PX4/MAVROS/px4ctrl with target hold and bounded landing
evidence. It does not prove three-UAV behavior, MWORKS/codegen regression in
Factory, UE Data Bridge, or full-system Factory acceptance.

Latest accepted three-UAV Diff planner evidence:

```text
Results/sunray_ros1/factory_l2_diff_swarm_3uav_l1_awff_20260702_025108/
```

This proves the Factory L2 scene can run the current three-UAV Diff scripted
target route through Sunray/PX4/MAVROS/px4ctrl with target hold and inter-UAV
safety metrics. `EGO_SWARM_METRICS.json` reports `status=passed`, blockers
`[]`, minimum inter-UAV distance `0.9848678640870179 m`, and execute target
errors `0.023462082073575096 m`, `0.031877418887012336 m`, and
`0.08656129372835616 m`. It does not prove autonomous exploration coverage,
MWORKS/codegen regression in Factory, UE Data Bridge, or final full-system
acceptance.

This workflow proves only that the accepted Factory scene base can be used by
the current Sunray ROS1 runtime lane. It does not prove UE rendering, Data
Bridge, SLAM/localization, planner, swarm, controller-performance, or final
closed-loop acceptance.

## 2. Gate Levels

| Gate | Purpose | Minimum Evidence | Claim Allowed |
|---|---|---|---|
| FS0 static preflight | Prove paths, JSON, XML, and SDF are structurally valid. | JSON/XML parse, launch XML parse, `gz sdf -k`, Sunray ROS1 preflight. | Factory scene base is structurally launchable. |
| FS1a single-UAV spawn/sensor runtime | Prove one Sunray150+MID360 can spawn in Factory, connect MAVROS, and publish nonempty MID360 data. | Result directory, `FACTORY_SUNRAY_SPAWN_GATE.json`, `SESSION.json`, MAVROS connected sample, `/uav1/livox/lidar` nonempty sample, model states, roslaunch log. | Factory scene base is usable for bounded single-UAV spawn and sensor startup. |
| FS1b single-UAV mission runtime | Prove the accepted spawn/sensor setup can also run a bounded px4ctrl takeoff/hover/land or equivalent mission. | Result directory, px4ctrl run manifest/metrics, MAVROS connected sample, `/uav1/livox/lidar` nonempty sample, mission metrics/logs. | Factory scene base is usable for a bounded single-UAV Sunray/PX4/MAVROS/px4ctrl runtime/sensor/mission gate. |
| FS2 RViz/manual visual review | Prove RViz displays the same run's trajectory and point-cloud/map evidence. | RViz logs plus screenshot/review manifest tied to FS1 run. | RViz visual review of Factory/Sunray sensor/trajectory is accepted. |

Run FS0 before FS1a. Run FS1b only after FS1a passes, or when the task
explicitly accepts mission-level diagnosis. FS2 may be a separate user-review
step if the user wants to inspect windows or screenshots.

## 3. FS0 Static Preflight

From Windows PowerShell:

```powershell
@'
import json, pathlib, xml.etree.ElementTree as ET
root = pathlib.Path("C:/Users/HP/Desktop/MoSim")
for rel in [
    "Config/gazebo/scene_profiles/factory_l2_static_sunray_scene.json",
    "Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/MANIFEST.json",
    "Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/VERIFICATION.json",
]:
    json.loads((root / rel).read_text(encoding="utf-8"))
for rel in [
    "Scripts/sunray/factory_l2_sunray_px4_gazebo.launch",
    "Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/worlds/factoryenvironmentcollect_l2_static_review.sdf",
]:
    ET.parse(root / rel)
print("factory FS0 json/xml OK")
'@ | python -
```

Then validate the Factory world with Gazebo Classic:

```powershell
wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim &&
  GAZEBO_MODEL_PATH="$PWD/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/models:$GAZEBO_MODEL_PATH" \
  gz sdf -v 1.6 -k Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/worlds/factoryenvironmentcollect_l2_static_review.sdf'
```

Run the current Sunray lane preflight:

```powershell
wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim &&
  bash Scripts/sunray/check_sunray_ros1_runtime_preflight.sh'
```

## 4. FS1a Bounded Spawn/Sensor Gate

Use the project wrapper script so the Factory world, Factory model path,
Sunray model paths, PX4 ROS package path, and evidence names are consistent:

```powershell
wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim &&
  RUN_ID=factory_l2_sunray_fs1a_spawn_$(date +%Y%m%d_%H%M%S) \
  GUI=false UAV_NUM=1 TOTAL_TIMEOUT_S=90 MAVROS_READY_TIMEOUT_S=60 \
  LIDAR_READY_TIMEOUT_S=60 \
  bash Scripts/sunray/run_factory_l2_sunray_spawn_gate.sh'
```

FS1a is the first runtime gate after static map acceptance. If it fails, do not
run mission/planner/UE work until the result directory classifies the startup
blocker.

## 5. FS1b Bounded Mission Gate

Use the current px4ctrl basic gate with the Factory world and Factory Gazebo
model path. This keeps the runtime authority in the current
Sunray/Gazebo/PX4/MAVROS/px4ctrl lane and treats Factory only as the static
scene base.

Recommended first command:

```powershell
wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim &&
  RUN_ID=factory_l2_px4ctrl_takeoff_hover_land_$(date +%Y%m%d_%H%M%S) \
  WORLD_FILE=$PWD/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/worlds/factoryenvironmentcollect_l2_static_review.sdf \
  GAZEBO_MODEL_PATH=$PWD/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/models:$GAZEBO_MODEL_PATH \
  GUI=false REVIEW_OPEN_RVIZ=false REVIEW_START_FASTLIO=false MISSION=takeoff_hover_land \
  TOTAL_TIMEOUT_S=180 MAVROS_READY_TIMEOUT_S=70 \
  bash Scripts/sunray/run_px4ctrl_basic_gate.sh'
```

The command is intentionally headless. It may run the takeoff-hover-land mission
because that is the smallest existing single-UAV px4ctrl gate that exercises
spawn, MAVROS, PX4, Gazebo, controller command flow, and MID360 readiness
without planner or UE involvement.

Current accepted F2 route uses `PX4CTRL_CORE_PROFILE=l1_awff` and the Factory
launch file:

```powershell
wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim &&
  RUN_ID=factory_l2_px4ctrl_l1_awff_takeoff_hover_land_$(date +%Y%m%d_%H%M%S) \
  WORLD_FILE=$PWD/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/worlds/factoryenvironmentcollect_l2_static_review.sdf \
  GAZEBO_MODEL_PATH=$PWD/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/models:$GAZEBO_MODEL_PATH \
  SUNRAY_GAZEBO_LAUNCH_FILE=$PWD/Scripts/sunray/factory_l2_sunray_px4_gazebo.launch \
  GUI=false REVIEW_OPEN_RVIZ=false REVIEW_START_FASTLIO=false \
  MISSION=takeoff_hover_land PX4CTRL_CORE_PROFILE=l1_awff \
  TOTAL_TIMEOUT_S=180 MAVROS_READY_TIMEOUT_S=130 \
  FREQUENCY_AUDIT_DURATION_S=10 CONTROL_DIAGNOSTICS_DURATION_S=30 TIME_TF_AUDIT_DURATION_S=30 \
  POST_MISSION_DIAGNOSTIC_GRACE_S=2 \
  bash Scripts/sunray/run_px4ctrl_basic_gate.sh'
```

The takeoff-hover-land default mission arguments include `--land-wait-s 25`,
`--force-disarm-after-land`, and a bounded wait for the vehicle to descend below
the force-disarm height before sending disarm. This is a gate/mission-script
settling fix, not a controller retune.

Sunray native `takeoff_hover_land` may still be used as a diagnostic, but it is
not the current control-authority acceptance gate. The run below is recorded as
a native mission diagnostic blocker, not a Factory scene rejection:

```text
Results/sunray_ros1/factory_l2_sunray_fs1b_takeoff_hover_land_20260701_235637/
```

## 6. FS1 Pass Conditions

FS1a passes only when the result directory contains:

```text
FACTORY_SUNRAY_SPAWN_GATE.json status passed
SESSION.json status passed
mavros_state_connected.txt showing connected: True
livox_lidar_ready_sample.txt with a PointCloud2 sample
model_states_last.txt with Gazebo model states
roslaunch_factory.log tied to the Factory world
```

FS1b px4ctrl passes only when the result directory contains:

```text
RUN_MANIFEST.json with mission_exit_code 0
PX4CTRL_BASIC_MISSION_METRICS.json showing the mission passed
mavros_state_first.txt showing connected: True
trajectory/control diagnostics and frequency artifacts
world_file matching Factory L2 review world in the run manifest
```

If FS1a passes but takeoff/hover/land metrics fail, record FS1b status as
`sensor_spawn_pass_mission_failed` and do not claim single-UAV mission runtime
pass. Diagnose the mission failure under
`Docs/Workflows/sunray_ros1_current_runtime_lane.md`.

If takeoff/hover/land metrics fail but spawn, MAVROS, and nonempty MID360 are
present, record status as `sensor_spawn_pass_mission_failed` and do not claim
single-UAV runtime pass. Diagnose the mission failure under
`Docs/Workflows/sunray_ros1_current_runtime_lane.md`.

## 7. FS2 RViz Review

Run FS2 only when the task explicitly needs visual RViz evidence. It may use
the same FS1 result directory if RViz was enabled, or a separate review run
with `RVIZ=true`.

FS2 must capture:

```text
RViz trajectory or point-cloud screenshot
RViz config path
the FS1 run/result directory being reviewed
whether the screenshot proves trajectory, raw MID360 scan, accumulated map, or only window state
```

Do not use Gazebo GUI screenshots as a replacement for RViz point-cloud or
trajectory evidence.

## 8. Failure Classification

| Failure | Classification | Response |
|---|---|---|
| `gz sdf -k` fails | static scene blocker | Fix scene/SDF/model path first; do not launch runtime. |
| Sunray preflight fails | runtime lane blocker | Fix Ubuntu-20.04/ROS1/Gazebo/Sunray/PX4/Livox preflight first. |
| FS1a launch exits before MAVROS | runtime startup blocker | Inspect `roslaunch_factory.log`, PX4 ROS package path, Gazebo plugin/model paths, stale processes, and Factory world loading. |
| `/gazebo/spawn_sdf_model` does not return, Gazebo reports factory sensor init timeout, and PX4 waits for TCP 4560 | gazebo model spawn/sensor-init blocker | Treat MAVROS disconnect as downstream; align the wrapper with the proven Sunray/Goal5 Livox overlay and MID360 startup defaults before changing Factory geometry. |
| MAVROS never connects after spawn service returns cleanly | runtime startup blocker | Inspect `sunray_gazebo.log`, PX4/MAVROS logs, stale processes, and ports. |
| MID360 remains empty | sensor blocker | Inspect Livox plugin load, `GAZEBO_MODEL_PATH`, assembled model sync, and `/uav1/livox/imu`. |
| Mission fails after sensor readiness | controller/mission blocker in Factory | Keep FS1 partial evidence; do not blame UE or static import until logs prove collision/free-space. |
| RViz does not show data but topics are nonempty | display blocker | Debug RViz fixed frame, display type, queue, decay, and config. |

## 9. Reporting Boundary

Report FS1a completion as:

```text
Factory L2 static scene base passed/failed bounded single-UAV Sunray spawn and
MID360 sensor startup gate.
```

Report FS1b completion as:

```text
Factory L2 static scene base passed/failed bounded single-UAV Sunray runtime
spawn/sensor gate.
```

Do not report:

```text
UE-Gazebo communication is complete
UE rendering mirror is complete
SLAM/planner is complete
full Factory closed loop is accepted
competition runtime is complete
```
