# MoSim Design Source

Status: rebuilt source set, 2026-06-11.

This directory defines what MoSim is intended to be. It is not a transcript of
current implementation status, not a packet ledger, and not an engineering task
queue.

MoSim is a layered-authority UAV simulation and verification system for the A8
quadrotor task. The system should let a user configure a scenario, run a
reproducible UAV experiment, review dynamics/control/perception/planning
evidence, and export report-ready results.

Current priority is competition closure first: implement the required A8
functions, including official PID baseline analysis, optimized Sysblock
controller integration, Syslab quantitative metrics, and multi-UAV formation
verification. Broader MoSim platform work continues after the competition
functional loop is complete.

## Reading Order

| Order | Document | Purpose |
|---:|---|---|
| 1 | `01_系统目标与需求边界.md` | Product goal, users, scope, non-goals, phased capability map. |
| 2 | `02_总体架构与权威边界.md` | RflySim-style four-layer architecture: Modeling/MIL-SIL, Flight Control, Runtime Plant/Sensors/HIL, Display/Scene/Review. |
| 3 | `03_核心模块设计.md` | RunManager, adapters, plant, sensor, localization, planner, flight control, and evidence modules mapped to the four layers. |
| 4 | `04_接口数据契约与时钟频率.md` | Typed data contracts, command/echo, clocks, frames, and rates. |
| 5 | `05_场景传感器与UE_ROS2链路.md` | Scene, sensor oracle, robotics integration, FAST-LIO, local map, and planner observation boundary. |
| 6 | `06_控制规划安全与评估目标.md` | Control, planning, safety, fault, formation, and metric goals. |
| 7 | `07_验收Gate与交付物.md` | Competition gates, post-competition extension gates, evidence bundles, deliverables, and failure rules. |
| 8 | `08_赛题闭环实现证据矩阵.md` | Current C0/C1/C2 implementation evidence matrix before post-competition platform expansion. |
| 9 | `09_多机编队架构与数据设计.md` | Multi-UAV formation architecture, identity model, result layout, database policy, and phased implementation plan. |
| 10 | `14_ROS2正式接入与控制器后端迁移设计.md` | Formal ROS2 integration route, controller ABI, generated C/C++ gate, and future Simulink replacement policy. |

## Active Reference And ADR Files

These files remain active references until their still-valid semantics are fully
absorbed or moved into an ADR folder:

- `10_架构边界与当前状态ADR.md`
- `11_RflySim式MoSim最小闭环架构审核.md`
- `12_MoSimQuadrotorModel模型归档与迁移计划.md`
- `13_RflySim四旋翼模型对标与MoSim优化路线.md`
- `design_rebuild_audit_20260610.md`

## Cache

Pre-rebuild design inputs live under:

```text
Docs/Design/cache/pre_rebuild_20260610/
```

Cached files are not deleted. They are historical design inputs whose current
semantics must be absorbed into this source set before the root design relies
on the replacement.

## Design Principle

Design the whole system now, but keep the execution priority explicit:

```text
A8 competition functional closure
  -> official PID baseline and limitation analysis
  -> optimized MWORKS.Sysblock controller implementation
  -> MWORKS-hosted Modeling / Flight-Control / Runtime-Plant integration
  -> Syslab quantitative metrics
  -> multi-UAV / formation verification
  -> competition evidence bundle
  -> post-competition MoSim platform expansion
```

Competition closure may host Modeling/MIL-SIL, Flight Control, and Runtime
Plant/Sensors/HIL roles inside MWORKS for speed. That is an implementation
slice, not a collapsed authority model. PX4/QGC, separated CopterSim-like
Runtime Plant, HIL, real-sensor migration, and broader robotics-platform work
are designed now but do not block the competition functional loop unless a
later requirement explicitly makes them part of the competition claim.

The design now treats ROS2 as the formal robotics integration layer for the
complete system route, while keeping MWORKS as the current competition/modeling
backend. The design reserves stable contracts for:

- ROS2/RViz2/FAST-LIO robotics integration;
- PX4 Offboard/SITL/HIL and QGC monitoring;
- future real LiDAR/IMU/hardware-in-the-loop migration;
- multiple localization, local-map, planner, and flight-control backends;
- single-UAV and multi-UAV experiment identities.
- multi-UAV formation contracts that keep per-UAV control, plant, traces, and
  metrics separated before any database or platform browsing layer is added.

No layer may bypass the typed contracts just because an early implementation is
smaller.

## Current Implementation Slice

The current implementation slice is deliberately smaller than the long-term
platform:

```text
MWORKS/Sysplorer/Sysblock/Syslab
  -> controller design and review
  -> Equation-backed executable controller where full graphical embedding is blocked
  -> MWORKS-hosted Flight Control backend
  -> MWORKS-hosted Runtime Plant backend
  -> Syslab-compatible metrics and evidence
```

ROS2 is the intended complete-system robotics middleware route. PX4/QGC, HIL,
and generated C/C++ remain backend-specific gates rather than automatic
prerequisites for every current MWORKS model-optimization claim. A current
competition or model-optimization claim should not wait for PX4 or generated
C/C++ unless a task explicitly moves that backend into the claim scope. If a
task claims perception, localization, local mapping, or planner handoff, it
must follow the ROS2/FAST-LIO evidence gates in `05`, `07`, and `14`.

Controller artifacts have different authority:

| Artifact | Current role |
|---|---|
| Graphical Sysblock controller | Structure/design/review evidence. It should expose the controller logic and remain behavior-equivalent to the executable controller. |
| Equation controller | Current stable full-system execution backend when graphical Sysblock embedding fails in Sysplorer. It may carry formal simulation evidence after equivalence and run gates pass. |
| Generated C/C++ controller | Future deployment/SIL/HIL/PX4-compatible backend. It is optional until generated-runtime authority is claimed. |

Therefore the current route is not "replace graphics with Equation." The route
is "keep graphical Sysblock for human/model-structure review, use Equation as
the stable executable bridge, and preserve a C/C++-ready interface for later."

## Current Evidence Matrix

For implementation-state review, read `08_赛题闭环实现证据矩阵.md` after the
timeless gate rules in `07_验收Gate与交付物.md`. The matrix records which
competition claims are already evidence-backed, which remain partial or
source-static, and which belong only to post-competition platform expansion.
