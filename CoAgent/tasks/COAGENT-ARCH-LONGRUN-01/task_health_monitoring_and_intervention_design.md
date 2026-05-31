# COAGENT-ARCH-LONGRUN-01 Task Health Monitoring And Intervention Design

Date: 2026-05-30
Status: design draft for B58

## Purpose

This document defines the runtime operating playbook for a long-running
multi-conversation task after work has started.

Existing metric documents answer what should be measured. This document answers
what Dispatch, reviewers, and the PMO do when the measurements show drift,
stale context, fake parallelism, blocked work, unsafe retry, or closeout risk.

This is design only. It does not implement a scheduler, metrics checker,
transport repair, conversation creation, worktree creation, MCP call,
notification sender, Git operation, or automatic task mutation.

## Relationship To Existing Artifacts

| Artifact | Role |
|---|---|
| `operating_metrics_and_anti_drift_cadence.md` | metric names, cadence, and high-level drift states |
| `operating_metrics_snapshot_design.md` | future read-only snapshot checker contract and `OMS_*` findings |
| `early_drift_detection_experiment_design.md` | positive and negative fixtures that prove drift is catchable |
| `end_to_end_task_operating_runbook.md` | whole-task sequence from intake to closeout |
| `runbook_readiness_checker_design.md` | future readiness gate before dispatch, rehearsal, integration, or closeout |
| `real_task_execution_walkthroughs.md` | concrete PX4 and UE examples this playbook must handle |

The missing layer is intervention. A metric is useful only if it changes the
next action.

## Health State Model

Every active task and task-scoped conversation should be classified into one
of these states at each Dispatch board review or high-risk transition:

| State | Meaning | Allowed Next Action |
|---|---|---|
| `continue` | goal, context, evidence, blockers, and WIP are within bounds | continue current slice until next checkpoint |
| `continue_with_watch` | minor drift or missing instrumentation exists but does not endanger the next step | continue one checkpoint only; required watch item must be answered |
| `shrink_topology` | active conversations exceed useful parallelism or have no independent evidence | close or pause non-critical lanes and update workflow graph |
| `pause_for_context` | worker context is stale, unacknowledged, or contradicted | stop high-risk work until context delta is acknowledged |
| `pause_for_review` | output exists but evidence, claim boundary, or acceptance is unclear | route to Verification, Safety, DevOps, or PMO review |
| `block_for_user` | login, license, GUI, destructive approval, credential, manual visual review, or unavailable external action is required | write one blocker/human-review packet and ask PMO once |
| `block_for_safety` | unsafe retry, secret risk, external path, destructive action, or policy violation appears | stop affected work and route to Safety |
| `close_ready` | required outputs exist, review passed, integration disposition is known, and learning records are settled | run closeout audit and mark task slice closed |
| `reject_completion` | a completion claim conflicts with audit evidence or gated follow-ups | keep task active and write rejection finding |

The state is not a mood label. It must cite durable evidence, such as a
checkpoint, result packet, blocker packet, board row, context delta, workflow
graph, validator report, or audit-map entry.

## Intervention Decision Table

