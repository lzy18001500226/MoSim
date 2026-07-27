# COAGENT-ARCH-LONGRUN-01 Operating Metrics Snapshot Design

Date: 2026-05-30
Status: design contract for `COAGENT-IMPL-NEXT-09`

## Purpose

Long-running multi-conversation work needs an objective health snapshot. The
snapshot must show whether a task is making evidence-backed progress, drifting,
blocked, pretending to be parallel, or waiting for review.

This document turns `operating_metrics_and_anti_drift_cadence.md` into an
implementation-ready read-only checker design. It does not implement the
checker, create a dashboard, schedule runs, dispatch conversations, change
transport, or alter runtime schemas.

## Core Rule

```text
no long-running task is healthy merely because it has recent chat activity
```

A healthy task has a current canonical goal, recent evidence on the critical
path, bounded open communication, fresh context, explicit blockers, reviewable
outputs, and no unresolved safety or integration escape.

## Non-Goals

`COAGENT-IMPL-NEXT-09` must not:

- execute conversations or subagents;
- create, delete, rename, or resume Codex sessions;
- create Git worktrees, stage files, commit, or push;
- call MCP tools or external APIs;
- infer private chat content from Codex databases;
- send email or desktop notifications;
- implement a web dashboard;
- silently promote design findings into stable policy.

The first implementation is a file-level, read-only snapshot over durable
CoAgent artifacts.

## Inputs

The future command should accept:

```text
--task-id <task id>
--task-root <path, default CoAgent/tasks/<task-id>>
--runtime-db Results/agent_runtime/tasks.sqlite3
--events-jsonl Results/agent_runtime/events.jsonl
--department-registry CoAgent/dispatch/department_threads.json
--mode snapshot|strict|fixtures
--json-output <optional path>
--markdown-output <optional path>
--now <optional ISO timestamp for deterministic tests>
```

Inputs are read-only. Missing optional inputs should produce
`needs_instrumentation` metrics, not invented values.

## Evidence Sources

| Source | Use |
|---|---|
| `shared_task_board.md` | phase, WIP, item states, risk register, protocol artifacts |
| `architecture_problem_matrix.md` | problem ids, owners, status, required outputs |
| `goal_requirement_audit_map.md` | requirement coverage and weak evidence |
| `review_brief.md` | review surface and forbidden claims |
| `ten_hour_audit_package.md` | final audit mapping and decision points |
| `Results/agent_runtime/tasks.sqlite3` | task state, updated time, claim token |
| `Results/agent_runtime/events.jsonl` | checkpoints, task events, runtime evidence |
| `Results/agent_packets/*.yaml` | department result and blocker packets |
| `Results/coagent_transport/runs/*.summary.md` | transport timeout evidence |
| `CoAgent/dispatch/department_threads.json` | visible conversation registry |

The snapshot may cite additional files only when they are under the project
root and directly linked from the task board, review brief, audit map, runtime
events, or packet evidence.

## Metric Model

Each metric should be represented as:

```json
{
  "metric": "critical_path_age",
  "category": "progress",
  "state": "review_required",
  "value": 87,
  "unit": "minutes",
  "threshold": "review_after_60_minutes",
  "evidence": ["Results/agent_runtime/events.jsonl"],
  "needs_instrumentation": false,
  "finding_codes": ["OMS_CRITICAL_PATH_STALE"],
  "next_action": "record checkpoint or rescope critical path"
}
```

Allowed metric states:

- `ok`
- `info`
- `needs_instrumentation`
- `review_required`
- `blocked`
- `rejected`

State ordering is:

```text
ok < info < needs_instrumentation < review_required < blocked < rejected
```

The overall snapshot state is the highest-severity state among non-informational
metrics, with two exceptions:

- any safety violation is at least `blocked`;
- any forbidden claim presented as completed proof is `rejected`.

## Required Metric Categories

### Progress

| Metric | Evidence | State Rule |
|---|---|---|
| `critical_path_age` | latest checkpoint/runtime event for current critical path | `review_required` after 60 minutes without evidence |
| `checkpoint_count` | runtime events | `needs_instrumentation` if events are missing |
| `checkpoint_age` | latest checkpoint event | `review_required` after 60 minutes on active work |
| `accepted_artifact_count` | board/review/audit links | `info` unless zero after claimed design progress |
| `open_task_age` | runtime task create/update time | `review_required` if no recent checkpoint |

### Coordination

| Metric | Evidence | State Rule |
|---|---|---|
| `open_mailbox_count` | mailbox ledger when available | `needs_instrumentation` until mailbox checker exists |
| `open_dispatch_edge_count` | runtime edges/events when available | `review_required` if edge lacks closeout |
| `handoff_failure_count` | packet/router/validator findings | `review_required` if greater than 0 |
| `context_ack_gap_count` | context delta records and ack records | `blocked` for high-risk stale context without ack |
| `contradiction_open_count` | review packets and mailbox contradiction records | `review_required` if unresolved |

