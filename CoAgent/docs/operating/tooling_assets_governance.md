# Tooling Assets Governance

> Portable governance for skills, workflows, plugins, MCP servers, scripts,
> hooks, checkers, and capability indexes used by a CoAgent deployment.

Status: split-audited portable core, 2026-06-10 CST.

Host-local paths, machine config, product-specific tools, and domain adapters
belong in the host project. For MoSim, use
`Docs/Workflows/tooling_assets_governance.md`, `Docs/Index/api_index.md`,
`Docs/Index/capability_index.md`, and the relevant domain skills.

## 1. Scope

This workflow covers these asset families:

| Asset Family | Meaning |
|---|---|
| Reference sources | External projects, vendor examples, papers, docs, and source audits used as learning input. |
| Skills | Condensed task-family procedures loaded on demand. |
| Workflows | Repeatable operating procedures, recovery routes, evidence gates, and cross-tool sequences. |
| Indexes | Routing tables for workflows, APIs, capabilities, references, memory, and evidence. |
| MCP/app/plugin surfaces | Live tool/data/action boundaries exposed by the host environment. |
| Scripts and checkers | Deterministic helpers for validation, evidence collection, and contract enforcement. |
| Hooks | Mechanical guardrails around session start, tool use, path safety, and completion checks. |

This workflow does not approve a tool action. Approval comes from the current
user/PMO decision, task packet scope, workflow authority, schema/checker, or
host policy.

## 2. Native Surface Policy

Use native or installed surfaces before extending CoAgent runtime. CoAgent
should fill project-specific gaps, not duplicate capabilities already exposed
by the host assistant environment.

Decision rule:

```text
mechanical guardrail -> hook + project preflight
durable repo instruction -> entry document
task procedure -> skill or workflow
live external action -> MCP/app/plugin
recurring reminder/check -> automation or verified scheduler
durable specialty context -> visible thread
bounded parallel work -> short-lived sub-agent
code review gate -> native review or scoped reviewer
background one-shot -> non-interactive execution surface
document/runtime dependency lookup -> host dependency helper or API index
project-specific packet/evidence glue -> CoAgent protocol/runtime helper
```

Before dispatching a non-trivial task, record the selected surface and rejected
alternatives when they matter. If the native surface is sufficient, do not add
new CoAgent runtime, transport, queue, or schema machinery for that task.

## 3. Capability Router

The capability index answers:

```text
which native surface / plugin / MCP / skill / script / visible thread /
sub-agent / checker should this task consider?
```

It does not answer:

```text
is this action authorized?
is this result accepted?
is this tool healthy right now?
```

Recommended capability-card fields:

```text
capability_id:
surface_type:
use_when:
owning_workflow_or_skill:
required_scope_field:
forbidden_actions:
health_or_checker:
claim_ceiling:
last_verified:
host_adapter:
```

Task packets may include `capability_index_consulted`,
`selected_capabilities`, and `rejected_capabilities` as planning evidence.
Those fields are advisory unless a checker/schema makes them mandatory for the
host workflow.

## 4. Ownership

Default ownership:

| Owner | Responsibility |
|---|---|
| Task owner | Updates the relevant doc when a reusable command, failure mode, recovery path, or operating constraint is discovered during the task. |
| Meta-maintenance owner | Audits stale indexes, duplicate workflows/skills, capability inventory, recurring checks, and missing landing records. |
| Domain owner | Owns domain-specific tools, MCPs, evidence gates, and stop conditions. |
| Release/Git owner | Owns imports, ignore/LFS rules, large-file checks, and integration commits. |
| Documentation secretary | Prepares reviewable context/documentation patches; does not change product priority or acceptance. |

No standing toolchain department is required by default. Create one only when a
host project has enough ongoing tool-operation work to justify durable context.

## 5. Tool Intake Pipeline

Do not move crawled or third-party material directly into active skills or
runtime config. Use this pipeline:

