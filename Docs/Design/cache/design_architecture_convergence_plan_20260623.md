# MoSim Design Architecture Convergence Plan

Status: cache migration design, not yet executed.

Date: 2026-06-23

Purpose: define how to converge the legacy `Docs/Design/01-10` design set into
the newer `Docs/Design/架构` architecture set without losing evidence, plant,
or formation-specific content.

This file is a migration design only. It does not by itself delete, move, or
supersede any active document.

## 1. Decision Summary

The newer `Docs/Design/架构` set should become the formal architecture source of
truth for the current MoSim control/runtime design.

The legacy `Docs/Design/01-10` set should not remain a parallel active entry
tree. All durable content should be migrated into the newer architecture set;
the old files should then be archived under
`Docs/Design/旧架构/` after unique content is preserved.

After migration, no legacy `01-10` document should remain as an active design
source in `Docs/Design/`. The only active root file in that folder should be
`README.md`, and it should route agents to `Docs/Design/架构`.

Do not directly delete old files before:

1. unique content is extracted;
2. indexes and workflow references are updated;
3. stale references are checked with `rg`;
4. the migration diff passes markdown/path sanity checks.

## 2. Target Source Of Truth

Formal architecture entry:

```text
Docs/Design/MoSim控制体系总览.md
```

Formal first-stage runtime basis:

```text
Sunray ROS1 / Gazebo Classic / RViz / px4ctrl / ATTITUDE_THRUST
```

Formal first-stage state-source policy:

```text
PX4/MAVROS fused state for controller baseline.
Gazebo truth for evaluation and Z-height substitute experiments when explicitly
declared.
FAST-LIO first as independent localization/map validation, then as a controlled
state-source replacement experiment.
```

Formal first-stage controller deployment boundary:

```text
MWORKS/Sysblock controller core -> generated C/C++ -> IController wrapper
-> ATTITUDE_THRUST adapter -> MAVROS/PX4 -> Gazebo/Sunray plant
```

The active architecture set should be treated as:

| Role | Document |
|---|---|
| Control architecture entry | `Docs/Design/MoSim控制体系总览.md` |
| Competition task scope | `Docs/Design/赛题.md` |
| Unified control interface | `Docs/Design/MoSim统一控制接口规范.md` |
| Single-UAV controller implementation | `Docs/Design/MoSim单机控制器实现规范.md` |
| Code generation and PX4 deployment | `Docs/Design/MoSim控制器代码生成与PX4部署规范.md` |
| Tuning and parameter optimization | `Docs/Design/MoSim控制器调参与参数优化规范.md` |
| Controller management/configuration | `Docs/Design/MoSim控制器管理与配置规范.md` |
| Controller testing/evaluation | `Docs/Design/MoSim控制系统测试与评价规范.md` |
| Control enhancement and fault tolerance | `Docs/Design/MoSim控制增强与容错规范.md` |
| Planning and formation interface | `Docs/Design/MoSim规划与编队控制接口规范.md` |
| FAST-LIO localization loop and planner reproduction base | `Docs/Design/MoSim_FASTLIO定位闭环与规划复现基础方案.md` |
| True-machine-style closure and C++ refactor | `Docs/Design/MoSim真机化收尾与C++化重构方案.md` |
| Agent workflow and execution gates | `Docs/Design/MoSim研发工作流与Agent任务编排规范.md` |

## 3. Legacy Document Disposition Matrix

