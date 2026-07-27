# CoAgent Directory Merge Design

> Design draft for consolidating the current `CoAgent/` tree without deleting
> historical or referenced material.

Status: design draft for user/PMO review, 2026-06-10 CST. This document does
not authorize deletion, movement, renaming, or runtime changes.

## 1. Problem

The current `CoAgent/` tree contains useful portable core pieces, host-project
adapters, early runtime experiments, historical gateway work, task evidence
helpers, and design records. The directory count is high, and some names imply
active runtime authority even when the current operational path has moved to
Codex App native features or MoSim host workflows.

The goal is not to delete. The goal is to merge and classify so each directory
has a clear role:

```text
current portable core
host adapter / MoSim binding
legacy runtime reference
historical evidence
archive candidate
future implementation candidate
```

## 2. Automation Boundary

There are two different automation layers.

### 2.1 Codex App automation

Actual Codex App automations live outside the project:

```text
C:\Users\HP\.codex\automations\<automation_id>\automation.toml
```

Observed fields include:

```text
id
kind
name
prompt
status
rrule
target_thread_id
created_at
updated_at
```

This layer is the real wall-clock wake-up path. It belongs to the Codex App
user profile, not to portable CoAgent. CoAgent may document expected prompts or
write audit packets, but it should not pretend this directory is project-owned
runtime state.

### 2.2 `CoAgent/automation`

`CoAgent/automation` is project-owned design/runtime support:

```text
automation_tasks.json
automation_runner.py
guardrails.py
worker_policy.json
SCHEDULED_AUTOMATION_DECISION.md
README.md
```

Its own README says it does not replace Codex App automation UI, does not call
Codex App automation APIs, and does not schedule wall-clock wakeups. It is a
durable definition, guardrail, dry-run planning, and reviewed staged-start
layer.

Therefore it should be classified as:

```text
portable automation definition and guardrail reference
not the active Codex App scheduler
```

Do not delete it. Instead, merge its surviving pieces into a clearer
`CoAgent/core automation policy` concept later, after reference audits.

## 3. Directory Classification Draft

This table is a first-pass design classification. It is not a deletion list.

| Directory | Current Role | Proposed Class | Merge Direction |
|---|---|---|---|
| `dispatch/` | visible-thread registry, communication contract, dispatch helpers | current portable core plus host registry | keep; split host IDs from portable contract over time |
| `protocol/` | packet schemas and templates | current portable core | keep; make schemas/templates the contract source |
| `context/` | context pack generator and quality gate | current portable core | keep; align with memory policy and host adapter |
| `memory/` | fenced project memory recall helper | current portable core | keep; clarify background-only authority |
| `hooks/` | native hook adapter and preflight | current portable core | keep; separate portable safety classes from host paths |
| `doctor/` | design and health checks | current portable core | keep; add directory classification checker later |
| `docs/` | architecture, operating, research, decisions | current design/control plane | keep; split mixed portable/host docs by no-loss audit |
| `skills/` | generic CoAgent skills | current portable core candidate | keep; avoid duplicating host `Docs/Skills/` |
| `tests/` | CoAgent tests | current portable core | keep; use to protect future merges |
| `runtime/` | early task runtime and queue model | legacy/future implementation candidate | keep for now; audit before making active |
| `transport/` | old transport adapters / dispatch bridge | legacy/future implementation candidate | keep for now; compare to Codex App native thread tools |
| `result_router/` | result import/routing | legacy/future implementation candidate | keep; decide whether packet checker supersedes it |
| `bootstrap/` | context/bootstrap/handoff support | support core or legacy helper | merge useful parts into context/dispatch docs later |
| `knowledge/` | knowledge index helpers | support core | keep if memory uses it; otherwise merge into memory |
| `learning/` | source-audit/learning records and tooling | research/support | merge with `docs/research` conceptually; preserve files |
| `devops/` | Git split and handoff helpers | host support/tooling | keep; classify as host/devops adapter unless generalized |
| `tasks/` | historical task specs/backlog | archive/history | keep as design/task archive; not current runtime authority |
| `automation/` | project automation definitions, guardrails, dry-run runner | legacy/future automation policy | keep; do not confuse with `.codex/automations` |
| `gateway/` | old gateway/notification work | historical or adapter reference | archive candidate; preserve until email/current notification boundary is audited |
| `work_queue/` | early queue helpers | legacy runtime | archive or merge into runtime after audit |
| `review_queue/` | review queue helpers | legacy runtime | archive or merge into review model after audit |
| `review_package/` | review package helpers | support or legacy | merge into evidence/review protocol if still useful |
| `blocker_packet/` | blocker packet helpers | protocol legacy | merge into `protocol/` or `dispatch/` after audit |
| `task_health/` | task health helpers | legacy/support | compare with dispatch SLO checker; merge or archive |
| `status_export/` | status export helpers | support/doctor | merge into `doctor/` or board export after audit |
| `evidence/` | evidence helpers | support/protocol | merge into result/evidence protocol if still referenced |
| `validators/` | tiny validator placeholder | archive candidate | keep until tests/reference audit proves unused |

