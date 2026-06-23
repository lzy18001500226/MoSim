# CoSim Architecture Draft Audit 2026-06-14

Status: first-pass audit.

## 1. Completed In This Rebuild

- Created a layered `Docs/CoSim` directory structure.
- Moved previous root-level long research notes into `research/raw/` without
  editing their contents.
- Recorded raw-file hashes in
  `cache/source_migration_manifest_20260614.md`.
- Added a common template for reviewed research decisions.
- Wrote first reviewed research decision set:
  - Gazebo / PX4 / ROS2;
  - Simulink / generated code / autopilot deployment;
  - JSBSim / ArduPilot;
  - UE / AirSim / visualization;
  - RL and high-speed physics backends;
  - SLAM / planner / MAV layer;
  - backend decision matrix.
- Wrote first discussion drafts for:
  - platform blueprint;
  - shared core and contracts;
  - vehicle-family tree;
  - backend adapter contract.

## 2. Semantic Preservation Check

| Topic from old notes | New location |
|---|---|
| CoSim as multi-domain composable platform | `00_platform/00_CoSim总体蓝图.md` |
| One entity has one physics truth | `00_platform/00_CoSim总体蓝图.md`, `30_backend_adapters/README.md` |
| Gazebo/PX4/ROS2 multirotor route | `research/01_Gazebo_PX4_ROS2.md`, `20_vehicle_families/multirotor/README.md` |
| Simulink future codegen route | `research/02_Simulink_Codegen_Autopilot.md`, `10_shared_core/01_共享内核与数据契约.md` |
| JSBSim fixed-wing route | `research/03_JSBSim_ArduPilot.md`, `20_vehicle_families/fixed_wing/README.md` |
| UE/AirSim frontend and sensor API ideas | `research/04_UE_AirSim_Visualization.md` |
| MuJoCo/Isaac/Genesis RL role | `research/05_RL_Physics_Backends.md` |
| SLAM/planner/map/MAV boundaries | `research/06_SLAM_Planner_MAV.md` |
| Fixed-wing, VTOL, ducted model-aircraft trees | `20_vehicle_families/*/README.md` |

## 3. Known Incompleteness

The draft is sufficient for user discussion, not final enough for
implementation. Remaining research gaps:

1. Gazebo curated note should later cite exact local `References/Gazebo`
   snapshot repos and selected versions.
2. PX4 and ArduPilot version compatibility must be verified before runtime
   work.
3. Simulink/UAV Toolbox installed versions and license availability are not
   checked in this rebuild.
4. Isaac/Genesis details remain high-level; final adoption needs install and
   GPU/runtime feasibility checks.
5. VTOL backend selection remains open.
6. Ducted model-aircraft route needs user-selected benign scenario and fidelity
   target.
7. UE sensor formal-authority policy remains open.

## 4. No-Claim Boundary

This rebuild did not run:

- Gazebo;
- PX4;
- ROS2;
- JSBSim;
- Simulink;
- MWORKS;
- UE;
- any live HIL/SIL/runtime task.

Therefore the new docs are architecture and research organization outputs, not
runtime evidence.
