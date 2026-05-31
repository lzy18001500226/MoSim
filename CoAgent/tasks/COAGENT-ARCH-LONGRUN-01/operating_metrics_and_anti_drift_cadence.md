# COAGENT-ARCH-LONGRUN-01 Operating Metrics And Anti-Drift Cadence

Date: 2026-05-30
Status: design draft

## Purpose

Long-running multi-conversation tasks can look busy while drifting away from
the user goal. This document defines the operating rhythm and metrics that
should detect the drift early enough to stop or correct the task.

This is design only. It does not implement dashboards, schedulers, automatic
conversation creation, or app-server transport.

## Control Principle

Every long-running task needs three feedback loops:

```text
fast local loop: worker checkpoint
medium coordination loop: Dispatch board review
slow learning loop: retrospective and knowledge promotion
```

If all three loops are missing, the system will rely on chat memory and late
human review, which is exactly the failure mode CoAgent is meant to avoid.

## Cadence Defaults

| Loop | Default cadence | Owner | Output |
|---|---:|---|---|
| worker checkpoint | every 30-60 minutes or before risky transition | scoped conversation owner | checkpoint packet |
| blocker escalation | within 10 minutes of confirmed blocker | blocked worker + Dispatch | blocker packet |
| context refresh | immediately after accepted cross-slice decision | ContextMemoryAgent | context delta and acknowledgement request |
| board review | every 60-90 minutes for active long task | DispatchAgent | shared task board update |
| review gate | before acceptance or merge | Verification/Safety/DevOps as applicable | review packet |
| integration queue review | after each accepted result packet | DevOpsReleaseAgent | integration packet or merge blocker |
| retrospective scan | after task close or repeated failure | KnowledgeSecretaryAgent + Continuous Improvement host | promotion/rejection record |

The cadence should shorten when risk, uncertainty, Git surface, tool fragility,
or context churn increases.

## Required Metrics

### Progress Metrics

| Metric | Meaning | Initial threshold |
|---|---|---|
| `critical_path_age` | time since critical-path owner last produced evidence | review after 60 minutes |
| `checkpoint_age` | time since a worker checkpoint | review after 60 minutes |
| `accepted_artifact_count` | artifacts accepted by review gate | should increase across phases |
| `integration_queue_age` | accepted result waiting for integration | review after one checkpoint |

### Coordination Metrics

| Metric | Meaning | Initial threshold |
|---|---|---|
| `open_mailbox_count` | unresolved cross-conversation messages | review if more than WIP limit |
| `handoff_failure_count` | missing, invalid, or ambiguous handoff packets | review if greater than 0; fail if repeated twice |
| `context_refresh_latency` | delay between context delta and acknowledgement | fail if high-risk work resumes before ack |
| `contradiction_open_age` | unresolved conflicting outputs | review after 30 minutes |

### Quality Metrics

| Metric | Meaning | Initial threshold |
|---|---|---|
| `evidence_gap_count` | claims without direct evidence path | review if greater than 0 |
| `review_escape_count` | issue discovered after acceptance | fail if caused by missing required evidence |
| `rework_count` | repeated work caused by bad assumption or drift | review if same cause repeats |
| `unsupported_claim_count` | product/tool claim not proven by accepted evidence | reject relevant claim |

### Organization Metrics

| Metric | Meaning | Initial threshold |
|---|---|---|
| `fake_parallelism_count` | split that produced no independent result | review if greater than 0 |
| `serial_collapse_count` | supposed team work executed by one lane | review if multi-lane task has one result source |
| `wip_over_limit_count` | active streams exceed board limit | fail task-shaping gate until reduced |
| `idle_permanent_lane_count` | permanent lane never produces useful packet | candidate for hosted/demotion review |

### Safety And Reliability Metrics