```text
discover or receive source
  -> inventory and source record
  -> classify: adopt | adapt | reference_only | reject | blocked
  -> inspect primary docs or source
  -> run a narrow smoke check when executable behavior is required
  -> write or update host workflow/skill only after the route is understood
  -> add runtime wrapper/config only when the server or script is useful
  -> add health check and recovery note
  -> update indexes and startup pointers only if routing changes
```

Required fields for a new reference source:

```text
name:
source_url:
local_path:
quality_signal:
license:
last_checked:
category:
possible_use:
adoption_status:
risks:
evidence_path:
owner:
```

Required fields for a new or changed MCP/app/plugin/script:

```text
name:
purpose:
launcher_or_entry:
runtime_lane:
workspace_boundary:
health_check:
smoke_test:
common_failures:
recovery_steps:
dangerous_calls:
related_skill_or_workflow:
owner:
last_verified:
```

Required fields for a new or changed skill:

```text
skill_name:
trigger_condition:
minimum_context_to_read:
tool_sequence:
forbidden_actions:
evidence_required:
smoke_or_acceptance_check:
overlap_with_existing_skills:
owner:
last_verified:
```

## 6. Runtime Boundaries

Every live tool surface must declare:

```text
read boundary:
write boundary:
auth boundary:
destructive actions:
manual-review actions:
health check:
claim ceiling:
rollback or blocker path:
```

Observation and action are separate capabilities. Screenshot, readback, or
status inspection does not imply permission to click, approve, restart, save,
publish, delete, or mutate runtime state.

## 7. Context Hygiene

Load the smallest context that can answer the task:

1. Entry document for hard boundaries and read order.
2. One owning workflow or skill.
3. Capability/API index only when routing or tool details are needed.
4. Host adapter for project-specific evidence gates.
5. Result packets or ledgers only when trace-back evidence is required.

Avoid loading entire documentation trees, plugin caches, old transcript dumps,
or broad reference mirrors as startup context.

## 8. Entry-Document Slimming Rule

Entry documents should contain:

- hard boundaries;
- startup order;
- authority map;
- source-of-truth pointers;
- compact current-route corrections when fresh conversations require them.

Move detailed content to:

| Detail Type | Landing |
|---|---|
| executable state machine | workflow |
| packet fields | schema/template/communication contract |
| tool sequence | skill or API index |
| domain evidence gate | host adapter or domain workflow |
| repeated incident lesson | owning workflow plus audit |
| current board state | board/progress file |
| historical trace | ledger or result packet |

No slimming is complete until a no-loss landing row records the target and
status.

## 9. Immediate Documentation Rule

When a task reveals a reusable correction, patch the owning document before
claiming completion, unless the task packet explicitly forbids writes.

Examples of reusable corrections:

- a tool requires a different health check;
- a workflow stop trigger is missing;
- a packet field is ambiguous;
- a capability is relevant but not indexed;
- a repeated failure mode needs a checker or schema gate.

If the correction is uncertain, write a candidate note or blocker instead of
promoting it as policy.

## 10. Maintenance Cadence

Suggested cadence:

| When | Check |
|---|---|
| before major dispatch | selected capability, owner workflow, evidence gate, stop trigger |
| weekly or before release | broken workflow/index links, duplicate skills, stale route names |
| after tool upgrade | hook/checker health, MCP/plugin smoke tests, API index drift |
| after repeated failure | owner workflow patched or explicit non-adoption recorded |
| before external import | license, large files, generated assets, auth boundary, ignore/LFS plan |

## 11. Acceptance Gates

A tooling-governance update is complete when:

- the selected surface is indexed or explicitly rejected;
- the owner workflow or skill exists;
- forbidden actions and claim ceiling are clear;
- health/checker evidence is named;
- host-local paths and product facts stay in host adapters;
- entry documents receive only necessary pointers;
- no new runtime dependency is introduced without a smoke check or blocker.
