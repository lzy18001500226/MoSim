# CoAgent Portable Core And MoSim Adapter Design

> Design draft for turning the current MoSim-local CoAgent work into a
> reusable agent-OS architecture while keeping MoSim as a host project, not as
> part of the portable core.

Status: design draft for user/PMO review, 2026-06-10 CST. This document is not
an execution workflow and does not authorize file moves, agent migration,
runtime changes, or business dispatch.

## 1. Decision Summary

The recommended architecture is:

```text
CoAgent = portable agent-OS core
MoSim = host project running on CoAgent through a MoSim adapter
```

MoSim should not be physically absorbed into `CoAgent/` as core content. MoSim
contains project facts, domain evidence, runtime gates, current thread IDs,
models, assets, results, and competition-specific priorities. Those must stay
host-local.

CoAgent should also not remain a loose set of MoSim scripts. It should become a
small reusable coordination layer with protocols, context governance, dispatch
SLOs, memory rules, capability routing, and checkers that another project can
adopt with its own adapter.

## 2. Why Not Put MoSim Inside CoAgent

MoSim-specific content includes:

```text
MWORKS/Sysplorer/Syslab models and live gates
ROS2/RViz/FAST-LIO runtime gates
UE5 scene, asset, sensor, and review gates
Sunray150 geometry/material history
A8 competition control roadmap
Models/, Config/, Scripts/, Results/
current visible thread IDs and PMO board state
domain-specific evidence bundles and screenshots
```

If these become portable CoAgent core, future projects inherit MoSim noise and
the core stops being reusable. The migration target must keep host facts out of
the core.

## 3. Desired Layering

```text
repository root
|
+-- CoAgent/
|   +-- protocol/          portable packet schemas and templates
|   +-- dispatch/          portable dispatch contracts plus host registry hooks
|   +-- context/           context pack generator and quality gate
|   +-- memory/            fenced project-memory retrieval helpers
|   +-- hooks/             native hook adapter and preflight policy
|   +-- doctor/            health/design consistency checks
|   +-- docs/
|       +-- operating/     portable workflows and role models
|       +-- architecture/  portable architecture and migration design
|       +-- research/      external/reference learning notes
|       +-- decisions/     approval and gate records
|
+-- Docs/
|   +-- Workflows/         host workflows and MoSim adapters
|   +-- Skills/            host/domain skills such as MWORKS and UE
|   +-- Index/             host route, API, memory, and capability indexes
|   +-- Design/            MoSim technical design
|
+-- Models/                MoSim model source
+-- Config/                MoSim scenarios/controllers/config
+-- Scripts/               MoSim scripts plus host-side quality checks
+-- Results/               MoSim evidence, packets, runtime leases, logs
```

This lets the current repository remain usable while establishing a clean
conceptual boundary. A later physical split could produce `coagent-core/` and
`mosim-project/`, but that should not be the first step.

## 4. Portable Core Responsibilities

CoAgent core should own only reusable agent-OS mechanics:

| Area | Portable Ownership |
|---|---|
| role model | PMO, Ops, department thread, context maintenance, review gate, disposable sub-agent |
| communication protocol | task packet, dispatch ticket, runtime lease, return packet, blocker packet |
| dispatch health | durable-start proof, readback, SLO classification, recovery packet vocabulary |
| state model | board, ledger/archive, checkpoint/event, current vs historical evidence |
| context model | entry-document boundaries, context packs, memory demotion, session migration |
| capability routing | capability cards, selected/rejected surfaces, claim ceilings |
| enforcement | schema, checker, hook, doctor, preflight |
| failover mechanics | R1/R2/R3 pattern, safe classes, reserve-capacity decision model |
| research intake | adopt/adapt/reference-only/reject pattern and evidence requirements |

Portable core should not name MoSim domain tools as required. It may define the
abstract slot:

```text
host_live_runtime_gate
host_domain_adapter
host_visible_thread_registry
host_current_board
host_evidence_checker
```

