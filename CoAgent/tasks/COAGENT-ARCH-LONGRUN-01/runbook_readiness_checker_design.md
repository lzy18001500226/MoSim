# COAGENT-ARCH-LONGRUN-01 Runbook Readiness Checker Design

Date: 2026-05-30
Status: design contract for `COAGENT-IMPL-NEXT-30`

## Purpose

Define the read-only checker that decides whether a serious task package is
ready to enter multi-conversation execution, proof-package validation, manual
rehearsal, or closeout review.

This document extends:

- `end_to_end_task_operating_runbook.md`
- `validator_shared_envelope_design.md`
- `goal_alignment_checker_design.md`
- `proof_ladder_and_validator_order.md`
- `common_proof_package_validator_design.md`
- `mailbox_ledger_and_replay_design.md`

It is design-only. It does not dispatch conversations, create conversations,
create worktrees, call MCP/tools, stage Git, send notifications, mutate goals,
or mark tasks complete.

## Core Rule

```text
a serious task is not ready when the next safe action exists only in chat
```

The checker verifies that the task package can be resumed, reviewed, routed,
blocked, integrated, and closed from project-owned files.

## Inputs

The future checker should accept:

```text
--task-id <task id>
--task-root <task directory or proof package directory>
--mode intake|preflight|post_dispatch|closeout|fixture
--json-output <optional path>
```

Input files, when present:

| File | Purpose |
|---|---|
| `task_charter.md` or `task_charter.yaml` | canonical goal and done definition |
| `proof_path_decision.yaml` | task class, first gate, minimum team, secondary risks |
| `context_pack.md` | curated context and rejected assumptions |
| `retrieval_manifest.yaml` | context source paths and budget class |
| `workflow_graph.yaml` | task nodes, dependencies, owners, and review gates |
| `handoff_*.yaml` | scoped objectives and expected result paths |
| `mailbox/*.yaml` | expected messages, acknowledgements, and response state |
| `result_packets/*.yaml` | worker outputs and evidence claims |
| `blocker_packets/*.yaml` | durable blocked state and resume conditions |
| `review_packets/*.yaml` | verification, safety, product, DevOps, or PMO reviews |
| `git_disposition.yaml` | integration, hold, discard, or superseded state |
| `knowledge_delta.yaml` | promotion, rejection, deferral, or retrospective action |
| `closeout_summary.md` | final disposition and remaining gated follow-ups |

The checker may run with partial files in `intake` mode, but it must not claim
dispatch or closeout readiness without the required stage files.

## Readiness Levels

| Level | Meaning |
|---|---|
| `intake_ready` | task can become a canonical charter |
| `preflight_ready` | package can enter validation or manual rehearsal |
| `dispatch_ready` | package can be dispatched after dependency validators pass |
| `post_dispatch_ready` | returned packets can be reviewed without hidden chat |
| `integration_ready` | mutable work has review and Git disposition |
| `closeout_ready` | task slice can be closed without unresolved durable state |
| `not_ready` | required fields/files are missing or contradictory |

No readiness level proves product correctness, tool reliability, automated
transport, Git safety, or implementation completion by itself.

## Required Checks

### Intake Readiness

Check that the package records:

- user objective;
- canonical task goal;
- non-goals;
- project boundary;
- first uncertainty that changes routing;
- review owner;
- close owner;
- stop condition.

Reject if the goal is only setup, elapsed time, conversation creation, document
volume, Git activity, or a backlog item.

### Proof Path Readiness

Check that the task class maps to a proof path:

- Candidate A for architecture mechanics;
- Candidate B for PX4/log parameter identification;
- Candidate C for UE scene truth/productization;
- Candidate D for Git-heavy change;
- Candidate E for auth/license/manual interruption;
- ordinary small task when no multi-conversation proof is needed.

Reject if:

- no first gate exists;
- high-risk secondary risks are omitted;
- all departments are selected without a reason;
- product work starts before tool/data/source gate;
- manual rehearsal is requested without explicit approval record.

### Context Readiness

Check that the context pack has:

- source path map;
- accepted decisions;
- rejected assumptions;
- stale material policy;
- retrieval manifest or source list;
- budget class;
- context version/hash;
- acknowledgement requirement for high-risk work.

Reject raw full transcript context, oversized packs without split
recommendation, stale packs without acknowledgement, and context that omits
known rejected assumptions for PX4 or UE tasks.

### Workflow And Handoff Readiness