### Quality

| Metric | Evidence | State Rule |
|---|---|---|
| `evidence_gap_count` | audit map, review brief, result packets | `review_required` if a terminal claim has no path |
| `unsupported_claim_count` | forbidden claims section, packets, audit map | `rejected` if claimed as complete |
| `review_escape_count` | review results and retrospective records | `review_required` if any unresolved escape exists |
| `invalid_packet_count` | packet validator output or known packet findings | `review_required` if greater than 0 |
| `stale_context_result_count` | context delta checker output when available | `blocked` for high-risk work |

### Organization

| Metric | Evidence | State Rule |
|---|---|---|
| `active_stream_count` | task board phase items | `rejected` if WIP exceeds limit without exception |
| `fake_parallelism_count` | active lanes with no independent result | `review_required` if greater than 0 |
| `serial_collapse_count` | multi-lane task with one evidence source | `review_required` when broad parallel work is claimed |
| `idle_permanent_lane_count` | department registry plus packets | `info` unless lane was required by task charter |
| `topology_bloat_count` | task team plan versus evidence | `review_required` if extra conversations lack outputs |

### Safety And Reliability

| Metric | Evidence | State Rule |
|---|---|---|
| `blocked_time_without_packet` | blocker packets and runtime events | `blocked` after 10 minutes |
| `unsafe_retry_count` | repeated failed tool/auth/license events | `rejected` if greater than 0 |
| `transport_timeout_count` | transport summaries and runtime blockers | `review_required`; repeated timeout gates automation |
| `visibility_drift_count` | visibility checker output or drift records | `review_required` until repair/blocker evidence exists |
| `manual_action_duplicate_count` | blocker/user-ask packets | `blocked` if duplicate active asks exist |

## Data Classification

Every metric value must declare one of:

| Classification | Meaning |
|---|---|
| `measured` | directly computed from durable files |
| `derived` | computed from measured fields with named assumptions |
| `reported` | copied from an accepted packet or review artifact |
| `needs_instrumentation` | required data is not recorded yet |
| `not_applicable` | metric does not apply to this task phase |

The snapshot must not use chat memory as a data source. If the information only
exists in chat and not in task files, packets, runtime state, or accepted docs,
the metric is `needs_instrumentation`.

## Drift Detection Rules

| Drift | Detection |
|---|---|
| `goal_drift` | task summary/result packet mutates canonical goal |
| `context_drift` | result cites stale context or missing context hash |
| `evidence_drift` | artifact count increases but audit map remains partial |
| `scope_bloat` | new artifacts are not tied to any problem id or backlog item |
| `topology_bloat` | extra conversations have no independent packet/evidence |
| `research_loop` | external source notes lack adoption proposal and problem id |
| `implementation_before_gate` | files under runtime/tooling change without approved backlog item |
| `review_escape` | accepted result later needs correction due to missing evidence |

Drift can be informational, but any repeated drift with the same cause should
be at least `review_required`.

## Negative Drift Cases

`COAGENT-IMPL-NEXT-09` must include fixtures or test data for at least these
cases:

| Case | Expected State | Stable Code |
|---|---|---|
| active task with no checkpoint beyond threshold | `review_required` | `OMS_CHECKPOINT_STALE` |
| claimed completion while audit map still has partial requirements | `rejected` | `OMS_COMPLETION_OVERCLAIM` |
| high-risk context change without acknowledgement | `blocked` | `OMS_CONTEXT_ACK_MISSING` |
| transport timeout without blocker packet | `blocked` | `OMS_TIMEOUT_NO_BLOCKER` |
| WIP exceeds limit without explicit exception | `rejected` | `OMS_WIP_LIMIT_EXCEEDED` |
| external research artifact without problem id | `review_required` | `OMS_RESEARCH_UNMAPPED` |
| product/tool capability claim without evidence path | `rejected` | `OMS_UNSUPPORTED_CLAIM` |
| multi-lane task with only one evidence-producing lane | `review_required` | `OMS_FAKE_PARALLELISM` |
| required data source missing | `needs_instrumentation` | `OMS_DATA_MISSING` |

## Stable Finding Codes

