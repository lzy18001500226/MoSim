# MoSim Design Rebuild Audit, 2026-06-10

Status: first rebuild pass executed.

Purpose: rebuild `Docs/Design/` around the target MoSim system design without
losing useful design semantics from earlier documents.

This audit records the no-loss design rebuild route. The first execution pass
created the new source documents and moved superseded inputs into cache after
their target semantics were restated.

## 1. Rebuild Objective

The new design set should answer:

```text
What are we building?
What problem does it solve?
What layers own which truth?
What modules and interfaces must exist?
What evidence proves a run is valid?
What is P0/P1/P2 scope?
What is explicitly out of scope?
```

It should not primarily answer:

```text
Which department thread is currently assigned?
Which packet was recently accepted?
Which partial implementation already passed?
Which temporary workaround happened in a past run?
```

Those belong in workflows, boards, ADRs, progress, packets, results, or audits.

## 2. Target Design Source Set

Proposed new root-level design documents:

| Target | Responsibility |
|---|---|
| `README.md` | Design entrypoint, reading order, source/current/cache distinction. |
| `01_系统目标与需求边界.md` | Product goal, users, scope, non-goals, P0/P1/P2 requirement boundaries. |
| `02_总体架构与权威边界.md` | Layered architecture and authority split across MWORKS, UE5, ROS2, Results, and optional future PX4. |
| `03_核心模块设计.md` | RunManager, MWORKSCore, UE5SensorOracle, ROS2Bridge, FASTLIOAdapter, PlannerAdapter, EvidenceManager, MoSim Studio. |
| `04_接口数据契约与时钟频率.md` | State, command, runtime echo, sensor, planner setpoint, run manifest, clock and rate contracts. |
| `05_场景传感器与UE_ROS2链路.md` | Scene, UAV visual, camera, collision, LiDAR/IMU, ROS2/RViz/FAST-LIO review path. |
| `06_控制规划安全与评估目标.md` | Control, planning, safety, fault, formation, and metric goals as product design, not status claims. |
| `07_验收Gate与交付物.md` | Gate A-E, evidence bundle, report/video deliverables, acceptance and blocker rules. |
| `08_架构决策记录.md` or `ADR/` | Active decisions, rejected routes, current authority boundary, status-bearing design notes. |

The generated `.docx` reference should not be a design source. It may be cached
or referenced as a review draft after any useful wording is absorbed.

## 3. No-Loss Migration Rules

Before slimming or moving any existing design file:

1. identify the still-valid semantics;
2. choose the new target document that will preserve them;
3. restate them in current product wording;
4. record stale or implementation-status claims that must not be promoted;
5. only then move the old file into `Docs/Design/cache/pre_rebuild_20260610/`
   or mark it as active ADR/reference.

## 4. Current File Audit Matrix

