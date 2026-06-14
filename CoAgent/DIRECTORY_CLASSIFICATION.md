# CoAgent Directory Classification

> Review inventory for consolidating `CoAgent/` by merge, not deletion.

Status: review draft, 2026-06-10 CST.

This file is not an execution workflow. It does not authorize moving,
renaming, deleting, archiving, dispatching agents, changing Codex App
automation, or changing MoSim runtime behavior.

## 1. Decision

The consolidation rule is:

```text
do not delete first
classify first
merge by no-loss audit
archive only after references and replacements are proven
```

`CoAgent/` should become a portable agent-OS core plus clearly marked support,
runtime-experimental, host-adapter, and historical areas. MoSim remains the
host project. MoSim domain facts, thread ids, Results evidence, Models, and
runtime gates must not be absorbed into the portable core.

## 2. Classification Fields

Each directory is classified with these fields:

| Field | Meaning |
|---|---|
| Runtime authority | Whether the directory is current execution authority, support material, legacy reference, or archive candidate. |
| Portable status | Whether the content is portable, mixed, host-local, or historical. |
| Merge target | Conceptual future home if consolidation is approved. |
| Delete allowed | Always `false` in this review draft. |
| Next review | What must happen before any physical move or slimming. |

Runtime authority values:

```text
active
support
legacy
archive_candidate
experimental
```

Portable status values:

```text
portable
mixed
host_local
historical
unknown_until_audit
```

## 3. Current Directory Classification

| Directory | Current role | Runtime authority | Portable status | Merge target | Delete allowed | Next review |
|---|---|---|---|---|---|---|
| `automation/` | Project-owned automation definitions, guardrails, dry-run/staged-start helpers. Not the Codex App wall-clock scheduler. | support | mixed | `support/automation_policy` or `runtime_experimental/automation` | false | Audit references to `automation_runner.py`, guardrails, tests, and compare with user-level `.codex/automations`. |
| `blocker_packet/` | Early blocker packet helper. | legacy | portable | `protocol/` or `dispatch/` | false | Compare with current result/blocker schemas and checker behavior. |
| `bootstrap/` | Task bootstrap and context/handoff support. | support | mixed | `context/` plus `dispatch/` | false | Audit whether `task_bootstrap.py` is still used by current packet or context-pack flows. |
| `context/` | Context pack generator and quality gate. | active | portable | `core/context` | false | Keep; align future context packs with memory and host adapter boundaries. |
| `devops/` | Git split, handoff, batch-plan helpers. | support | mixed | `support/devops` or host adapter tooling | false | Separate portable Git handoff concepts from MoSim-specific Git cleanup rules. |
| `dispatch/` | Communication contract, visible route registry, transport helpers, session repair helpers. | active | mixed | `core/dispatch` plus host registry adapter | false | Split portable contract from MoSim concrete thread ids over time. |
| `docs/` | Architecture, operating, research, decisions, status notes. | active | mixed | `core/docs` plus host adapters where needed | false | Use no-loss section-level migration map before slimming old architecture notes. |
| `doctor/` | Health, protocol, design, goal-alignment checks. | active | portable | `core/doctor` | false | Keep; add directory-classification checker only after this review is accepted. |
| `evidence/` | Evidence manifest and refresh command helpers. | support | portable | `core/evidence` or `protocol/evidence` | false | Compare with current Results packet/evidence manifest conventions. |
| `gateway/` | Old Weixin gateway/notification work. | archive_candidate | historical | `archive/gateway` after notification audit | false | Preserve until current email-only notification boundary and deleted WeChat route history are fully referenced elsewhere. |
| `hooks/` | Native hook adapter and preflight safety policy. | active | mixed | `core/hooks` plus host path adapters | false | Keep; separate portable safety classes from MoSim/Windows path assumptions. |
| `knowledge/` | Knowledge source indexer and source list. | support | mixed | `memory/` or `docs/research` support | false | Decide whether knowledge index remains a runtime helper or becomes reviewed research inventory. |
| `learning/` | Learning index and prior audit notes. | support | mixed | `docs/research` with preserved audit history | false | Preserve source provenance and adopt/adapt/reference-only/reject decisions. |
| `memory/` | Fenced memory recall helper and memory policy. | active | portable | `core/memory` | false | Keep; ensure global Codex memory is only a recall hint, not project fact authority. |
| `protocol/` | Schemas, packet templates, vocabulary, conversation protocol. | active | portable | `core/protocol` | false | Keep as contract source; align YAML/JSON templates and checkers before moving anything. |
| `result_router/` | Result import/routing and old notification packet generation. | legacy | mixed | `runtime_experimental/result_router` or `dispatch/` | false | Determine whether current Results packet checkers supersede it. |
| `review_package/` | Human review package helper. | support | portable | `core/review` or `protocol/review` | false | Merge with review packet templates only after tests and references are mapped. |
| `review_queue/` | Review queue helper and closeout workflow support. | support | portable | `core/review` or `runtime_experimental/review_queue` | false | Preserve closeout semantics; avoid turning review queue into product authority. |
| `runtime/` | Early local task runtime and queue model. | experimental | portable | `runtime_experimental/runtime` | false | Keep gated by `CoAgent/STATUS.md`; do not mark as active visible-thread transport without approval. |
| `skills/` | Generic CoAgent skills such as window capture/action separation. | active | portable | `core/skills` | false | Keep distinct from host `Docs/Skills/`; add capability-index cards as needed. |
| `status_export/` | Status export helper. | support | portable | `doctor/` or `support/status_export` | false | Audit whether PMO board export or doctor reports should own this. |
| `task_health/` | Task health and continuation helper. | support | portable | `doctor/` or `runtime_experimental/task_health` | false | Compare with dispatch SLO checker and durable-start workflow. |
| `tasks/` | Historical architecture task specs and design backlog. | archive_candidate | historical | `archive/tasks` after no-loss index | false | Do not delete; create index and preserve useful design records before any move. |
| `tests/` | CoAgent tests. | active | portable | `core/tests` | false | Keep; tests protect future merges. |
| `transport/` | Old transport adapters and Codex exec bridge. | legacy | mixed | `runtime_experimental/transport` | false | Compare with Codex App native thread tools and visible-thread dispatch model. |
| `validators/` | Minimal validator placeholder. | archive_candidate | unknown_until_audit | `doctor/` or `archive/legacy_helpers` | false | Prove unused or merge into doctor before archiving. |
| `work_queue/` | Early queue helpers and dry-run audits. | legacy | historical | `runtime_experimental/work_queue` or `archive/work_queue` | false | Preserve audits; compare with current dispatch ticket and PMO board model. |