## 4. Merge Principles

Use these principles instead of deletion:

1. If a directory contains executable helpers still referenced by docs, tests,
   or scripts, keep it until the replacement path is proven.
2. If a directory is historical but explains current decisions, move only after
   recording its new archive location and references.
3. If two directories express the same concept, choose the more general core
   name and migrate references gradually.
4. If a directory mixes portable and host content, split by no-loss audit:
   portable rules to `CoAgent/`, host bindings to `Docs/` or `Results/`.
5. If a helper is superseded by Codex App native tools, document the superseded
   boundary before archiving it.

## 5. Proposed Target Shape

Long-term target:

```text
CoAgent/
  core/
    protocol/
    dispatch/
    context/
    memory/
    hooks/
    doctor/
    skills/
  runtime_experimental/
    runtime/
    transport/
    result_router/
    automation/
    work_queue/
    review_queue/
  support/
    bootstrap/
    knowledge/
    learning/
    devops/
    evidence/
    status_export/
  archive/
    gateway/
    tasks/
    legacy_helpers/
  docs/
    architecture/
    operating/
    research/
    decisions/
```

This is a conceptual target, not an immediate directory move. The current repo
can first use classification documents and migration maps without changing
paths.

## 6. Safer Intermediate Shape

Before physical moves, add classification metadata:

```text
CoAgent/DIRECTORY_CLASSIFICATION.md
CoAgent/docs/architecture/coagent_directory_merge_design_20260610.md
CoAgent/docs/operating/MIGRATION_MAP.md rows for each merge
```

Each directory gets:

```text
path:
class:
current_entrypoints:
current_references:
tests:
runtime_authority: active | support | legacy | archive
portable_status: portable | mixed | host_local | historical
merge_target:
delete_allowed: false
next_review:
```

## 7. Reference Audit Before Any Move

For each candidate directory, run:

```powershell
rg -n "CoAgent/<dir>|CoAgent\\<dir>" AGENTS.md Docs CoAgent Scripts Results
rg --files CoAgent/<dir>
python -m pytest <related tests if any>
git diff --check -- <touched paths>
```

Move or rename only if:

1. all references are updated or intentionally preserved,
2. tests/checkers pass,
3. no active automation, packet, or dispatch path uses the old location,
4. a no-loss migration row exists,
5. the user/PMO approves the move.

## 8. Automation Merge Proposal

Recommended classification:

```text
C:\Users\HP\.codex\automations
  real Codex App scheduler storage
  user-profile state
  not portable CoAgent source

CoAgent/automation
  durable automation definition and guardrail reference
  project-owned dry-run/reviewed-start helper
  not the active wall-clock scheduler
```

Possible future merge:

```text
CoAgent/automation/automation_tasks.json
  -> CoAgent/protocol/templates/automation_task_schema.json or capability cards

CoAgent/automation/guardrails.py
  -> CoAgent/hooks or CoAgent/doctor if still useful

CoAgent/automation/automation_runner.py
  -> runtime_experimental/automation_runner.py until a real scheduler adapter is approved

CoAgent/automation/SCHEDULED_AUTOMATION_DECISION.md
  -> CoAgent/docs/decisions/ if it remains a design decision
```

No file should be deleted in this step.

## 9. Suggested First Review Batch

Start with the smallest, lowest-risk review batch:

```text
automation/
gateway/
work_queue/
review_queue/
blocker_packet/
task_health/
status_export/
validators/
```

For each, produce:

```text
current references
current runtime use
tests/checkers
recommended class
merge target
manual-review question
```

Do not move files until the review is accepted.

## 10. Open Questions

1. Should `CoAgent/automation` become a permanent portable automation-policy
   module, or should it be archived after Codex App automation prompt storage is
   documented?
2. Should legacy runtime directories be grouped under an actual
   `runtime_experimental/` folder, or only marked through metadata to avoid
   breaking references?
3. Should historical gateway code be preserved under `docs/research` as design
   evidence, or under `archive/gateway` as old implementation material?
4. Should MoSim-specific support helpers under `CoAgent/devops` move to host
   `Scripts/`, or remain CoAgent support until another project reuses them?
5. Should a checker enforce that portable core docs do not reference host-local
   Windows paths or current thread IDs?

## 11. Recommended Next Action

Do not delete or move directories now.

Next safe task:

```text
write CoAgent/DIRECTORY_CLASSIFICATION.md as a reviewable inventory
classify each directory with references and runtime authority
mark delete_allowed=false for all entries
identify first merge candidates
```

After that, perform one no-loss merge pilot on a low-risk legacy directory.
