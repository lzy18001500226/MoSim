# COAGENT-ARCH-LONGRUN-01 Handoff Workflow Validator Design

Date: 2026-05-30
Status: design contract for `COAGENT-IMPL-NEXT-13`

## Purpose

CoAgent uses `handoff_mode` and `workflow_graph` objects to make routing
explicit instead of prose-only. This document defines how a later read-only
validator should check those objects before dispatch or proof execution.

This is design-only. It does not execute a workflow graph, create
conversations, create worktrees, dispatch packets, call tools/MCP, stage Git,
or send notifications.

## Core Rule

```text
no handoff or workflow graph is dispatchable until it validates
```

A graph is only an execution plan after the validator proves that goal,
context, authority, output path, review, blocker, and closeout semantics are
recoverable from files.

## Inputs

Future command shape:

```bash
python3 CoAgent/validators/handoff_workflow_validator.py \
  --handoff CoAgent/protocol/templates/handoff_mode.yaml \
  --workflow CoAgent/protocol/templates/workflow_graph.yaml \
  --task-id COAGENT-PROOF-CANDIDATE-A \
  --mode pre_dispatch \
  --json-output Results/coagent_validators/handoff_workflow.json
```

Modes:

- `handoff_only`: validate one handoff packet;
- `workflow_only`: validate one graph;
- `pre_dispatch`: validate handoffs and graph together before routing work;
- `post_dispatch`: validate that node outputs, reviews, blockers, and closeout
  match the graph after execution;
- `fixture`: validate a fixture against expected decision and finding codes.

The validator is read-only except for optional JSON output.

## Required Handoff Fields

| Field | Required | Check |
|---|---|---|
| `handoff_id` | yes | non-empty, task-local unique |
| `task_id` | yes | equals expected task id |
| `canonical_task_goal` | yes | equals workflow and charter goal |
| `mode` | yes | allowed handoff mode |
| `from_owner` | yes | known owner or declared worker |
| `to_owner` | yes | known owner or declared worker |
| `authority_transfer` | yes | allowed authority type |
| `input_filter.include` | yes | includes context, evidence, scope, forbidden actions |
| `input_filter.exclude` | yes | excludes transcript, unrelated work, secrets |
| `context_pack_path` | yes | project-local or approved proof-local path |
| `expected_result_packet_path` | yes | under proof root or `Results/agent_packets/` |
| `review_gate` | yes | known reviewer or review node |
| `return_path` | yes | not empty, normally Dispatch/MainAgent |
| `cancellation_or_resume_rule` | yes | names cancel/resume/stale-context behavior |
| `acceptance.reviewer` | yes | not empty |
| `acceptance.terminal_states` | yes | non-empty allowed states |

## Required Workflow Fields

| Field | Required | Check |
|---|---|---|
| `workflow_id` | yes | non-empty |
| `task_id` | yes | equals expected task id |
| `canonical_task_goal` | yes | equals handoff and charter goal |
| `created_by` | yes | known owner |
| `nodes` | yes | at least one node |
| `edges` | conditional | required when multiple nodes exist |
| `interrupts` | conditional | required for human/tool/auth/license waits |
| `review.required_review_nodes` | yes | all referenced nodes exist |
| `review.final_review_owner` | yes | known reviewer |
| `close_condition` | yes | contains terminal, artifacts, review, integration rules |

Every node must define:

- `node_id`;
- `node_type`;
- `owner`;
- `objective`;
- `input_packets`;
- `output_packets`;
- `state`.

## Allowed Values

Handoff modes:

- `direct_main`
- `department_lane`
- `manager_calls_subagents`
- `handoff_to_scoped_conversation`
- `task_team_parallel_slices`
- `review_board`
- `arena_comparison`
- `incident_response`

Authority transfer:

- `none`
- `scoped_execution`
- `review_gate`
- `integration`
- `incident_command`

Node types:

- `deterministic`
- `agent`
- `tool`
- `review`
- `artifact`
- `human_interrupt`
- `merge`

Edge types:

- `depends_on`
- `handoff`
- `parallel_join`
- `review_gate`
- `resume_after`

Node states:

- `pending`
- `running`
- `blocked`
- `review_required`
- `completed`
- `cancelled`

## Cross-Object Checks

The validator should reject when:

- task id differs across handoff, workflow, and charter;
- canonical goal differs across objects;
- a workflow agent node has no matching handoff or task packet;
- a handoff expected result path is not produced by any matching workflow node;
- a review gate references a missing review node;
- `return_path` is empty or points to an unknown owner;
- close condition cannot be satisfied by declared nodes/artifacts/reviews;
- a blocked or human-interrupt node lacks blocker and resume packet paths;
- a merge node lacks integration plan and rollback plan;
- a tool node lacks tool/MCP capability gate and blocker class;
- a node can finish without evidence or review where review is required;
- any object uses raw transcript, secret path, or private session data as
  context.

## Dispatch Safety Checks

Before dispatch, reject if:

- context pack path is missing or absent;
- expected result packet path is absent;
- review owner is absent;
- cancellation/resume rule is absent;
- forbidden actions are not declared for non-trivial work;
- output path is outside the project, proof root, or approved `Results/`;
- workflow has a cycle without an explicit review/interrupt reason;
- workflow has an unreachable required review or closeout node;
- high-risk node type appears without Safety/Verification review.

High-risk node types:

- `tool`;
- `human_interrupt`;
- `merge`;
- any node declaring Git, UE, MWORKS, Fab, login, license, notification,
  worktree creation, delete, move, force push, or external path write.

## Post-Dispatch Checks

After execution, reject or block if:

- required node output packet is missing and no blocker exists;
- a node marked `completed` has no evidence;
- a review node has no terminal review decision;
- an interrupt has no resume packet or still-open blocker;
- graph closeout is marked complete while required nodes are not terminal;
- graph closeout is marked complete while mailbox has open required responses;
- graph state claims completion after a worker changed the canonical goal;
- integration is requested without integration owner, diff scope, checks, and
  rollback plan.

## Output JSON

Required report shape:

```json
{
  "ok": false,
  "decision": "fail_before_dispatch",
  "mode": "pre_dispatch",
  "task_id": "COAGENT-PROOF-CANDIDATE-A",
  "handoff_paths": ["handoffs/context.yaml"],
  "workflow_path": "workflow_graph.yaml",
  "finding_codes": ["HWFLOW_REVIEW_GATE_MISSING"],
  "findings": [
    {
      "code": "HWFLOW_REVIEW_GATE_MISSING",
      "severity": "error",
      "path": "handoffs/context.yaml",
      "field": "review_gate",
      "message": "review gate is required before dispatch"
    }
  ],
  "dispatch_allowed": false,
  "next_action": "fix_handoff_before_dispatch"
}
```

Decisions:

- `pass`;
- `pass_with_warnings`;
- `fail_before_dispatch`;
- `blocked_after_dispatch`;
- `needs_review`;
- `needs_dependency`;
- `rejected`.

## Stable Finding Codes

| Code | Meaning |
|---|---|
| `HWFLOW_TASK_ID_MISMATCH` | task id differs across objects |
| `HWFLOW_GOAL_MISMATCH` | canonical goal differs |
| `HWFLOW_UNKNOWN_MODE` | unsupported handoff mode |
| `HWFLOW_UNKNOWN_AUTHORITY` | unsupported authority transfer |
| `HWFLOW_CONTEXT_PACK_MISSING` | context path missing or absent |
| `HWFLOW_RESULT_PATH_MISSING` | expected result path absent |
| `HWFLOW_OUTPUT_PATH_UNSAFE` | output path outside approved roots |
| `HWFLOW_REVIEW_GATE_MISSING` | review gate or node absent |
| `HWFLOW_RETURN_PATH_MISSING` | return path absent |
| `HWFLOW_CANCEL_RESUME_MISSING` | cancellation/resume rule absent |
| `HWFLOW_FORBIDDEN_ACTIONS_MISSING` | forbidden actions absent |
| `HWFLOW_AGENT_NODE_UNROUTED` | agent node lacks handoff/task packet |
| `HWFLOW_BLOCKER_RESUME_MISSING` | interrupt/blocked node lacks blocker/resume |
| `HWFLOW_TOOL_GATE_MISSING` | tool node lacks capability/blocker gate |
| `HWFLOW_MERGE_PLAN_MISSING` | merge node lacks integration/rollback |
| `HWFLOW_REQUIRED_NODE_UNREACHABLE` | required node cannot be reached |
| `HWFLOW_CYCLE_UNJUSTIFIED` | cycle exists without review/interrupt reason |
| `HWFLOW_CLOSEOUT_UNSATISFIABLE` | close condition cannot be met |
| `HWFLOW_RAW_TRANSCRIPT_CONTEXT` | raw transcript used as context |
| `HWFLOW_SECRET_OR_PRIVATE_PATH` | secret/private path included |
| `HWFLOW_MISSING_OUTPUT_PACKET` | post-dispatch output absent with no blocker |
| `HWFLOW_NON_TERMINAL_REVIEW` | review node has no terminal decision |
| `HWFLOW_OPEN_BLOCKER_AT_CLOSE` | closeout attempted with open blocker |
| `HWFLOW_GOAL_MUTATION` | worker or node changed canonical goal |

## Fixture Matrix

Positive fixtures:

| Fixture | Expected |
|---|---|
| valid single department handoff | `pass` |
| valid Candidate A preflight graph | `pass` |
| valid blocked interrupt with blocker/resume paths | `pass_with_warnings` |

Negative fixtures:

| Fixture | Expected Codes |
|---|---|
| missing result path | `HWFLOW_RESULT_PATH_MISSING` |
| missing review gate | `HWFLOW_REVIEW_GATE_MISSING` |
| missing return path | `HWFLOW_RETURN_PATH_MISSING` |
| goal mismatch | `HWFLOW_GOAL_MISMATCH` |
| unsafe output path | `HWFLOW_OUTPUT_PATH_UNSAFE` |
| unrouted agent node | `HWFLOW_AGENT_NODE_UNROUTED` |
| tool node without capability gate | `HWFLOW_TOOL_GATE_MISSING` |
| merge node without rollback | `HWFLOW_MERGE_PLAN_MISSING` |
| closeout impossible | `HWFLOW_CLOSEOUT_UNSATISFIABLE` |
| raw transcript context | `HWFLOW_RAW_TRANSCRIPT_CONTEXT` |
| open blocker at closeout | `HWFLOW_OPEN_BLOCKER_AT_CLOSE` |

## Integration With Candidate A

Candidate A preflight should call this validator before live dispatch. The
Candidate A validator may treat `HWFLOW_*` errors as hard preflight failures.

Candidate A post-dispatch should call this validator to ensure required nodes,
reviews, blockers, and closeout conditions match the declared graph.

## Implementation Boundary

The later implementation slice may add:

- read-only validator script;
- tiny handoff/workflow fixtures;
- tests for stable finding codes;
- JSON report output.

It may not add:

- graph execution;
- automatic dispatch;
- conversation creation;
- app-server transport;
- worktree creation;
- Git stage/commit/push;
- email/desktop notification;
- tool/MCP/UE/MWORKS/Fab calls.

## Design Decision

`handoff_mode` and `workflow_graph` are planning artifacts, not execution
authority. The validator must prove that a graph can be routed and closed
safely before any runtime turns it into work.
