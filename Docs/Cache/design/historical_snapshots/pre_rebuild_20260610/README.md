# Pre-Rebuild Design Cache, 2026-06-10

This folder is the holding area for design documents that belong to the
pre-rebuild MoSim design narrative.

The rebuild goal is not to delete prior design work. The goal is to separate:

1. current system design source documents;
2. historical or partially superseded design inputs;
3. implementation-status notes and evidence claims;
4. externally generated reference drafts such as `.docx` review material.

## Cache Rule

A document may move here only after a rebuild audit records:

- its original path;
- the reason it is being cached;
- the current design document that preserves or restates its still-valid
  semantics;
- any known stale claims, evidence claims, or implementation-status statements
  that must not be promoted into the new system design.

## Current Rebuild Boundary

The new `Docs/Design/` root should describe what MoSim is intended to be before
it describes how the current repo happens to implement it.

The target system is:

```text
MWORKS / Sysplorer / Sysblock / Syslab
  -> dynamics, controller, truth, experiments, metrics, report evidence

UE5 / MoSimSceneLibrary
  -> scene rendering, UAV visual, camera, collision, sensor oracle, video

ROS2 / RViz2 / FAST-LIO / planner stack
  -> robotics transport, localization/map/planner review, setpoint traces

Results / evidence bundle
  -> reproducible run manifest, configuration snapshot, logs, metrics, figures,
     screenshots, videos, and acceptance/blocker records
```

Current implementation status and packet history should remain in workflows,
progress files, results, audits, or ADRs. New design source documents should
avoid presenting unimplemented gates as completed facts.

## Cached Inputs

The first rebuild pass created the new design source set in `Docs/Design/` and
then moved the following pre-rebuild inputs here:

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

The active root design entrypoint is now `Docs/Design/README.md`. The rebuild
audit is cached at `Docs/Cache/design/rebuild_audits/design_rebuild_audit_20260610.md`.