Every node must have:

- local objective;
- alignment to canonical goal;
- input filter;
- context path;
- expected output path;
- review gate;
- return path;
- stop condition;
- forbidden actions.

Reject hidden dependencies, missing result paths, missing review owner,
unbounded write scope, same-file conflict without integration owner, and any
node that can mutate the canonical goal.

### Mailbox And Packet Readiness

Check that cross-conversation communication has:

- allowed message types;
- message ids;
- sender and receiver;
- expected response state;
- acknowledgement records when required;
- result or blocker path for each active work node.

Reject closed tasks with open required responses, duplicate active blockers
with different asks, result packets without evidence paths, and blocker packets
without last safe state or resume condition.

### Evidence And Review Readiness

Check that claims have evidence labels and review disposition:

- design-only;
- offline script;
- manual review;
- GUI evidence;
- MCP/tool evidence;
- Git metadata;
- runtime metadata;
- external reference.

Reject label inflation, unsupported evidence labels, product claims from design
docs, screenshot-as-truth, and external references promoted without adoption
decision.

### Git And Integration Readiness

For mutable work, require:

- change inventory;
- path family classification;
- write scope match;
- large-file/generated-output policy;
- review owner;
- merge owner;
- close owner;
- rollback plan;
- cleanup state.

Reject broad staging plans, external path mutations, large binaries without
policy, destructive actions without explicit approval, and missing Git
disposition.

### Knowledge And Retrospective Readiness

Check that completed or repeated learning has:

- knowledge promotion decision;
- rejected lesson record when not promoted;
- retrospective action for repeated failures;
- owner and review owner;
- closeout criteria or deferral reason.

Reject repeated incidents that remain status-only notes.

### Closeout Readiness

Closeout requires:

- result packet or accepted no-op disposition;
- review disposition;
- closed or carried-forward blocker state;
- acknowledged context delta;
- closed mailbox responses;
- Git disposition for mutable work;
- knowledge decision;
- remaining work represented as a task or accepted gated follow-up.

Reject completion if any requirement passes only because a file exists, a
backlog item exists, time passed, conversations exist, or implementation was
planned.

## Stable Finding Codes

| Code | Meaning |
|---|---|
| `RUNBOOK_CHARTER_MISSING` | task charter is missing |
| `RUNBOOK_GOAL_NOT_ALIGNED` | goal checker dependency failed or goal fields are weak |
| `RUNBOOK_FIRST_GATE_MISSING` | no proof path or first gate |
| `RUNBOOK_TOPOLOGY_UNJUSTIFIED` | all-department or multi-conversation routing lacks reason |
| `RUNBOOK_CONTEXT_MISSING` | context pack or source map missing |
| `RUNBOOK_CONTEXT_TOO_LARGE` | context exceeds budget without split recommendation |
| `RUNBOOK_REJECTED_ASSUMPTION_MISSING` | high-risk known false assumption omitted |
| `RUNBOOK_WORKFLOW_MISSING` | workflow graph or handoff records missing |
| `RUNBOOK_RESULT_PATH_MISSING` | delegated node lacks expected result path |
| `RUNBOOK_REVIEW_OWNER_MISSING` | review owner missing for a risk-bearing node |
| `RUNBOOK_FORBIDDEN_ACTION_UNDECLARED` | handoff lacks forbidden actions |
| `RUNBOOK_MAILBOX_UNREPLAYABLE` | mailbox state cannot reconstruct next safe action |
| `RUNBOOK_OPEN_RESPONSE_ON_CLOSE` | closeout attempted with open required response |
| `RUNBOOK_PACKET_INVALID_OR_MISSING` | result or blocker packet missing or invalid |
| `RUNBOOK_EVIDENCE_LABEL_MISSING` | claim lacks evidence label |
| `RUNBOOK_EVIDENCE_INFLATED` | weak evidence is promoted into stronger proof |
| `RUNBOOK_GIT_DISPOSITION_MISSING` | mutable work lacks Git disposition |
| `RUNBOOK_KNOWLEDGE_DECISION_MISSING` | completed learning lacks promotion/rejection/deferral |
| `RUNBOOK_RETRO_ACTION_MISSING` | repeated failure lacks retrospective action |
| `RUNBOOK_CLOSEOUT_OVERCLAIM` | closeout claims more than evidence supports |
| `RUNBOOK_DEPENDENCY_MISSING` | required validator report missing |
| `RUNBOOK_FORBIDDEN_SIDE_EFFECT` | checker attempted or declared forbidden mutation |

