# COAGENT-ARCH-LONGRUN-01 Handoff Mode And Workflow Graph Design

Date: 2026-05-30
Status: design draft

## Purpose

The vendor gap review identified a concrete issue: CoAgent has topology names,
but the handoff decision is still too easy to express as prose. This document
turns routing into two explicit design objects:

- `handoff_mode`: how one owner transfers or delegates work;
- `workflow_graph`: how one task team's nodes and gates relate.

This is design only. It does not implement graph execution or app-server
transport.

## Handoff Mode

Use `handoff_mode` whenever work moves between conversations, departments, or
review lanes.

Template:

```text
CoAgent/protocol/templates/handoff_mode.yaml
```

Required fields:

| Field | Purpose |
|---|---|
| `mode` | direct main, department lane, subagent call, scoped conversation, task team, review board, arena, or incident |
| `from_owner` / `to_owner` | makes responsibility transfer explicit |
| `authority_transfer` | says whether execution, review, integration, or incident command moved |
| `input_filter` | prevents raw transcript and secret/path pollution |
| `context_pack_path` | defines starting context |
| `expected_result_packet_path` | defines return artifact |
| `review_gate` | names who accepts or rejects |
| `return_path` | prevents orphaned work |
| `cancellation_or_resume_rule` | defines timeout, stale-context, and blocker behavior |

## Handoff Modes

| Mode | Use | Authority transfer |
|---|---|---|
| `direct_main` | small direct work | none |
| `department_lane` | one permanent lane reviews or executes a bounded task | scoped execution or review |
| `manager_calls_subagents` | parent uses bounded disposable helpers | none outside parent |
| `handoff_to_scoped_conversation` | one visible task-slice conversation owns execution | scoped execution |
| `task_team_parallel_slices` | multiple visible slices work in parallel | scoped execution per slice |
| `review_board` | high-impact design or safety decision | review gate |
| `arena_comparison` | bounded alternatives evaluated by same rubric | scoped execution plus review |
| `incident_response` | unsafe state, repeated failure, corrupted state, or activation/login block | incident command |

## Handoff Gate

Dispatch must not approve a handoff if any of these are missing:

- canonical task goal;
- local objective;
- context pack path;
- expected result packet path;
- review owner;
- close or cancellation condition;
- forbidden actions;
- evidence requirement.

For implementation later, this should become a validator before any automatic
dispatch starts.

## Workflow Graph

Use `workflow_graph` when one task needs more than one node, dependency, review
gate, or interrupt.

Template:

```text
CoAgent/protocol/templates/workflow_graph.yaml
```

Node types:

- `deterministic`: script, validator, or static check;
- `agent`: visible conversation or bounded subagent;
- `tool`: MCP/tool capability call;
- `review`: Verification/Safety/Product/DevOps review;
- `artifact`: output that must exist before next step;
- `human_interrupt`: user action, login, license, or manual review;
- `merge`: Git/worktree integration.

Edge types:

- `depends_on`;
- `handoff`;
- `parallel_join`;
- `review_gate`;
- `resume_after`.

## Workflow Graph Rules

1. Every graph has one `task_id` and one canonical task goal.
2. Every agent node has a handoff mode or task packet.
3. Every review node has evidence inputs.
4. Every human interrupt has a blocker packet and resume packet.
5. Every merge node has an integration plan and rollback plan.
6. No node may change the canonical goal.
7. A blocked node must not remain invisible to the shared task board.

## Minimal Graph For Candidate A

```text
dispatch_charter
  -> context_pack
  -> context_review_agent
  -> result_packet
  -> verification_review
  -> context_delta
  -> knowledge_promotion
  -> closeout
```

Required joins:

- `result_packet` cannot close until `verification_review` completes;
- `context_delta` cannot be marked consumed until acknowledgement is present;
- `closeout` cannot complete while mailbox required responses are open.

## Minimal Graph For PX4 Gate

```text
dispatch_charter
  -> log_audit_context_pack
  -> log_audit_agent
  -> identifiability_matrix
  -> verification_review
  -> estimator_go_or_stop_decision
```

Stop condition:

If identifiability fails, the graph ends with `input_required` or
`non_identifiable_parameters_recorded`. It must not continue into estimator
implementation.

## Minimal Graph For UE Scene Truth Gate

```text
dispatch_charter
  -> scene_source_context_pack
  -> toolchain_capability_agent
  -> scene_capability_card
  -> safety_review_if_needed
  -> verification_review
  -> truth_export_go_or_stop_decision
```

Stop condition:

If UE/Fab automation is not proven, the graph produces a manual-import blocker
or local-project fallback. It must not spend days retrying Fab automation.

## Relationship To Worktrees

The workflow graph does not create worktrees. It only records whether a node
requires one.

Worktree creation remains gated and must use:

```text
CoAgent/protocol/templates/worktree_binding.yaml
```

Read-only research and design proof nodes should default to no worktree.

## Relationship To Metrics

Each workflow graph node should later provide enough data to calculate:

- critical path age;
- blocked time;
- handoff failures;
- context refresh latency;
- review escape;
- closeout latency.

If a metric cannot be calculated, the trace evaluation records
`needs_instrumentation`.

## Acceptance For This Design Object

This design object is acceptable when:

- task routing decisions are no longer only prose;
- handoff authority and return path are explicit;
- workflow graph nodes expose dependencies and review gates;
- interrupts have resume semantics;
- future automation can validate a graph before executing it.