## 4. Automation Boundary

There are two separate automation layers:

```text
C:\Users\HP\.codex\automations
  real Codex App scheduler storage
  user-profile state
  not portable CoAgent source

CoAgent/automation
  project-owned automation definition, guardrail, dry-run, and staged-start layer
  not the active wall-clock scheduler by itself
```

Therefore `CoAgent/automation` must not be deleted merely because current
wall-clock automations live in `.codex/automations`. It should be merged only
after the useful definition, guardrail, and reviewed-start concepts are either
preserved in portable CoAgent or explicitly superseded.

## 5. No-Loss Merge Procedure

Before moving or slimming any directory, write a migration row:

```text
source path:
source file or section:
content type:
portable or host-local:
target path:
target section:
status: exact | equivalent | host_local | obsolete | conflict | missing
evidence:
tests/checkers:
reviewer:
date:
delete/slim allowed: yes | no
```

Physical move or deletion requires all of these:

1. Landing file or landing directory exists.
2. Landing content is exact or equivalent.
3. Host-local MoSim facts are not moved into portable core.
4. References are updated or intentionally preserved.
5. Tests/checkers pass for executable contracts.
6. User or PMO explicitly approves the move.

## 6. Reference Audit Commands

Use targeted reference audits. Do not broad-delete by directory name.

```powershell
rg -n "CoAgent/<dir>|CoAgent\\<dir>" AGENTS.md Docs CoAgent Scripts Results
rg --files CoAgent/<dir>
python -m pytest CoAgent/tests/<related_test>.py
git diff --check -- <touched paths>
```

For directories with runtime or automation meaning, also audit:

```powershell
rg -n "<dir>|<helper_name>" CoAgent Docs Scripts Results
```

## 7. Suggested Merge Batches

Batch 1: clarify active portable core without moving files.

```text
protocol/
dispatch/
context/
memory/
hooks/
doctor/
skills/
tests/
```

Batch 2: classify support helpers and decide whether they remain support or
merge into core.

```text
bootstrap/
knowledge/
learning/
devops/
evidence/
status_export/
task_health/
review_package/
review_queue/
```

Batch 3: isolate legacy or experimental runtime pieces.

```text
runtime/
transport/
result_router/
automation/
work_queue/
```

Batch 4: archive candidates only after no-loss audit.

```text
gateway/
tasks/
validators/
blocker_packet/
```

## 8. Open Decisions

1. Whether the future physical shape uses `CoAgent/core/*` or keeps current
   top-level names with classification docs.
2. Whether `dispatch/department_threads.json` remains in portable CoAgent with
   host-local content, or moves to a host adapter path while `dispatch/` keeps
   only schema and contract.
3. Whether `automation/` becomes an approved scheduler adapter later, or stays
   a definition and guardrail layer around Codex App automation.
4. Whether `learning/` is merged into `docs/research/` or remains a separate
   provenance/audit store.
5. How much of `tasks/COAGENT-ARCH-LONGRUN-01/` is still useful design
   material versus historical task evidence.

## 9. Non-Goals

This classification does not:

1. delete files,
2. move files,
3. rename directories,
4. modify Codex App private state,
5. change active automations,
6. change MoSim MWORKS/ROS2/UE runtime behavior,
7. grant CoAgentOps product authority,
8. make legacy transport or runtime code current authority.