| Trigger | Minimum Evidence | State | Owner | Required Intervention |
|---|---|---|---|---|
| critical path has no evidence delta beyond cadence | latest checkpoint, board, runtime event | `pause_for_review` | DispatchAgent | require evidence delta, rescope slice, or close inactive lane |
| checkpoint repeats activity without advancing a requirement | checkpoint, goal audit map | `continue_with_watch` then `pause_for_review` on repeat | VerificationAgent | record `no_delta` watch item; reject repeated busy-work checkpoint |
| worker goal weakens canonical goal | task charter, packet goal restatement | `pause_for_review` or `reject_completion` | DispatchAgent + MainAgent | rewrite scoped objective or recreate invalid goal before further dispatch |
| context delta exists without required acknowledgement | context delta, ack record, risk class | `pause_for_context` | ContextMemoryAgent | stop high-risk work; request ack and resume condition |
| worker cites stale/rejected assumption | context pack, result packet, rejected decision record | `pause_for_context` | ContextMemoryAgent + VerificationAgent | issue contradiction record and require corrected result |
| multiple active lanes produce no independent outputs | board, packets, workflow graph | `shrink_topology` | DispatchAgent | close, merge, or pause lanes; update WIP and graph |
| supposed parallel task is executed by one lane | board, packet provenance | `pause_for_review` | DispatchAgent + VerificationAgent | reclassify as single-lane or require bounded independent review |
| mailbox message is open past age limit | mailbox ledger, message age | `pause_for_review` | DispatchAgent | nudge owner once; then close as blocker or contradiction |
| contradiction remains unresolved | contradiction record, competing packets | `pause_for_review` | VerificationAgent | appoint reviewer, decide accepted/rejected/deferred, update context |
| blocker appears without blocker packet | error log, tool result, runtime state | `block_for_user` or `block_for_safety` | SafetyComplianceAgent | write blocker packet before any retry |
| same auth/license/tool failure is retried | blocker history, tool logs | `block_for_safety` | SafetyComplianceAgent | stop retry loop; request one PMO action or downgrade route |
| tool capability card is missing or stale | capability card index, route claim | `pause_for_review` | ToolchainMCPAgent | refresh card, downgrade claim, or write route blocker |
| Git surface is broad, slow, locked, or conflicting | Git inventory, status/diff evidence | `pause_for_review` | DevOpsReleaseAgent | create integration plan or route to Git-heavy proof path |
| result packet has unsupported status or shape | result packet, router/checker finding | `pause_for_review` | RuntimePlatformAgent + VerificationAgent | repair packet or convert to blocker; do not treat as accepted evidence |
| accepted result waits too long for integration | accepted packet, integration queue | `pause_for_review` | DevOpsReleaseAgent | choose merge, hold, reject, or split integration |
| review discovers missing required evidence | review packet, evidence label report | `pause_for_review` | VerificationAgent | downgrade claim and update audit map |
| completion is claimed while audit map has gaps | final audit, goal map | `reject_completion` | MainAgent + VerificationAgent | keep goal active and list exact remaining gates |
| all required outputs and reviews are settled | review packets, Git disposition, context updates | `close_ready` | DispatchAgent + MainAgent | run closeout audit and retrospective trigger scan |

## Board Review Procedure

At each board review, Dispatch should update a task-health section with:

```yaml
task_health:
  task_id: COAGENT-ARCH-LONGRUN-01
  health_state: pause_for_review
  critical_path_owner: DispatchAgent
  critical_path_evidence:
    - CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/task_health_monitoring_and_intervention_design.md
  checkpoint_age_minutes: measured_or_unknown
  context_state: fresh | stale | needs_ack | unknown
  mailbox_state: clear | open | aged | contradiction | unknown
  blocker_state: none | packeted | missing | unsafe_retry
  topology_state: minimal | bloated | fake_parallelism | serial_collapse
  review_state: not_ready | ready | accepted | rejected | needs_user
  intervention:
    decision: continue | continue_with_watch | shrink_topology | pause_for_context | pause_for_review | block_for_user | block_for_safety | close_ready | reject_completion
    owner: VerificationAgent
    due: next_checkpoint
    required_evidence: "one accepted review packet or updated audit-map row"
```

This can initially be written manually into the board or a checkpoint packet.
Future implementation can generate it from the operating metrics snapshot.

## Critical Path Rule

Every active long task must name one current critical-path owner.

Rules:

- If no owner is named, Dispatch owns the critical path by default.
- If the owner has no evidence delta within the cadence, the state becomes
  `pause_for_review`.
- If another lane is making useful progress but cannot affect the next
  acceptance decision, it is supporting work, not the critical path.
- If the critical path requires a user/manual/tool action, it must become a
  blocker or human-review packet, not a silent wait.

This prevents a long task from hiding behind unrelated parallel activity.

## Topology Intervention Rules

Multi-conversation topology must be adjusted during execution:

| Condition | Decision |
|---|---|
| one lane can safely finish the next evidence step | keep single lane |
| two lanes need independent judgment or disjoint write sets | keep both lanes |
| three or more lanes are active but only one has evidence | shrink topology |
| a lane is blocked by tool/auth/manual review but another lane can progress safely | keep safe parallel lane, packet the blocker |
| two lanes disagree on a fact that affects acceptance | pause dependent work and route contradiction review |
| a permanent lane is not needed for the current task phase | keep dormant; do not invent work |