| Legacy document | Disposition | Target / extraction rule |
|---|---|---|
| `Docs/Design/旧架构/01_系统目标与需求边界.md` | Absorb then archive | Extract stable competition scope, non-goals, and phase boundaries into `MoSim控制体系总览.md` and `Docs/Design/赛题.md` if not already covered. |
| `Docs/Design/02_总体架构与权威边界.md` | Absorb then archive | Preserve current authority split only where it matches Sunray ROS1 current lane. Move formal boundary statements into `MoSim控制体系总览.md`; keep outdated ROS2/PX4-native material as historical/future only. |
| `Docs/Design/03_核心模块设计.md` | Absorb then archive | Map RunManager, controller core, adapters, evidence manager, and UI concepts into the new control/runtime docs only if they are still active. Do not keep duplicate module taxonomy as a second entry point. |
| `Docs/Design/04_接口数据契约与时钟频率.md` | Absorb then archive | Migrate only active ABI, frame, topic, state, reference, and frequency contracts into `MoSim统一控制接口规范.md`, `MoSim单机控制器实现规范.md`, and `MoSim控制器代码生成与PX4部署规范.md`. Historical ROS2/direct-actuator surfaces remain future/reference only. |
| `Docs/Design/05_场景传感器与UE_ROS2链路.md` | Split then archive | Move active Sunray/MID360/FAST-LIO assumptions into `MoSim_FASTLIO定位闭环与规划复现基础方案.md`. Move future UE/visualization requirements to a later UE/front-end document if needed. Do not keep ROS2 as current runtime evidence. |
| `Docs/Design/06_控制规划安全与评估目标.md` | Absorb then archive | Control and tuning content belongs in control architecture, tuning, testing, and enhancement docs. Planning/formation content belongs in `MoSim规划与编队控制接口规范.md`. |
| `Docs/Design/07_验收Gate与交付物.md` | Absorb then archive | Gate definitions should move into `MoSim控制系统测试与评价规范.md` and `MoSim研发工作流与Agent任务编排规范.md`. Keep evidence-vs-claim rules explicit. |
| `Docs/Design/旧架构/08_赛题闭环实现证据矩阵.md` | Migrate to new architecture then archive | Do not bury this in architecture prose. Default target after the user migration is `Docs/Design/赛题.md` unless a standalone evidence matrix is reintroduced. It records proof status and must remain separately reviewable, but the legacy root file should not stay active. |
| `Docs/Design/09_多机编队架构与数据设计.md` | Merge then archive | Extract UAV identity, per-UAV namespace/topic isolation, result layout, formation metrics, and database boundaries into `MoSim规划与编队控制接口规范.md`. |
| `Docs/Design/旧架构/10_四旋翼模型与RuntimePlant设计.md` | Migrate to new architecture then archive | Do not delete its plant/model authority content. Default target after the user migration is `Docs/Design/MoSim真机化收尾与C++化重构方案.md` unless a standalone plant spec is reintroduced. The legacy root file should not stay active. |
| `Docs/Design/README.md` | Rewrite | Replace old `01-10` reading order with the new architecture source-of-truth order and a legacy-cache note. |

## 4. New Architecture Document Disposition

| Current architecture document | Disposition |
|---|---|
| `MoSim控制体系总览.md` | Keep as formal root. It should state the active lane, first-stage scope, and links to all formal subdocs. |
| `赛题.md` | Keep as competition/task-scope source. It should absorb durable scope material from legacy `01` when needed. |
| `MoSim统一控制接口规范.md` | Keep. It should own state/reference/output semantics and controller ABI. |
| `MoSim单机控制器实现规范.md` | Keep. It should own px4ctrl Golden Slice and controller-core behavior. |
| `MoSim控制器代码生成与PX4部署规范.md` | Keep. It should own generated C/C++ and wrapper deployment. |
| `MoSim控制器调参与参数优化规范.md` | Keep. It should own error criteria and tuning workflow. |
| `MoSim控制器管理与配置规范.md` | Keep. It should own controller profiles and config management. |
| `MoSim控制系统测试与评价规范.md` | Keep. It should own offline consistency, Gazebo/RViz evidence, metrics, and gates. |
| `MoSim控制增强与容错规范.md` | Keep as future/backlog design, clearly separated from first-stage commitments. |
| `MoSim规划与编队控制接口规范.md` | Keep. It should absorb legacy `09` and become the EGO/EGO-Swarm/formation interface authority. |
| `MoSim_FASTLIO定位闭环与规划复现基础方案.md` | Keep. It should own FAST-LIO, point cloud/map, localization replacement, and planning reproduction assumptions. |
| `MoSim真机化收尾与C++化重构方案.md` | Keep. It should own deployability, C++ refactor priority, true-machine-style sensor assumptions, and Orin NX/V6X constraints. |
| `MoSim研发工作流与Agent任务编排规范.md` | Keep. It should own agent execution gates and repeatable workflow. |
| `MoSim体系.md` | Archive or leave cache-only. It is an old research draft and must not be counted as a formal execution spec. |
| `架构.md` | Extract useful corrections, then archive or convert into a short historical explainer. It overlaps heavily with formal docs and should not remain an active source-of-truth entry. |

