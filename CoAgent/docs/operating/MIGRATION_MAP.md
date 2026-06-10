# CoAgent Operating Migration Map

Status: active migration map, 2026-06-10 CST.

The migration boundary is `CoAgent/`. Project application workflows remain in
the host project unless they define reusable agent-OS behavior.

## No-Loss Landing Status

The files below now exist under `CoAgent/docs/operating/`, but they are
conservative no-loss landing copies seeded from MoSim workflows. They are not
yet fully portable canonical rewrites. Keep the old `Docs/Workflows/*`
compatibility paths valid until each file has a deletion-to-landing audit row.

| Old MoSim Path | CoAgent Landing Path | Treatment |
|---|---|---|
| `Docs/Workflows/org_operating_model.md` | `CoAgent/docs/operating/org_operating_model.md` | Conservative landing copy. Still mixed portable-core + MoSim adapter. |
| `Docs/Workflows/coagent_ops_patrol_workflow.md` | `CoAgent/docs/operating/coagent_ops_patrol_workflow.md` | Conservative landing copy. Still includes MoSim owner/thread ids, board paths, MWORKS, ROS2, and UE adapter rules. |
| `Docs/Workflows/coagent_meta_maintenance.md` | `CoAgent/docs/operating/coagent_meta_maintenance.md` | Conservative landing copy. Still includes dated MoSim incident details. |
| `Docs/Workflows/agent_orchestration.md` | `CoAgent/docs/operating/agent_orchestration.md` | Conservative landing copy. Still includes MoSim examples, local paths, and host references. |
| `Docs/Workflows/tooling_assets_governance.md` | `CoAgent/docs/operating/tooling_assets_governance.md` | Conservative landing copy. Still includes host-local Windows paths and MoSim tool adapters. |
| `Docs/Workflows/session_memory_migration.md` | `CoAgent/docs/operating/session_memory_migration.md` | Conservative landing copy. Still includes MoSim cache paths and promotion targets. |
| `Docs/Workflows/coagent_ops_efficiency_audit_20260609.md` | `CoAgent/docs/operating/audits/coagent_ops_efficiency_audit_20260609.md` | Audit/reference only, not executable policy. |
| Current portability review | `CoAgent/docs/operating/PORTABILITY_REVIEW_20260610.md` | Review record for the CoAgent portable boundary, durable-start dispatch rule, and default no-thread-click heartbeat decision. |
| MoSim visible dispatch adapter | `Docs/Workflows/mosim_visible_dispatch_adapter.md` | Host adapter for MWORKS/ROS2/UE/Sunray-specific dispatch gates. The former contract domain-gate block has an audited exact landing here; future slimming still needs audit rows. |

## No-Loss Migration Gate

The migration order is mandatory:

```text
1. create or verify the landing file
2. copy or restate the source block there
3. record deletion-to-landing status
4. update indexes and startup pointers
5. only then slim the old entry/source text
```

For any future large slimming, record each removed block with:

```text
source block:
landing file and section:
status: exact | equivalent | intentionally_host_local | obsolete_superseded | missing
reviewer:
date:
```

If the landing file is missing, the status is `missing`, or stop conditions are
weakened, the editor must restore the source block or patch the landing before
reporting completion.

## Already In CoAgent

| Path | Role |
|---|---|
| `CoAgent/dispatch/communication_contract.md` | Packet, dispatch, semantic boundary, and SLO contract. |
| `CoAgent/dispatch/department_threads.json` | Host-project visible-route registry. Portable schema; concrete ids are host-local. |
| `CoAgent/protocol/` | Packet schemas, templates, and protocol vocabulary. |
| `CoAgent/runtime/`, `task_health/`, `status_export/`, `review_queue/`, `result_router/` | Reusable local runtime/status/review machinery. |
| `CoAgent/hooks/`, `automation/`, `doctor/`, `transport/` | Reusable guardrail, automation, health-check, and transport boundaries. |