The host project fills those slots.

## 5. MoSim Adapter Responsibilities

MoSim adapter should own all project-specific policy:

| Area | MoSim Ownership |
|---|---|
| technical mainline | A8 quadrotor control, MWORKS truth, UE scene/sensor oracle, ROS2 review surface |
| domain gates | MWORKS live gate, ROS2 one-probe/runtime gates, UE source/runtime gates, Sunray/PBR freeze |
| visible routes | concrete thread IDs, names, active/archived route status, R1/R2/R3 assignments |
| current operations | PMO board, dispatch queue, waiting returns, blockers, manual decisions |
| evidence | Results packets, screenshots, metrics, logs, runtime leases, review bundles |
| host skills | MWORKS/UE/ROS/Syslab workflows and tool sequences |
| host indexes | capability index, API index, workflow index, project work memory index |
| model assets | Models, Config, UE assets, Sunray geometry/material files |

The adapter translates portable CoAgent concepts into MoSim gates. Example:

```text
portable: host_live_runtime_gate required
MoSim: MWORKS live gate with no-start attach evidence and login/license stop rules
```

## 6. Current Mixed Areas

Several files are still mixed portable-core plus MoSim-adapter content. They
should not be slimmed by deletion. They need no-loss split audits.

| Mixed Area | Current Risk | Target |
|---|---|---|
| `CoAgent/docs/operating/tooling_assets_governance.md` | portable tool policy mixed with Windows/MoSim path details | portable tool governance in CoAgent; MoSim tool adapters in `Docs/Workflows/` and `Docs/Index/` |
| `CoAgent/docs/operating/agent_orchestration.md` | task graph rules mixed with MoSim examples and legacy detail | portable orchestration core plus host examples in adapter docs |
| `CoAgent/docs/operating/session_memory_migration.md` | anti-pollution rule mixed with MoSim cache paths | portable memory promotion protocol plus MoSim cache adapter |
| `Docs/Index/capability_index.md` | useful host router but not machine checked | host router now; future capability cards/checker |
| `Docs/Workflows/new_conversation_context.md` | recovery entry can attract too many current rules | short host startup summary only |
| `Docs/Workflows/agent_task_ledger.md` | historical trace sometimes used as live board | archive/recovery only; PMO board is current state |

## 7. Target Object Model

The reusable CoAgent architecture should standardize these objects:

```text
Project
HostAdapter
RoleView
VisibleThreadRoute
TaskPacket
DispatchTicket
RuntimeLease
CheckpointEvent
ReturnPacket
BlockerPacket
CapabilityCard
SkillDescriptor
ContextPack
MemoryRecallBlock
CheckerResult
BoardSection
LedgerRecord
```

Important relationships:

```text
Project has HostAdapter
HostAdapter defines domain gates and route registry
PMO creates TaskPacket and DispatchTicket
VisibleThread writes RuntimeLease first
Department returns ReturnPacket or BlockerPacket
CheckerResult validates claim boundary
BoardSection reflects current state
LedgerRecord preserves historical trace
ContextPack starts bounded work
MemoryRecallBlock is background evidence only
```

## 8. File Placement Rules

Use these rules for future migration decisions:

| Content Type | Portable Core | Host Adapter |
|---|---|---|
| role names without project IDs | yes | optional extension |
| concrete thread IDs and titles | no | yes |
| packet schemas/templates | yes | host examples only |
| dispatch SLO vocabulary | yes | host thresholds/gates only when domain-specific |
| MWORKS/ROS2/UE rules | no | yes |
| capability-card template | yes | actual capability index/card set |
| skill format | yes | concrete domain skills |
| memory promotion protocol | yes | project cache paths and reviewed facts |
| current board state | no | yes |
| result evidence | no | yes |
| hook safety classes | yes | project path adapters |

## 9. Migration Method

Do not do a broad move. Use a no-loss migration matrix:

```text
source file:
source section:
content type:
portable or host-local:
target file:
target section:
status: exact | equivalent | host_local | obsolete | conflict | missing
evidence:
reviewer:
date:
delete/slim allowed: yes | no
```

Deletion or slimming is allowed only when:

1. the landing file exists,
2. the landing is exact or equivalent,
3. host-local content is not moved into portable core,
4. indexes are updated if routing changes,
5. tests/checkers pass if executable contracts changed.

## 10. Proposed Migration Phases

### Phase 0: Freeze Decision

Agree that:

```text
CoAgent is portable core.
MoSim is the first host adapter.
MoSim does not move wholesale into CoAgent.
No broad physical directory move happens yet.
```

### Phase 1: Define Templates

Create or finalize:

```text
workflow template
skill template
capability card template
host adapter template
context pack template
dispatch ticket and packet templates
research note template
no-loss migration row template
```

### Phase 2: Split Mixed Documents

Use the migration matrix on mixed files:

```text
agent_orchestration
tooling_assets_governance
session_memory_migration
communication_contract host examples
capability_index future machine-readable card set
```

### Phase 3: Add Checkers

Add deterministic gates for:

```text
capability card required fields
workflow required sections
skill required sections
host adapter required fields
memory recall fenced/background-only rule
dispatch ticket + runtime lease consistency
```

### Phase 4: Slim Entry Documents

Only after landing and checks:

```text
AGENTS.md -> compact hard boundaries
new_conversation_context.md -> short host recovery
workflow_index.md -> route table only
project_work_memory_index.md -> recovery routing only
```

## 11. Minimal Host Adapter Contract

Any project using CoAgent should provide:

```text
host name
workspace root
entry document path
current board path
visible thread registry path
domain workflow directory
host skill directory
capability index or cards
result packet root
runtime lease root
project memory index/cache path
notification policy
forbidden live actions
default evidence classes
```

For MoSim, the current bindings are approximately:

```text
host name: MoSim
workspace root: C:\Users\HP\Desktop\MoSim
entry document path: AGENTS.md
current board path: Docs/Workflows/mainline_operations_board.md
visible thread registry path: CoAgent/dispatch/department_threads.json
domain workflow directory: Docs/Workflows/
host skill directory: Docs/Skills/
capability index: Docs/Index/capability_index.md
result packet root: Results/agent_packets/
runtime lease root: Results/runtime_leases/
project memory index: Docs/Index/project_work_memory_index.md
```

These bindings are examples for MoSim only; they are not portable defaults.

## 12. Risks

| Risk | Mitigation |
|---|---|
| over-abstracting before MoSim works | keep MoSim adapter first, promote only repeated patterns |
| losing rules during slimming | require no-loss migration rows |
| turning indexes into authority | keep permission in PMO/user, task packet, workflow, checker |
| global memory contaminating host facts | project memory is verified against host files before use |
| CoAgent becoming another large project inside MoSim | core owns mechanics only; host owns facts and evidence |
| physical moves breaking paths | defer physical split until logical split is audited |

## 13. Open Questions

1. Should `CoAgent/docs/operating/tooling_assets_governance.md` be split into
   `tooling_governance_core.md` plus MoSim adapter references, or left as a
   conservative mixed landing until more checkers exist?
2. Should capability cards become the first machine-readable migration target,
   or should workflow/skill templates come first?
3. Should MoSim host adapter have a single manifest file, such as
   `Docs/Workflows/mosim_host_adapter.yaml`, or continue using current docs and
   indexes?
4. Should project-owned memory use the existing `CoAgent/memory` helper only,
   or add a host-specific memory card format under `Docs/Index/`?
5. What is the smallest checker set that prevents future documentation drift
   without slowing PMO dispatch?

## 14. Recommended Next Step

Review this design first. If accepted, the first implementation task should be
small and reversible:

```text
create host-adapter manifest draft
create workflow/skill/capability-card templates
write no-loss migration matrix for one mixed document
run docs/checker review
```

Do not start by moving directories or rewriting `AGENTS.md`.
