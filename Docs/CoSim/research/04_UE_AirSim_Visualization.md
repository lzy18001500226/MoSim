# UE / AirSim / Project AirSim

Status: reviewed research decision draft, 2026-06-14.

Source raw notes:

- `research/raw/AirSim.md`
- `research/raw/Project AirSim.md`
- `research/raw/Cosys-AirSim.md`
- `research/raw/rclUE.md`

External sources:

- AirSim documentation: https://microsoft.github.io/AirSim/
- AirSim code structure: https://microsoft.github.io/AirSim/code_structure/
- Project AirSim repository: https://github.com/iamaisim/ProjectAirSim

## 1. Position

UE is CoSim's high-quality visualization, review, operator-console, replay, and
optional visual/sensor frontend. AirSim and Project AirSim are architecture
references for turning UE from a passive renderer into a programmable vehicle
and sensor environment.

The default CoSim position is:

```text
Gazebo / JSBSim / MWORKS / MuJoCo / Isaac owns plant truth
UE consumes confirmed state and renders it
UE may generate labelled sensor observations when that sensor profile is active
```

## 2. Best-Fit Vehicle Families

| Vehicle family | Fit | Reason |
|---|---|---|
| Multirotor | default frontend | High-quality UAV mesh, camera, LiDAR/depth visualization, experiment console, replay. |
| Fixed-wing | default frontend | Aircraft visual, control-surface animation, terrain/sky review. |
| VTOL | default frontend | Transition visualization and reviewer-facing state. |
| Ducted model-aircraft | default frontend | Visual review and short high-speed replay. |
| Ground/heterogeneous future | optional | AirSim/CARLA-like actor/sensor ideas can be reused. |

## 3. Authority Classification

| Authority surface | Classification |
|---|---|
| Plant truth | Not default plant truth. UE physics must be labelled if used. |
| Flight-control authority | No default authority. UI commands must go through command/echo adapters. |
| ROS2 / algorithm bus | rclUE/ROS plugins are integration options, not global bus replacement. |
| UE / rendering frontend | Default authority for visual rendering and human review surface. |
| Sensor generation | Optional authority for camera/depth/raycast/LiDAR profiles if labelled and validated. |
| RL / batch training | Useful for photorealistic data and embodied visual tasks; not default high-throughput physics. |
| SIL / HIL / deployment | Review and replay surface only unless a specific AirSim/PX4/HIL route is adopted. |

## 4. Integration Pattern

Default CoSim route:

```text
authoritative plant state
  -> state frame / transform adapter
  -> UE vehicle actor, scene actor, camera, audio, and overlay
  -> screenshot/video/replay evidence
  -> optional UE sensor observation frame
  -> ROS2 / logging / planner only if source-labelled
```

Rejected default route:

```text
UE hidden scene geometry
  -> planner final evidence
```

Truth-map debugging is allowed only under a `truth_debug` or `truth_map`
label, not as sensor-based autonomy.

## 5. Strengths

- Best surface for human review, media, scene aesthetics, and visual fidelity.
- AirSim-style plugin architecture demonstrates how to expose camera, depth,
  segmentation, LiDAR, collision, and vehicle APIs.
- UE can host an RflySim-like experiment console while remaining a frontend.
- Project AirSim illustrates runtime component composition and configuration
  patterns that CoSim can copy without adopting the whole stack.

## 6. Gaps And Risks

- UE tick/render time should not become the authoritative physics clock.
- rclUE/ROS plugins can create platform/Windows maintenance friction.
- Visual truth, scene geometry truth, sensor observations, and plant truth can
  be confused unless the run manifest labels them.
- AirSim classic is valuable as a reference but should not become the default
  long-term foundation without a compatibility audit.

## 7. CoSim Adoption Decision

Decision: default frontend and architecture-reference route.

UE is mandatory for high-quality review and replay, but not mandatory for every
headless simulation. AirSim/Project AirSim/Cosys-AirSim are reference
architectures and optional implementation sources, not default plant truth.

## 8. Required Next Evidence

- State-frame contract: coordinate system, units, timestamp, vehicle ID, and
  scene ID.
- UE replay smoke that consumes authoritative state without writing back.
- Sensor-profile gate for UE camera/depth/LiDAR output if used by algorithms.
- Experiment console command/echo proof before UE UI can affect active runs.