## Host-Project Local By Design

These are not migrated into CoAgent as generic operating policy:

| MoSim Path | Reason |
|---|---|
| `Docs/Workflows/mainline_operations_board.md` | Current MoSim PMO board, not portable policy. |
| `Docs/Workflows/agent_task_ledger.md` | MoSim historical/recovery ledger. May be archived locally. |
| `PROGRESS.md` | MoSim current project progress. |
| `Docs/Design/` | MoSim product/technical architecture. |
| `Docs/Skills/Mworks/`, `Docs/Skills/Unreal/`, `Docs/Skills/Sysplorer/` | Host domain execution skills. |
| `Models/`, `UE5/`, `Config/`, `Scripts/`, `References/`, `Results/` | MoSim application assets, tooling, and evidence. |
| `Docs/Workflows/mosim_visible_dispatch_adapter.md` | MoSim-specific visible-department domain gate adapter. |

## Cleanup Candidates

These should be cleaned only after review:

```text
CoAgent/**/__pycache__/
CoAgent/**/*.pyc
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/
CoAgent/work_queue/audits/* dry-run outputs
CoAgent/docs/status/* obsolete one-off status snapshots
CoAgent/docs/research/* if superseded by current learning index
```

Do not delete `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/` until any still-useful
architecture conclusions are either already represented in `CoAgent/docs/` or
explicitly marked obsolete.

## Next Split Targets

These files are intentionally preserved as no-loss landing copies but still
need a second pass before `CoAgent/docs/operating/` is cleanly portable:

| Path | Keep Portable | Move/Leave As Host Adapter |
|---|---|---|
| `CoAgent/docs/operating/agent_orchestration.md` | task graph, surface selection, checkpoint, sub-agent, long-running-task rules | concrete MoSim thread ids, MWORKS/ROS2/UE evidence examples, local reference-project paths |
| `CoAgent/docs/operating/coagent_meta_maintenance.md` | recurring meta-maintenance cadence, registry hygiene checks, stale-rule prevention | dated MoSim incidents, deleted WeChat routes, MWORKS-specific patrol incidents |
| `CoAgent/docs/operating/tooling_assets_governance.md` | hook/tool/MCP governance principles and entry-document slimming policy | host-local Windows paths, MWORKS/UE/ROS tool adapters, machine-specific Codex config paths |
| `CoAgent/docs/operating/coagent_ops_patrol_workflow.md` | patrol order, SLO, durable-start liveness, bounded dispatch, recovery state machine | MoSim board sections, exact visible thread ids, MWORKS window classifications, MoSim email wording |
| `CoAgent/docs/operating/org_operating_model.md` | reusable roles and ownership boundaries | MoSim current route names, route ids, department capacity assignments |
| `CoAgent/docs/operating/session_memory_migration.md` | cache-first anti-pollution workflow | MoSim cache paths and project-specific promotion targets |

The default visible-thread liveness policy is now durable-start first. The old
thread-row click refresh behavior must remain an incident-scoped exception
unless PMO/user explicitly reauthorizes it for a specific recovery task.

## Audited Split Rows

| Date | Source Block | Landing File And Section | Status | Reviewer |
|---|---|---|---|---|
| 2026-06-10 | `CoAgent/dispatch/communication_contract.md` old `Domain Dispatch Gates` MoSim ROS2/UE/Sunray/MWORKS sections | `Docs/Workflows/mosim_visible_dispatch_adapter.md#4-domain-gates` | exact | Codex current turn |

Notes:

- `CoAgent/dispatch/communication_contract.md` now keeps only the portable rule
  that a host-project domain gate must be supplied and named in the task
  packet.
- MoSim-specific MWORKS/Sysplorer/Syslab, ROS2/RViz2/FAST-LIO, UE, Sunray150,
  and R2/R3 failover wording lives in the MoSim adapter.
- The MWORKS live-gate checker command remains referenced from the portable
  contract as an example of a host-specific machine gate.