| Current file | Current role | Keep active? | Proposed action | Semantics to preserve | Stale or risky wording to quarantine |
|---|---|---:|---|---|---|
| `00_系统总体设计.md` | Mixed overview: old control-first framing plus newer RflySim-like product ambition and UI split. | Partial | Extract into `01`, `02`, `03`, then cache original. | MWORKS as control/truth authority; UE as renderer/sensor/review layer; front-end command/echo rule; modular product ambition; evidence-first principle. | Layer stack is too broad and mixes product, implementation, MCP automation, and current tooling. Avoid presenting all listed layers as mandatory P0 deliverables. |
| `01_需求范围与验收.md` | Requirement catalog and old P0/P1/P2 split for control, planning, GUI, system closure. | Partial | Rewrite into `01_系统目标与需求边界.md` and `07_验收Gate与交付物.md`, then cache original. | Functional requirement families; non-functional requirements; P0/P1/P2 prioritization; deliverable classes; failure criteria. | Old P0 still centers on CSV/plots/video before full UE/ROS2/FAST-LIO product boundary. Some items read like implementation status instead of product requirements. |
| `02_模型接口与运行流程.md` | Rich interface, coordinate, scenario, result, and MWORKS integration notes. | Partial | Extract into `04_接口数据契约与时钟频率.md`, `03_核心模块设计.md`, and `07`; then cache original. | Coordinate conventions; state preprocessing; dynamics interfaces; control allocation; trajectory/scenario/result contracts; bus concepts; result directory concepts. | Mixes old pure-MWORKS interfaces with later UE/ROS2 route. Needs authority labels and source labels before reuse. |
| `03_控制系统架构.md` | Detailed controller design for PID/AWFF/MPC/NMPC/INDI/L1 and system-state signals. | Partial | Extract current goals into `06_控制规划安全与评估目标.md`; keep detailed equations as cached/reference design. | Controller ladder; robust control goals; INDI/L1/safety/fault allocation concepts; state estimator / flight mode / mission manager / setpoint arbiter signals. | Must not imply all advanced controllers are implemented or accepted. Keep runtime performance claims separate from product design. |
| `04_安全故障与容错.md` | Safety filter, fault injection, detection, reallocation, emergency manager. | Partial | Extract into `06`; cache original as detailed reference. | Safety constraints; CBF/QP-inspired routes; motor efficiency fault; residual detection; control allocation reconstruction; degraded modes; event logs. | Some detailed implementation recipes may be premature for P0 design. Do not make fault reallocation mandatory for minimum credible loop. |
| `05_路径规划与轨迹生成.md` | Broad planning algorithm survey plus later local map and closed-loop planning additions. | Partial | Extract product-level planning scope into `06` and UE/ROS2 map boundary into `05`; cache original as reference. | Planner ladder; minimum snap/B-spline; local A*/fallback; 3D map and collision-check ideas; trackability-aware planning; setpoint outputs. | Too broad for current system design. Avoid claiming EGO/GCOPTER-style integration before adapter and evidence gates exist. |
| `06_多机编队控制.md` | Formation design concepts and metrics. | Partial | Extract concise P2/scope note into `06`; cache original. | Leader-follower, virtual structure, formation switching, collision avoidance, formation metrics. | Not a P0 system-defining requirement. Keep as P2/future capability unless PMO reopens it. |
| `07_场景扰动与测试矩阵.md` | Scenario, disturbance, test matrix, and screenshot list. | Partial | Extract into `01`, `05`, and `07`; cache original. | Scenario profile concept; disturbance/fault matrix; test categories; Factory/UE video-scene idea; evidence screenshot list. | Old scenarios may not match current UE scene/source labels. Avoid treating screenshot lists as acceptance without run evidence. |
| `08_仿真指标与自动评估.md` | Metrics, result structure, GUI metric panel, replay/video evidence concepts. | Partial | Extract into `07_验收Gate与交付物.md` and `03` EvidenceManager; cache original. | Metrics taxonomy; raw/metrics/summary outputs; evidence bundle; replay/video material list; automated analysis duties. | GUI panel details and health scoring may be too implementation-specific for the system design root. |
| `09_UE_ROS_MWORKS无人机仿真架构重构.md` | Large replan and evidence-bearing architecture history after rejecting toy routes. | Active reference, but too large | Split: stable decisions into `02`, `04`, `05`, `07`; detailed history/evidence into ADR/cache. | Hard rejection of grid-cell/fake point-cloud routes; MWORKS/UE/ROS2 authority boundary; timing/topic contracts; Mid360/FAST-LIO constraints; reuse/adapt/reject categories; minimum loop concept. | Contains dated gateway/WeChat notes, current-status evidence, task history, and implementation-step details. Those should not become primary system design. |
| `10_架构边界与当前状态ADR.md` | Active ADR for current authority boundary and status. | Yes | Keep active as ADR source, but cross-link from new `08_架构决策记录.md` or `ADR/README.md`. | Current accepted authority boundary; Gazebo/Sunray plugin translation; parameter credibility labels; RflySim reference boundary; timing policy; anti-regression checklist. | It is status-bearing. Do not merge all current status into timeless design; keep ADR date and status explicit. |
| `11_RflySim式MoSim最小闭环架构审核.md` | Gap audit against RflySim-like platform. | Active reference | Keep as audit/reference until design rebuild extracts product target and gap classes. | Nine-module target table; minimum closed-loop gap; dynamics upgrade need; PX4 as contract reference; ROS2 native review; UE command echo need. | Completion percentages and current evidence are dated. Keep as audit, not product spec. |
| `12_MoSimQuadrotorModel模型归档与迁移计划.md` | Model package organization and migration plan. | Active implementation plan | Keep outside root design source or move later to workflow/model-plan area after review. | Formal package ownership; category tree; rename/disposition policy; acceptance gates for `.mo` organization. | This is implementation/migration planning, not product system design. Do not fold into high-level requirements except for model ownership summary. |
| `MoSim 无人机仿真系统详细设计文档.docx` | External/generated reference draft supplied by user. | No | Cache or leave as reference input; do not treat as source of truth. | Useful current wording around target system, P0/P1/P2, module names, gates, data contracts. | Generated by another agent; may include unreviewed claims and should not override project docs. |