| Code | Meaning |
|---|---|
| `OMS_DATA_MISSING` | required durable source missing |
| `OMS_CHECKPOINT_STALE` | checkpoint or critical-path evidence too old |
| `OMS_BLOCKER_MISSING` | blocked state lacks blocker packet |
| `OMS_TIMEOUT_NO_BLOCKER` | transport timeout lacks resumable blocker |
| `OMS_COMPLETION_OVERCLAIM` | completion claim contradicts audit evidence |
| `OMS_UNSUPPORTED_CLAIM` | product/tool/process claim lacks evidence |
| `OMS_CONTEXT_ACK_MISSING` | required context acknowledgement absent |
| `OMS_CONTEXT_STALE` | result or worker uses stale context |
| `OMS_INVALID_PACKET` | result packet is malformed or unsupported |
| `OMS_WIP_LIMIT_EXCEEDED` | active streams exceed board WIP limit |
| `OMS_FAKE_PARALLELISM` | split work produced no independent evidence |
| `OMS_SERIAL_COLLAPSE` | claimed multi-lane work collapsed into one lane |
| `OMS_RESEARCH_UNMAPPED` | research lacks problem id/adoption proposal |
| `OMS_VISIBILITY_DRIFT` | visible-thread metadata drift affects dispatch readiness |
| `OMS_UNSAFE_RETRY` | unsafe retry after auth/license/tool blocker |
| `OMS_DUPLICATE_MANUAL_ASK` | duplicate active user asks |

Codes are part of the test contract. Wording can change; codes should remain
stable unless the validator contract is versioned.

## Output JSON

The future checker should write:

```json
{
  "ok": false,
  "task_id": "COAGENT-ARCH-LONGRUN-01",
  "snapshot_time": "2026-05-30T05:30:00+08:00",
  "overall_state": "review_required",
  "metrics": [],
  "finding_codes": ["OMS_CHECKPOINT_STALE"],
  "findings": [
    {
      "code": "OMS_CHECKPOINT_STALE",
      "severity": "warning",
      "metric": "checkpoint_age",
      "evidence": ["Results/agent_runtime/events.jsonl"],
      "message": "active task has no recent checkpoint within threshold"
    }
  ],
  "needs_instrumentation": ["open_mailbox_count"],
  "evidence_files": [
    "CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/shared_task_board.md"
  ],
  "review_required": true,
  "blocked": false,
  "rejected": false,
  "next_action": "record checkpoint or justify cadence exception"
}
```

The Markdown output should be a compact review table, not a dashboard. It
should include:

- overall state;
- metric table grouped by category;
- findings by severity;
- evidence links;
- `needs_instrumentation` list;
- next safe action.

## Integration With Other Validators

The snapshot should consume outputs from other read-only validators when they
exist:

| Validator | Consumed Output |
|---|---|
| result packet validator | invalid packet, stale context, unsupported claim |
| context delta checker | context ack gaps, stale context use |
| handoff/workflow validator | handoff failures, missing closeout |
| mailbox ledger checker | open messages, ack gaps, contradictions |
| visibility drift gate | dispatch readiness and metadata drift |
| proof-package validators | candidate proof state and closeout status |

If those validators are not implemented, the snapshot must mark the relevant
metric as `needs_instrumentation` and cite the missing validator. It must not
pretend to have validated unavailable data.

## Implementation Boundary

The future implementation should live under CoAgent runtime or doctor code as a
read-only report generator. It may parse Markdown tables conservatively, but
should prefer structured runtime files, packet files, and validator JSON when
available.

Allowed implementation behavior:

- read project files;
- parse runtime events and packet files;
- emit JSON/Markdown reports under a user-approved output path;
- return non-zero when `strict` mode sees `blocked` or `rejected`;
- include deterministic fixture mode.

Forbidden implementation behavior:

- dispatch or resume conversations;
- edit task files as part of a check;
- auto-repair packets or context records;
- change runtime state;
- call external services;
- create notifications;
- run Git staging/commit/push.

## Acceptance For `COAGENT-IMPL-NEXT-09`

Implementation is acceptable only when:

1. a valid current long-running task produces a read-only JSON and Markdown
   snapshot;
2. missing data is reported as `needs_instrumentation`;
3. at least one negative drift fixture returns `review_required`;
4. at least one blocker fixture returns `blocked`;
5. at least one overclaim fixture returns `rejected`;
6. every finding cites a durable evidence path or missing data source;
7. no dashboard, scheduler, transport, conversation creation, or Git operation
   is introduced;
8. tests cover stable `OMS_*` finding codes.

## Current Consequence

For `COAGENT-ARCH-LONGRUN-01`, this design means the final 10-hour audit cannot
depend on the number of documents or conversations alone. The audit should ask
whether the runtime/task files prove:

- recent critical-path checkpointing;
- no hidden open dispatch edges;
- no stale context accepted as fresh;
- no completion overclaim;
- no unsupported product/tool capability claim;
- no unacknowledged safety or manual-intervention blocker;
- no fake parallelism or WIP bloat.

Until this snapshot is implemented, operating metrics remain a design contract,
not an executable health gate.