## 5. Required Index Updates

When executing this migration, update at least:

```text
Docs/Design/README.md
Docs/Index/doc_index.md
Docs/Index/workflow_index.md
Docs/Index/project_work_memory_index.md
Docs/Index/sunray_migration_index.md
```

Also scan for stale references:

```powershell
rg -n "Docs/Design/(0[1-9]|10)_|0[1-9]_|10_四旋翼|MoSim体系\\.md|架构/架构\\.md" Docs -g "*.md"
```

References inside historical cache files may remain if they are explicitly
historical. Active workflow and index files should not route agents to old
`01-10` documents as the primary entry.

## 6. Execution Plan

### Phase A: Prepare migration map

1. Create a path-by-path migration table from every old active document to the
   new target.
2. Mark each target as `absorbed`, `kept_independent`, `archived`, or
   `historical_reference`.
3. Identify unique content that would be lost if archived.

### Phase B: Extract unique content

Minimum extraction requirements:

1. `08` evidence matrix remains separately reviewable.
2. `09` multi-UAV identity/topic/result/database semantics are preserved.
3. `10` plant/model authority and RuntimePlant assumptions are preserved.
4. `05` active Sunray/MID360/FAST-LIO facts are preserved without reactivating
   the old ROS2 route.

### Phase C: Rewrite active entry points

1. Rewrite `Docs/Design/README.md` to point to the new architecture root.
2. Update `Docs/Index/doc_index.md`, `Docs/Index/workflow_index.md`,
   `Docs/Index/project_work_memory_index.md`, and
   `Docs/Index/sunray_migration_index.md`.
3. Keep old document links only under a `Legacy / historical` label.

### Phase D: Archive

Move legacy design documents to:

```text
Docs/Design/旧架构/
```

Suggested move list after successor docs and index rewrites exist:

```text
Docs/Design/01_系统目标与需求边界.md
Docs/Design/02_总体架构与权威边界.md
Docs/Design/03_核心模块设计.md
Docs/Design/04_接口数据契约与时钟频率.md
Docs/Design/05_场景传感器与UE_ROS2链路.md
Docs/Design/06_控制规划安全与评估目标.md
Docs/Design/07_验收Gate与交付物.md
Docs/Design/08_赛题闭环实现证据矩阵.md
Docs/Design/09_多机编队架构与数据设计.md
Docs/Design/10_四旋翼模型与RuntimePlant设计.md
```

`08` and `10` should be moved only after their successor documents exist in
`Docs/Design/架构`.

`架构/MoSim体系.md` and `架构/架构.md` should be archived or downgraded only after
the formal docs contain their current, non-duplicated decisions.

### Phase E: Validate

Run:

```powershell
rg -n "Docs/Design/(0[1-9]|10)_|0[1-9]_|10_四旋翼|MoSim体系\\.md|架构/架构\\.md" Docs/Index Docs/Workflows Docs/Design -g "*.md"
git diff --check -- Docs/Design Docs/Index Docs/Workflows
```

Acceptance:

1. active indexes route to the new architecture root;
2. no active workflow uses old `01-10` as the primary source of truth;
3. legacy references are explicitly marked historical/cache;
4. `08` evidence matrix and `10` plant/model authority are not lost;
5. `架构.md` and `MoSim体系.md` are not formal active entries.
6. no legacy `Docs/Design/01-10` file remains active outside cache.

## 7. Non-Goals

This migration does not:

1. change the current Sunray ROS1 runtime lane;
2. change px4ctrl, FAST-LIO, EGO, or Gazebo code;
3. claim any new runtime evidence;
4. delete evidence packets or result folders;
5. make ROS2/PX4-native/x500 routes current again;
6. merge evidence status into timeless architecture prose.

## 8. Recommended Next Action

After user approval, execute only Phase A-C first:

1. create successor docs or sections for `08`, `09`, and `10`;
   default successor docs are `MoSim赛题证据矩阵.md` and
   `MoSim四旋翼Plant与Sunray模型参数规范.md`;
2. rewrite `Docs/Design/README.md`;
3. update indexes;
4. run stale-reference scan.

Archive moves should be a separate, reviewable commit or checkpoint after the
new entry points are confirmed readable.