## Dependency Reports

The checker should consume shared-envelope reports when they exist:

| Dependency | Required Before |
|---|---|
| goal alignment checker | any readiness beyond intake |
| evidence label doctor | evidence/review, integration, closeout |
| context delta checker | dispatch and post-dispatch resume |
| handoff/workflow validator | dispatch readiness |
| result packet validator | post-dispatch and closeout |
| blocker packet validator | blocked or resumed tasks |
| mailbox replay checker | post-dispatch and closeout |
| tool capability health gate | PX4/UE/MWORKS/Fab/Codex/Git tool-dependent tasks |
| Git/worktree validator | mutable Git-heavy work |
| retrospective closure checker | repeated-failure closeout |

If a required dependency is absent:

- report `needs_dependency` in design audit mode;
- report `fail_before_dispatch` before live dispatch;
- report `blocked` before closeout when the missing dependency could change
  the closeout decision.

## Fixture Matrix

Positive fixtures:

| Fixture | Expected |
|---|---|
| Candidate A package with charter, context, workflow, handoffs, mailbox, packets, review, and closeout | `dispatch_ready` or `closeout_ready` by mode |
| PX4 intake package with explicit matrix-only limitation | `preflight_ready` |
| UE capability-only package with planning readiness false | `preflight_ready` |
| Git inventory-only package with hold disposition | `integration_ready` |

Negative fixtures:

| Fixture | Expected Codes |
|---|---|
| goal says "create task and open conversations" | `RUNBOOK_GOAL_NOT_ALIGNED` |
| multi-conversation topology with no proof path | `RUNBOOK_FIRST_GATE_MISSING`, `RUNBOOK_TOPOLOGY_UNJUSTIFIED` |
| raw transcript as context | `RUNBOOK_CONTEXT_TOO_LARGE` |
| UE package omits "rendering is not planning truth" | `RUNBOOK_REJECTED_ASSUMPTION_MISSING` |
| handoff lacks expected result path | `RUNBOOK_RESULT_PATH_MISSING` |
| closeout has open mailbox response | `RUNBOOK_OPEN_RESPONSE_ON_CLOSE` |
| design doc claims product proof | `RUNBOOK_EVIDENCE_INFLATED` |
| mutable work has no Git disposition | `RUNBOOK_GIT_DISPOSITION_MISSING` |
| repeated visibility drift has no retrospective action | `RUNBOOK_RETRO_ACTION_MISSING` |
| missing shared-envelope dependency before dispatch | `RUNBOOK_DEPENDENCY_MISSING` |

## Output

The checker should emit the shared validator envelope, for example:

```json
{
  "schema_version": "coagent.validator_report.v1",
  "validator": "runbook_readiness_checker",
  "task_id": "COAGENT-PROOF-CANDIDATE-A",
  "mode": "preflight",
  "decision": "fail_before_dispatch",
  "ok": false,
  "readiness_level": "not_ready",
  "finding_codes": ["RUNBOOK_RESULT_PATH_MISSING"],
  "findings": [
    {
      "code": "RUNBOOK_RESULT_PATH_MISSING",
      "severity": "error",
      "path": "workflow_graph.yaml",
      "message": "ContextMemoryAgent node has no expected result packet path",
      "remediation": "add expected_result_path before dispatch"
    }
  ],
  "dependency_reports": [],
  "evidence_paths": [
    "CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/end_to_end_task_operating_runbook.md"
  ],
  "side_effects": {
    "declared": ["read_project_files", "write_validator_report"],
    "forbidden": ["live_dispatch", "conversation_creation", "mcp_or_tool_call", "git_mutation", "goal_mutation"]
  },
  "claim_boundaries": [
    {
      "claim": "task package is dispatch-ready",
      "supported": false,
      "limitations": "readiness check does not execute dispatch or prove product behavior"
    }
  ],
  "next_action": "repair workflow graph before any live dispatch"
}
```

## Implementation Boundary

The first implementation should be read-only and fixture-backed. It may read
project task packages and write reports under `Results/coagent_validators/`.
It must not create, delete, mutate, complete, or block Codex goals; create or
dispatch conversations; call MCP/tools; create worktrees; stage Git; send
notifications; edit Codex state; rewrite task documents automatically; or
inspect credentials, account caches, provider configs, or private chat history.
