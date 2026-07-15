# CoSim Rebuild Plan 2026-06-14

Status: archived/reference rebuild plan. This file is not a current MoSim
execution route unless the user explicitly reopens CoSim architecture work.

## 1. Goal

Rebuild `Docs/CoSim` from a flat pile of technology notes into a layered,
vehicle-family-first blueprint for a future CoSim platform.

The rebuild order is:

```text
preserve raw research
  -> write reviewed research decisions with a common template
  -> compare backends against CoSim requirements
  -> define vehicle-family capability trees
  -> extract shared platform architecture
  -> write implementation roadmap only after architecture review
```

Do not treat early architecture drafts as final product truth until the
reviewed research decisions and user review converge.

## 2. User Requirements Captured

CoSim is intended to become a larger simulation software platform, not only an
A8 quadrotor competition repository.

Required long-term capability families:

- quadrotor and multirotor simulation;
- multirotor swarm, formation, exploration, person-following, obstacle
  avoidance, SLAM, mapping, planning, end-to-end learning, and reinforcement
  learning experiments;
- fixed-wing model-aircraft simulation;
- VTOL / quadplane / lift-plus-cruise simulation;
- ducted model-aircraft and benign test-body simulation;
- software-in-the-loop, hardware-in-the-loop, and real-hardware deployment
  path;
- Simulink as the future controller design and generated-code route after the
  competition period;
- ROS2 + Gazebo as the default multirotor robotics/plant route after the
  current MWORKS-first slice;
- UE as high-quality rendering, review, console, and optional sensor frontend;
- backend replaceability instead of hard-binding the platform to one simulator.

## 3. Rebuild Principles

1. Vehicle families are the top-level product tree.
2. Shared platform services are factored out once and reused by each vehicle
   family.
3. Simulation backends are adapters, not the main document structure.
4. Raw research is preserved and moved under `research/raw`.
5. Reviewed research decisions are short, template-based, and decision-oriented.
6. Formal architecture documents cite reviewed research decisions rather than
   rereading long raw notes.
7. A single entity must declare one authoritative physics backend for a run.
8. Render truth, plant truth, flight-control authority, algorithm state, and
   evidence state must remain separate.
9. Benign model-aircraft and hobby simulation is in scope. Weaponization,
   targeting, destructive payload design, and deployment guidance are out of
   scope.

## 4. Logical Subagent Plan

No user-visible Codex threads were created for this rebuild. The work is split
into logical research lanes inside this thread:

| Lane | Scope | Output |
|---|---|---|
| Gazebo/PX4/ROS2 lane | multirotor engineering truth, SITL/HIL, ROS bridge, sensor topics | reviewed research decision + multirotor architecture |
| JSBSim/ArduPilot lane | fixed-wing and aircraft dynamics, ArduPlane, aero data path | reviewed research decision + fixed-wing architecture |
| RL physics lane | MuJoCo, Isaac, Genesis, Bullet, Flightmare and batch training | reviewed research decision + RL/high-speed notes |
| UE/AirSim lane | UE plugin architecture, sensor API, rendering/frontend split | reviewed research decision + visualization boundary |
| Autonomy lane | SLAM, local map, planner, MAVLink, multi-UAV command layer | reviewed research decision + shared bus contracts |
| Documentation lane | raw preservation, research-decision template, index, cache manifest | cache plan + README/index |

## 5. Target Directory Shape

```text
Docs/CoSim/
  README.md
  cache/
    cosim_rebuild_plan_20260614.md
    source_migration_manifest_20260614.md
    research_template_20260614.md
  research/
    raw/
    01_Gazebo_PX4_ROS2.md
    02_Simulink_Codegen_Autopilot.md
    03_JSBSim_ArduPilot.md
    04_UE_AirSim_Visualization.md
    05_RL_Physics_Backends.md
    06_SLAM_Planner_MAV.md
    07_Backend_Decision_Matrix.md
  00_platform/
  10_shared_core/
  20_vehicle_families/
    multirotor/
    fixed_wing/
    vtol/
    ducted_model_aircraft/
  30_backend_adapters/
```

## 6. Current User-Review Boundary

This rebuild produces a first architecture draft for discussion. It does not:

- claim Gazebo/PX4/ROS2/UE runtime implementation is complete;
- change current A8 competition gates;
- replace the current MWORKS evidence route;
- approve real-hardware flight;
- create or dispatch CoAgent visible threads;
- delete raw research content.