## 5. Proposed Current Product Wording

Use this as the rebuild anchor unless the user changes it:

> MoSim is a layered-authority UAV simulation and verification system for the
> A8 quadrotor task. MWORKS/Sysplorer/Sysblock/Syslab owns dynamics, control,
> truth, experiments, metrics, and report evidence. UE5/MoSimSceneLibrary owns
> scene rendering, aircraft visual review, camera/collision/sensor oracle, and
> video output. ROS2/RViz2/FAST-LIO/planner components own robotics transport,
> localization/map/planner review, and setpoint traces. The system succeeds when
> it can produce reproducible run bundles with explicit authority boundaries,
> source labels, timing contracts, metrics, visual evidence, and clear blockers.

## 6. Execution Record

The first rebuild pass created:

```text
Docs/Design/README.md
Docs/Design/01_系统目标与需求边界.md
Docs/Design/02_总体架构与权威边界.md
Docs/Design/03_核心模块设计.md
Docs/Design/04_接口数据契约与时钟频率.md
Docs/Design/05_场景传感器与UE_ROS2链路.md
Docs/Design/06_控制规划安全与评估目标.md
Docs/Design/07_验收Gate与交付物.md
Docs/Design/cache/pre_rebuild_20260610/README.md
```

The first rebuild pass moved these pre-rebuild inputs into
`Docs/Design/cache/pre_rebuild_20260610/`:

```text
00_系统总体设计.md
01_需求范围与验收.md
02_模型接口与运行流程.md
03_控制系统架构.md
04_安全故障与容错.md
05_路径规划与轨迹生成.md
06_多机编队控制.md
07_场景扰动与测试矩阵.md
08_仿真指标与自动评估.md
09_UE_ROS_MWORKS无人机仿真架构重构.md
MoSim 无人机仿真系统详细设计文档.docx
```

The first rebuild pass kept these active references in the root:

```text
10_架构边界与当前状态ADR.md
11_RflySim式MoSim最小闭环架构审核.md
12_MoSimQuadrotorModel模型归档与迁移计划.md
```

Updated indexes:

```text
Docs/Index/doc_index.md
Docs/Index/workflow_index.md
Docs/Index/project_work_memory_index.md
Docs/Index/sunray_migration_index.md
Docs/Index/px4_reference_index.md
Docs/Workflows/new_conversation_context.md
```

## 7. Remaining Decisions

1. Should the new root design set use the 7-document structure in section 2,
   or should `05` and `06` be merged later to keep the root smaller?
2. Should `10_架构边界与当前状态ADR.md` and `11_RflySim式MoSim最小闭环架构审核.md`
   remain at root as active ADR/audit, or move under a new `ADR/` folder after
   the root design set exists?
3. Should implementation-heavy model migration content from `12` remain in
   `Docs/Design/` or be moved later to `Docs/Workflows/` or a model-specific
   planning folder?

## 8. Next Safe Step

After review, refine the new source documents for technical depth, then decide
whether to create `Docs/Design/ADR/` for `10/11` and whether to move `12` to a
workflow or model-maintenance area.
