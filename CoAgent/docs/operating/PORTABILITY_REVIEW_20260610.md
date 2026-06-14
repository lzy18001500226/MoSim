# CoAgent Operating Portability Review 20260610

Status: active review record, 2026-06-10 CST.

## Goal

Make `CoAgent/` the migratable agent-OS boundary while keeping MoSim
application-specific workflow, board, evidence, and domain rules in the host
project. Do not slim or delete semantics before they are copied, mapped, or
explicitly marked host-local.

Current scoped goal:

```text
CoAgent/docs/operating/ contains reusable agent-OS policy.
Docs/Workflows/ contains MoSim compatibility adapters and host-project boards.
CoAgent/dispatch/communication_contract.md contains portable packet and SLO
contract fields, with host examples allowed where clearly marked as examples.
```

## Subagent Plan

```yaml
subagent_plan: used
subagent_plan_reason: >
  The user explicitly requested goal/sub-agent planning and the main risk is
  silent semantic loss from a prior large slimming pass. A read-only explorer
  was useful as an independent deletion/landing audit while the main thread
  repaired missing landing files and source-of-truth pointers.
subagents_used:
  - 019ead8c-f748-7411-b54f-8b10b31dcdd3
  - 019eb065-b9b3-7f21-ba95-975318c9daf4
  - 019eb066-0095-7191-aecf-85cded33f193
verification_gates:
  - targeted text searches for stale click-refresh rules
  - deletion-to-landing audit table for removed or weakened semantics
  - protocol/template consistency checks
  - CoAgent doc/protocol smoke tests
manual_review_or_blocker_triggers:
  - any proposal to delete old compatibility paths
  - any runtime, automation, restart, or visible-thread lifecycle change
  - any migration of MoSim domain evidence rules into portable CoAgent policy
```

## Decisions Captured

1. `CoAgent/` is the portable boundary.
2. MoSim application assets and evidence stay host-local: `Models/`, `UE5/`,
   `Config/`, `References/`, `Results/`, `Docs/Design/`, and domain skills.
3. `AGENTS.md` stays compact: hard boundaries plus pointers, not full
   executable workflows.
4. Non-trivial visible-department tasks must plan local goal, critical path,
   parallel slices, verification gates, and `subagent_plan`.
5. Non-trivial visible-department tasks must also declare a
   `durable_start_requirement`; the target thread's first execution step is to
   write that durable artifact unless the task is an exact no-write probe.
6. The 10-minute heartbeat must not click through every visible thread as the
   default liveness check.
7. CoAgentOps may inspect or capture the Codex App main shell/list area to
   detect pending approval/review/provider indicators such as `待批准`, then
   notify by sparse Chinese email or PMO notice. It must not click approval,
   review, send, restart, login, save, archive, delete, pin, overflow, or
   composer controls.
8. Thread-row refresh clicking is an incident-scoped exception only, not the
   routine heartbeat mechanism.
9. The six `CoAgent/docs/operating/*.md` workflow files created on
   2026-06-10 started as conservative no-loss landing copies. As of this
   second-pass audit, `org_operating_model.md`,
   `coagent_ops_patrol_workflow.md`, `agent_orchestration.md`,
   `coagent_meta_maintenance.md`, `tooling_assets_governance.md`, and
   `session_memory_migration.md` are split-audited portable cores.
10. `Docs/Workflows/mosim_visible_dispatch_adapter.md` is the MoSim host
    adapter for MWORKS/ROS2/UE/Sunray-specific dispatch gates. The former
    MoSim-specific domain gate text from `CoAgent/dispatch/communication_contract.md`
    has been audited as an exact landing in that adapter; the portable contract
    now keeps only the host-adapter rule and checker pointer.
11. `CoAgent/docs/operating/context_documentation_governance.md` was created
    as the missing portable core for context authority, document responsibility,
    documentation-secretary scope, capability routing, project-owned memory, and
    no-loss documentation migration.

## Portable Core Vs MoSim Adapter

| Semantic Area | Portable CoAgent Core | MoSim Adapter / Host Local |
|---|---|---|
| Task lifecycle | goal, task graph, packet, checkpoint/result/blocker, review/import | competition priorities, current PMO board rows, accepted engineering gates |
| Dispatch SLO | dispatch ticket, 5-minute meaningful-progress surface window, durable-start requirement | concrete `Results/agent_packets/` paths and MoSim active ticket rows |
| Failover | R2 safe static/diagnostic/checker/review failover, R3 reserve rule | MWORKS/ROS2/UE R1/R2/R3 thread ids and live-resource exclusions |
| Liveness | native read/send, expected packet, durable-start artifact, approval/provider/context classification | Codex App main-shell observation and MoSim-specific pending approval email wording |
| UI action | no default transcript clicking; incident-scoped observation-only exception | MWORKS activation/window patrol and any approved host GUI evidence path |
| Documentation memory | cache-first promotion before old chat becomes project truth | MoSim cache folders, `PROGRESS.md`, `agent_task_ledger.md`, board history |
| Context governance | authority ladder, document responsibilities, documentation-secretary boundary, no-loss migration rule | MoSim startup context, project memory index, concrete route registry |
| Organization model | shared core, role views, conflict owner, task packet scope, capability router, reusable role catalogue | current MoSim route IDs, deleted route history, R1/R2/R3 concrete assignments |

## Semantics Preserved

The previous click-refresh proposal is not silently deleted. It is downgraded
from default heartbeat policy to an incident-scoped exception because the user
confirmed that routine clicking is too complex and should not be the primary
dead-thread detector. The new default evidence ladder is:

```text
task dispatch
  -> durable-start artifact expected within 5 minutes
  -> native read/send and expected packet checks
  -> approval/review/provider/context classification
  -> main-shell pending indicator observation and sparse email if needed
  -> recovery/blocker if no meaningful progress is found
```

Independent read-only deletion audit result:

| Source Area | Current Landing | Status | Action |
|---|---|---|---|
| Domain dispatch gates overall | `CoAgent/dispatch/communication_contract.md#domain-dispatch-gates`, `Docs/Workflows/mosim_visible_dispatch_adapter.md#4-domain-gates` | split-exact | Portable contract keeps host-adapter requirement; MoSim specifics live in adapter. |
| R2/R3 failover rules | `CoAgent/dispatch/communication_contract.md`, `Docs/Workflows/coagent_ops_patrol_workflow.md` | exact | No semantic loss found. |
| MWORKS window/license/activation rules | `Docs/Workflows/mosim_visible_dispatch_adapter.md#4-domain-gates`, `Docs/Workflows/coagent_ops_patrol_workflow.md`, `Docs/Skills/Mworks/*` | exact | MoSim-specific rule has moved out of portable contract. |
| ROS2/RViz/FAST-LIO gates | `Docs/Workflows/mosim_visible_dispatch_adapter.md#4-domain-gates`, `Docs/Workflows/ros2_runtime_setup.md` | exact | MoSim-specific rule has moved out of portable contract. |
| UE gates | `Docs/Workflows/mosim_visible_dispatch_adapter.md#4-domain-gates`, `Docs/Workflows/unreal_renderer.md` | exact | MoSim-specific rule has moved out of portable contract. |
| Sunray/PBR gates and freeze | `Docs/Workflows/mosim_visible_dispatch_adapter.md#4-domain-gates` | exact | MoSim-specific rule has moved out of portable contract. |
| Dispatch SLO and durable-start rule | `CoAgent/dispatch/communication_contract.md`, `Docs/Workflows/coagent_ops_patrol_workflow.md` | strengthened | Keep strengthened gate. |
| Detailed thread-row click/refresh sweep | `Docs/Workflows/coagent_ops_patrol_workflow.md#53-incident-scoped-thread-row-refresh-appendix` | restored as recovery-only | Restored the 0.5s dwell, title-region-only click, blank-view skip/retry-next-pass, and forbidden-control details without making it routine heartbeat. |
| MoSim visible dispatch adapter | `Docs/Workflows/mosim_visible_dispatch_adapter.md` | audited exact landing | Adapter is now the host landing for the former contract domain-gate text. |
| Portable CoAgentOps patrol workflow | `CoAgent/docs/operating/coagent_ops_patrol_workflow.md`; MoSim long-form adapter remains `Docs/Workflows/coagent_ops_patrol_workflow.md` | split-audited | Portable file now keeps reusable SLO, liveness, bounded dispatch, recovery, failover, and packet/checker mechanics. |
| Portable organization model | `CoAgent/docs/operating/org_operating_model.md`; MoSim long-form adapter remains `Docs/Workflows/org_operating_model.md` | split-audited | Portable file now keeps shared core, role views, registry requirements, task flow, delegation, gates, and completion criteria. |
| Portable agent orchestration | `CoAgent/docs/operating/agent_orchestration.md`; MoSim long-form adapter remains `Docs/Workflows/agent_orchestration.md` | split-audited | Portable file now keeps task graph, queue, durable-start, packet, delegation, checkpoint, review, evidence, resume, and Git ownership rules. |
| Portable meta-maintenance | `CoAgent/docs/operating/coagent_meta_maintenance.md`; MoSim long-form adapter remains `Docs/Workflows/coagent_meta_maintenance.md` | split-audited | Portable file now keeps registry hygiene, capability inventory, automation records, incident follow-up, and stale-rule prevention. |
| Portable tooling governance | `CoAgent/docs/operating/tooling_assets_governance.md`; MoSim long-form adapter remains `Docs/Workflows/tooling_assets_governance.md` | split-audited | Portable file now keeps native-surface policy, capability router, tool intake, runtime boundaries, context hygiene, and entry-document slimming. |
| Portable session-memory migration | `CoAgent/docs/operating/session_memory_migration.md`; MoSim adapter remains `Docs/Workflows/session_memory_migration.md` | split-audited | Portable file now keeps three-round cache-first promotion and anti-pollution rules. |
| Portable context/documentation governance | `CoAgent/docs/operating/context_documentation_governance.md`; MoSim startup/memory adapters remain in `Docs/Workflows/` and `Docs/Index/` | created and audited | Missing indexed operating document has been added as portable core. |

Second-pass no-loss audit file:

```text
CoAgent/docs/operating/audits/no_loss_split_audit_20260610.md
```

## Cleanup Candidates

These are candidates only; do not delete without a follow-up review:

```text
CoAgent/docs/operating/audits/
  - keep current audit rows; later archive only after another review.

CoAgent/docs/research/context_documentation_governance_research_20260610.md
  - research note now partially promoted to operating policy; keep as source
    record unless a later review marks it superseded.

CoAgent/docs/status/*
  - one-off status snapshots may be pruned only after current indexes and
    migration records no longer depend on them.
```

## Verification Plan

Run targeted checks after edits:

```powershell
python -m pytest CoAgent/tests/test_design_surface_docs.py CoAgent/tests/test_protocol_vocabulary.py -q
python Scripts/quality/check_dispatch_ticket_slo.py CoAgent/protocol/templates/visible_thread_dispatch_ticket.json
python Scripts/quality/check_agent_task_native_surface_gate.py CoAgent/protocol/templates/visible_thread_dispatch_packet.json --strict
```

Do not run Git staging/commit operations in this pass because the worktree has
pre-existing staged external reference files unrelated to this documentation
task.
