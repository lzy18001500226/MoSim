# MoSim Design Source

Status: active architecture entry, 2026-06-24.

This directory is the active design source for MoSim. The former numbered
`01-10` design set has been migrated into the documents below and archived
under `Docs/Cache/design/old_architecture/`.

Do not use the old numbered documents as active execution guidance. Use them
only for historical trace-back when a current document explicitly points there.

## Active Reading Order

Read only the smallest set required for the task. For ordinary architecture or
implementation work, start with Level 0 and then enter the relevant Level 1/2
document.

### Level 0: Entry And Scope

| Order | Document | Purpose |
|---:|---|---|
| 1 | `README.md` | Current design entry, document map, and evidence boundary. |
| 2 | `赛题.md` | Competition scope, task boundary, and claim framing. |
| 3 | `需求.md` | MoSim requirement catalog, priority, and acceptance scope. |
| 4 | `架构.md` | Current system architecture decision and execution order. |
| 5 | `架构/README.md` | Topic tree entry and domain routing. |
| 6 | `架构/00_架构与任务/任务路线图.md` section 0 | Current 6-Goal route, post-Goal branches, and project-level capability table. Use this before selecting an implementation task. |

### Level 1: Interfaces And Runtime Boundaries

| Document | Purpose |
|---|---|
| `架构/01_控制器平台/控制平台接口与闭环实施规范.md` | G1-G6 control-platform authority for typed interfaces, composition, module registry, promotion gates, and the bounded Factory fault surface. |
| `架构/00_架构与任务/系统架构问题与决策矩阵.md` | Architecture risks, authority boundaries, remaining design decisions, and traceability matrices that must be frozen before broad implementation. |
| `架构/00_架构与任务/系统集成接口与编排.md` | Cross-module frames, controller core ABI, profiles, orchestration, launch plans, and code-generation coupling boundaries. |
| `架构/00_架构与任务/ExperimentProfile与兼容性矩阵.md` | ExperimentProfile schema, compatibility rejection/degradation matrix, Launch Plan contract, Run Manifest contract, and `Config/profiles/` validation entry. |
| `架构/00_架构与任务/任务算法与场景地图注册接口.md` | MissionAlgorithmRegistry, SceneMapRegistry, planner/exploration/formation adapters, map switching, and the offline QGC 2D map contract. |
| `架构/04_展示与实验平台/Flight Console与二维任务地图详细设计.md` | QGC 5.0.8 reuse audit, UE-centered Flight Console layout, Factory mini/expanded mission map, waypoint/boundary/fleet editing, coordinate and command-authority contracts. |
| `MoSim大系统介绍与学长评审提纲.md` | Shareable system overview that separates accepted runtime evidence, bounded results, source/design readiness, open risks, and questions for external technical review. |
| `架构/01_控制器平台/统一控制接口.md` | State, reference, controller output, adapter, frame, and timing contracts. |
| `架构/02_感知定位与规划集群/FASTLIO定位闭环.md` | FAST-LIO localization, point-cloud/map validation, and planner rerun gates. |
| `架构/02_感知定位与规划集群/规划与编队控制接口.md` | Diff-Planner current loop, EGO/EGO-Swarm references, planner/formation interfaces, and multi-UAV contracts. |
| `架构/03_测试调参与证据/真机化与C++化.md` | Flight-like code responsibility, C++/generated-code boundary, and real-machine sensor assumptions. |
| `架构/04_展示与实验平台/展示与实验平台接口.md` | RViz/Gazebo/UE/Web/QGC display boundary, ExperimentProfile UI entry, evidence capture, and multi-window review layout. |

### Level 2: Controller Implementation And Evidence

| Document | Purpose |
|---|---|
| `架构/01_控制器平台/单机控制器实现.md` | Single-UAV controller-core implementation, including px4ctrl Golden Slice. |
| `架构/01_控制器平台/代码生成与PX4部署.md` | MWORKS/Sysblock code generation and PX4/MAVROS deployment route. |
| `架构/03_测试调参与证据/调参与参数优化.md` | Baseline tuning, error analysis, parameter profiles, and optimization workflow. |
| `架构/01_控制器平台/控制器管理与配置.md` | Controller profiles, configuration, switching policy, and management boundary. |
| `架构/03_测试调参与证据/测试与评价.md` | Offline consistency, Gazebo/RViz evidence gates, metrics, and acceptance rules. |
| `架构/01_控制器平台/控制增强与容错.md` | Safety, disturbance rejection, fault tolerance, and advanced-control backlog. |

### Level 3: Execution Workflow

| Document | Purpose |
|---|---|
| `架构/00_架构与任务/任务路线图.md` | Current Goal route, acceptance gates, and repeatable implementation order. |

Reference-only documents:

```text
Docs/Cache/design/superseded/
Docs/Cache/design/old_architecture/
Docs/Cache/design/consolidation_plans/
```

