# MoSim Design Source

Status: active architecture entry, 2026-06-23.

This directory is the active design source for MoSim. The former numbered
`01-10` design set has been migrated into the documents below and archived
under `Docs/Design/旧架构/`.

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
| 3 | `架构.md` | Current system architecture decision and execution order. |
| 4 | `MoSim控制体系总览.md` | Formal control-system root and controller roadmap. |

### Level 1: Interfaces And Runtime Boundaries

| Document | Purpose |
|---|---|
| `MoSim统一控制接口规范.md` | State, reference, controller output, adapter, frame, and timing contracts. |
| `MoSim_FASTLIO定位闭环与规划复现基础方案.md` | FAST-LIO localization, point-cloud/map validation, and planner rerun gates. |
| `MoSim规划与编队控制接口规范.md` | EGO/EGO-Swarm/planner/formation interfaces and multi-UAV contracts. |
| `MoSim真机化收尾与C++化重构方案.md` | Flight-like code responsibility, C++/generated-code boundary, and real-machine sensor assumptions. |

### Level 2: Controller Implementation And Evidence

| Document | Purpose |
|---|---|
| `MoSim单机控制器实现规范.md` | Single-UAV controller-core implementation, including px4ctrl Golden Slice. |
| `MoSim控制器代码生成与PX4部署规范.md` | MWORKS/Sysblock code generation and PX4/MAVROS deployment route. |
| `MoSim控制器调参与参数优化规范.md` | Baseline tuning, error analysis, parameter profiles, and optimization workflow. |
| `MoSim控制器管理与配置规范.md` | Controller profiles, configuration, switching policy, and management boundary. |
| `MoSim控制系统测试与评价规范.md` | Offline consistency, Gazebo/RViz evidence gates, metrics, and acceptance rules. |
| `MoSim控制增强与容错规范.md` | Safety, disturbance rejection, fault tolerance, and advanced-control backlog. |

### Level 3: Execution Workflow

| Document | Purpose |
|---|---|
| `MoSim研发工作流与Agent任务编排规范.md` | Agent execution workflow, task gates, and repeatable implementation order. |

Reference-only documents:

```text
MoSim体系.md
Docs/Design/旧架构/
Docs/Design/cache/
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
1. Minimal big-system loop:
   Sunray/PX4/MAVROS/px4ctrl + Gazebo + RViz + MID360/FAST-LIO gates
   + EGO/EGOv2/Diff-Planner + EGO-Swarm 2/3-machine smoke.

2. Representative controller template:
   px4ctrl baseline, official PID, and SE3 Basic only.

3. MWORKS Golden Slice:
   MWORKS model -> generated C/C++ -> offline equivalence -> Adapter
   -> same Sunray/PX4/Gazebo closed loop.

4. Batch controller expansion:
   improved PID, LQI, DFBC, LMPC/NMPC, INDI, L1, safety, and fault-tolerance
   controllers are released one at a time after the template is proven.
```

Historical/future routes such as ROS2 Humble, PX4-native `x500`, downloaded
replacement FAST-LIO source, fake point clouds, and direct Python controller
shortcuts are not current runtime evidence unless a later user/PMO decision
explicitly reopens them.

## Legacy Design Archive

The old numbered design set is archived here:

```text
Docs/Design/旧架构/
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
Docs/Design/cache/
```

## Evidence Rule

Design documents define architecture, interfaces, workflows, and gates. They do
not prove runtime success by themselves. Runtime claims still require source,
logs, metrics, screenshots, result bundles, or return packets under the
corresponding workflow.