| Metric | Meaning | Initial threshold |
|---|---|---|
| `blocked_time_without_packet` | time blocked without blocker packet | fail after 10 minutes |
| `unsafe_retry_count` | repeated retry after auth/license/tool failure | fail if greater than 0 |
| `transport_timeout_count` | visible conversation dispatch misses result budget | review each occurrence; gate automation after repeat |
| `manual_action_duplicate_count` | multiple agents ask user for same action | fail operator-experience gate |

## Anti-Drift Checks

Each checkpoint packet must answer:

1. Is the canonical task goal still unchanged?
2. Which evidence was produced since the last checkpoint?
3. Which assumption could invalidate current work?
4. Does any context delta need acknowledgement?
5. Is the current topology still the smallest useful topology?
6. Is the task blocked, continuing, or ready for review?

If a worker cannot answer these, Dispatch must pause or rescope that slice.

## Drift States

| State | Meaning | Required response |
|---|---|---|
| `goal_drift_suspected` | worker goal no longer matches charter | decision_required packet |
| `context_stale` | worker is using superseded context | pause and require context acknowledgement |
| `evidence_drift` | output no longer proves the claim | Verification review packet |
| `scope_bloat` | task accumulates unrelated work | PMO/Dispatch rescope |
| `topology_bloat` | too many conversations for actual parallelism | Dispatch shrink decision |
| `research_loop` | external research is not mapping to decisions | External Intelligence stop/reframe |
| `implementation_before_gate` | worker starts gated implementation | Safety/Dispatch block |

## Board Review Questions

Dispatch board review should ask:

1. What is the current critical path?
2. Which conversations are active, blocked, review-ready, or closable?
3. Which result packets are waiting for review?
4. Which accepted outputs are waiting for integration?
5. Which context deltas require acknowledgement?
6. Which blockers require one user-facing ask?
7. Has any conversation exceeded checkpoint cadence?
8. Should the team spawn, shrink, merge, or stop?

The board review is not a meeting transcript. It updates the task state.

## Escalation Rules

Escalate to PMO/user when:

- canonical goal change is proposed;
- required input, login, license, manual GUI review, or destructive approval is
  needed;
- a task exceeds appetite and no evidence justifies continuation;
- the same blocker repeats across three goal turns;
- review rejects a core assumption that changes project direction.

Escalate to Safety when:

- a path, secret, account, license, destructive action, or GUI/MCP policy risk
  appears.

Escalate to DevOps when:

- write scopes overlap;
- Git status is too slow/noisy for main thread;
- broad rename/import/large asset risk appears;
- accepted work waits in the integration queue.

Escalate to Verification when:

- a claim lacks evidence;
- product correctness and process evidence are mixed;
- a result packet is malformed;
- a contradiction affects acceptance.

## Retrospective Triggers

Create a retrospective action if any of these happens:

- invalid packet format recurs;
- context stale acknowledgement is missing;
- a visible conversation transport times out repeatedly;
- a manual-intervention ask is duplicated;
- a worker continues after a known blocker;
- a review escape would have been caught by a template/check;
- a task produces useful research but no decision mapping.

Retrospective action must land in one of:

- implementation backlog;
- doctor check;
- protocol template;
- workflow doc;
- skill update;
- hook/preflight proposal;
- rejected-idea archive.

## Minimal Implementation Later

When approved, the smallest implementation slice is a read-only metrics
snapshot:

```text
task events + shared task board + result packets
  -> metrics JSON/Markdown
  -> verification gate decision
```

It should not require app-server transport, automatic scheduling, dashboard UI,
or automatic conversation creation.

## Current Consequence For COAGENT-ARCH-LONGRUN-01

The current long-run architecture task should be judged by whether it produces
recoverable design artifacts and updates the problem matrix. It should not be
judged by the number of conversations opened or the amount of prose written.

Known current evidence:

- department result packets exposed packet-format and transport reliability
  failures;
- context lifecycle fields were added because stale context was still
  procedural;
- verification thresholds exist but still need executable negative tests;
- operating metrics need a future read-only snapshot implementation.