The goal is not fewer departments. The goal is the smallest topology that
advances the user task without losing needed independence.

## Human Intervention Rule

When a blocker needs the user, CoAgent should produce one PMO-facing ask:

```text
Need: exact action required
Why: task impact and evidence path
Scope: affected task slice only
Safe parallel work: what can continue without the user action
Resume check: exact command, file, or observation required after user action
Forbidden: retries, secret requests, broad GUI/file actions not needed now
```

If two conversations would ask the same user action, Dispatch deduplicates and
keeps one active blocker packet.

## PX4 Parameter Identification Application

For a PX4/Sunray150 parameter-identification task, task health is evaluated as:

| Phase | Healthy State | Drift Or Blocker |
|---|---|---|
| log intake | log availability, sampling, channels, units, and flight modes are recorded | paper-reading starts before data sufficiency |
| identifiability | each requested parameter has signal support, uncertainty, and residual plan | claim says "parameters solved" without identifiability matrix |
| estimator design | estimator inputs and non-identifiable parameters are separated | estimator tunes parameters that data cannot support |
| simulation tuning | offline/MWORKS evidence labels are separated | offline demo is reported as MWORKS proof |
| manual/license interruption | blocker packet has exact login or activation ask | repeated simulation retry after activation loss |
| closeout | uncertainty, unsupported parameters, tuning backlog, and report evidence are recorded | completion ignores parameters that require simulation tuning |

The default intervention for unmapped research is `pause_for_review`: the lane
must map source material to one identifiability, estimator, validation, or
blocker decision.

## UE Scene Truth Application

For a UE/Fab/local scene-truth task, task health is evaluated as:

| Phase | Healthy State | Drift Or Blocker |
|---|---|---|
| source gate | asset source, engine version, local/Fab/manual path, and license boundary are known | Fab visibility is treated as import capability |
| capability card | UE/MCP route health and allowed probes are current | stale MCP status is used for map mutation |
| truth export | collision/navmesh/occupancy/SDF outputs have manifest entries | screenshot or rendering is used as planning truth |
| planning readiness | consumer algorithm gets coordinate frame, scale, and completeness checks | visual review is accepted without geometry truth |
| manual import | one PMO ask says what to import and where | repeated attempts to automate Launcher/Fab without evidence |
| Git disposition | large assets are ignored/LFS/planned before staging | broad add of scene tree or generated artifacts |

The default intervention for missing or stale tool capability is
`pause_for_review` or `block_for_user`, not continued product work.

## Completion Gate Interaction

`close_ready` requires all of:

- canonical goal unchanged;
- current critical path has accepted evidence;
- required context deltas are acknowledged or explicitly deferred;
- open mailbox items are closed, blocked, or deferred with owner;
- blockers have packeted resume state or are accepted as gated follow-ups;
- review, safety, and Git disposition are recorded when applicable;
- learning/retrospective triggers are evaluated;
- final audit does not contain contradictory `weak evidence` or
  `forbidden claim` entries.

If any item is missing, the task may still be healthy, but it is not
completion-ready.

## Future Implementation Boundary

A later implementation can add a read-only task-health snapshot or board
updater after the shared validator envelope and operating metrics snapshot
exist.

Future implementation must stay read-only unless separately approved. It
should not dispatch conversations, create worktrees, repair Codex state,
send notifications, call MCP tools, stage Git, or rewrite task documents
without explicit implementation approval.

Potential future backlog item:

```text
COAGENT-IMPL-NEXT-32
Task health intervention checker: read durable task state and emit the
recommended intervention decision with evidence, owner, and next safe action.
```

## Current Consequence For COAGENT-ARCH-LONGRUN-01

For the active long-run architecture task, this playbook means:

- the task remains active until final audit evidence supports closure;
- document volume or elapsed time cannot be used as the health signal;
- the current critical path is design coverage plus final audit readiness;
- Candidate A, PX4, UE, Git-heavy, and auth/license proof execution remain
  gated follow-ups, not current completion evidence;
- any future visible-conversation dispatch should pass visibility, context,
  packet, blocker, and task-health preflight first.