These are not current execution sources unless a current document explicitly
points to a section for trace-back.

## Current Runtime Boundary

Current executable review lane:

```text
Ubuntu-20.04 / ROS1 Noetic
  -> References/Sunray assembled Sunray150 + MID360
  -> Gazebo Classic
  -> RViz trajectory/path and real MID360 point-cloud review
```

Current controller baseline:

```text
px4ctrl / ATTITUDE_THRUST / MAVROS-PX4 fused state
```

Current code-generation direction:

```text
MWORKS/Sysblock controller core
  -> generated C/C++
  -> IController wrapper
  -> ATTITUDE_THRUST adapter
  -> MAVROS/PX4
  -> Gazebo/Sunray plant
```

Current implementation order:

```text
Goal 1:
  px4ctrl + PX4/MAVROS fused state + Gazebo/RViz baseline takeoff, hover, land.

Goal 2:
  Non-FAST-LIO single-UAV control baseline: step, figure-eight, spiral, circle,
  safety abnormal cases and parameter freeze.

Goal 3:
  FAST-LIO independent localization/mapping evaluation, Diff-Planner single-UAV
  reproduction, and Diff-Planner swarm three-UAV engineering baseline.
  The FAST-LIO independent, PX4-EKF-fused, and Hybrid-Z branches are represented
  as ExperimentProfile configs before runtime claims are allowed.

Goal 4:
  Representative controller template: px4ctrl, official PID, and SE3 Basic.

Goal 5:
  MWORKS px4ctrl Golden Slice: core extraction, offline equivalence, generated
  C/C++, and Gazebo A/B back-integration.

Goal 6:
  MWORKS-generated controller core back into the Diff-Planner single-UAV chain,
  then extend to Diff-Planner swarm only after the single-UAV gate passes.

G8 frozen baseline:
  G8_MWORKS_FULL_LOOP_BASELINE_20260629 is the current generated-core baseline
  for px4ctrl, Diff-Planner single-UAV, and Diff-Planner three-UAV regression.

G9-0:
  ControllerProfile, ExperimentProfile, Launch Plan, Run Manifest, source-basis
  gate, and static rejection checks for the controller-family expansion.

G9-A/F:
  official PID, SE3 Basic, DFBC, SMC, PID-INDI/INDI, and NMPC are released one
  at a time through Docs/Workflows/add_controller.md. Planned controllers stay
  under Config/profiles/candidates/ and must reject with C-CTRL-01 before
  implementation evidence exists.

Post-G9 controller route:
  G9.5/G9.6 paper-grade high-performance and robust controller reproduction
  -> G10 augmentation matrix and ablation
  -> G11 all implemented/accepted controllers and augmentation combinations
     through MWORKS/codegen, offline equivalence, ROS/Sunray reinjection, and
     Gazebo regression.

Post-G11 branches:
  FAST-LIO through PX4 EKF state-source A/B as a separate localization branch,
  PX4-native uORB deployment as a later gated route, and UE/QGC/frontend
  display integration only after the controller/codegen loop is stable.
```

Before starting a non-trivial task, identify its project-level capability block
from `架构/00_架构与任务/任务路线图.md` section 0.3:

```text
S0 scope
S1 runtime baseline
S2 state source / sensing / localization
S3 single-UAV control baseline
S4 trajectory and mission reference
S5 single-UAV planning and local map
S6 multi-UAV / swarm baseline
S7 MWORKS Golden Slice and code generation
S8 controller family expansion
S9 robustness / safety / fault tolerance
S10 C++ / real-machine readiness
S11 visualization / UE / frontend
S12 automated evaluation / report / delivery
```

Do not infer the task order from the longest topic document. The current
6-Goal route in `架构/00_架构与任务/任务路线图.md` is the execution selector;
topic documents provide contracts and gates after the task block is chosen.

Historical/future routes such as ROS2 Humble, PX4-native `x500`, downloaded
replacement FAST-LIO source, fake point clouds, and direct Python controller
shortcuts are not current runtime evidence unless a later user/PMO decision
explicitly reopens them.

## Legacy Design Archive

The old numbered design set is archived here:

```text
Docs/Cache/design/old_architecture/
```

Archived files:

```text
01_系统目标与需求边界.md
02_总体架构与权威边界.md
03_核心模块设计.md
04_接口数据契约与时钟频率.md
05_场景传感器与UE_ROS2链路.md
06_控制规划安全与评估目标.md
07_验收Gate与交付物.md
08_赛题闭环实现证据矩阵.md
09_多机编队架构与数据设计.md
10_四旋翼模型与RuntimePlant设计.md
```

Historical cache and migration notes live under:

```text
Docs/Cache/design/consolidation_plans/
```

## Evidence Rule

Design documents define architecture, interfaces, workflows, and gates. They do
not prove runtime success by themselves. Runtime claims still require source,
logs, metrics, screenshots, result bundles, or return packets under the
corresponding workflow.
