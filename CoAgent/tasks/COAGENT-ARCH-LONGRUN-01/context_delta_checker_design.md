# COAGENT-ARCH-LONGRUN-01 Context Delta Checker Design

Date: 2026-05-30
Status: design contract for `COAGENT-IMPL-NEXT-02`

## Purpose

Context drift is one of the main failure modes for long-running
multi-conversation work. A new conversation can be visible and still act on
stale assumptions if context deltas, acknowledgements, and pause/resume state
are not machine-checkable.

This document defines the later read-only checker for context deltas and
acknowledgements. It does not change runtime schemas, generate context packs,
dispatch conversations, or approve automatic resume.

## Core Rule

```text
high-risk work cannot resume from stale context without an acknowledgement
record proving the affected conversation saw the new context version
```

A context delta is durable only when it names what changed, what it supersedes,
who is affected, whether acknowledgement is required, and what condition allows
resume.

## Inputs

Future command shape:

```bash
python3 CoAgent/validators/context_delta_checker.py \
  --task-id COAGENT-ARCH-LONGRUN-01 \
  --context-delta CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/examples/context_delta.yaml \
  --context-pack CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/context_pack.md \
  --ack-dir CoAgent/context/acks/COAGENT-ARCH-LONGRUN-01 \
  --mode pre_resume \
  --json-output Results/coagent_validators/context_delta_check.json
```

Modes:

- `delta_only`: validate one context delta file;
- `ack_only`: validate acknowledgement records for one delta;
- `pre_resume`: decide whether an affected slice may resume;
- `post_result`: validate that a result packet cites a current context;
- `fixture`: run positive/negative fixtures against stable finding codes.

The checker is read-only except for optional JSON report output.

## Required Delta Fields

The current template already has some fields. The future checker should require
the stricter lifecycle fields below before high-risk dispatch or resume:

| Field | Required | Meaning |
|---|---|---|
| `context_delta_id` | yes | stable id |
| `task_id` | yes | owning task |
| `source_result_packet` | conditional | packet that produced the delta |
| `created_by` | yes | authoring owner |
| `created_at` | yes | timestamp |
| `context_pack_id` | yes | affected context pack id |
| `context_pack_version_or_hash` | yes | version/hash before or after change |
| `change_type` or `delta_type` | yes | fact, decision, interface, blocker, evidence, stale notice, lesson |
| `changed_fact_or_decision` or `summary` | yes | human-readable change |
| `supersedes` | yes | prior facts, docs, packets, or assumptions superseded |
| `affected_slices` | yes | task slices affected |
| `affected_departments` or `applies_to.conversations` | yes | target conversations/departments |
| `acknowledgement_required` | yes | whether receivers must ack |
| `acknowledgement_state` | yes | `not_required`, `pending`, `partial`, `complete`, or `blocked` |
| `pause_until_refresh` | yes | whether affected work must pause |
| `reviewer` or `review.review_owner` | yes | owner who accepts the delta |
| `resume_condition` | yes | exact condition for affected work to continue |
| `evidence_paths` | yes | source evidence |

The checker may accept current-template aliases only if it emits normalized
fields in its JSON report. For example, `delta_type` can map to `change_type`,
and `applies_to.conversations` can map to `affected_departments`.

## Required Ack Fields

Acknowledgement records should contain:

| Field | Required | Meaning |
|---|---|---|
| `ack_id` | yes | stable id |
| `context_delta_id` | yes | delta acknowledged |
| `task_id` | yes | owning task |
| `department` | yes | acknowledging department |
| `conversation_or_worker_id` | yes | conversation or worker id |
| `acknowledged_context_pack_version_or_hash` | yes | version/hash seen |
| `acknowledged_at` | yes | timestamp |
| `acknowledged_by` | yes | actor |
| `resume_allowed` | yes | boolean |
| `resume_reason` | yes | why resume is or is not safe |

## State Model

| State | Meaning |
|---|---|
| `fresh` | no open delta affects the slice |
| `stale` | delta affects slice and acknowledgement is required |
| `paused_for_refresh` | affected work must not continue |
| `ack_pending` | at least one receiver has not acknowledged |
| `ack_complete` | all required acknowledgements exist |
| `blocked` | resume condition is not met |
| `superseded` | a newer context pack replaces this one |

State is derived from files. The checker must not infer acknowledgement from
raw chat.

## Pre-Resume Checks

Reject resume when:

- context delta is missing required lifecycle fields;
- `pause_until_refresh=true` and acknowledgement is missing;
- `acknowledgement_required=true` and `acknowledgement_state` is not
  `complete` or `not_required`;
- an affected department lacks an ack record;
- ack context hash does not match the required context hash;
- resume condition is empty;
- reviewer is missing;
- delta supersedes the result packet's cited context;
- high-risk work claims `resume_allowed=true` without evidence paths.

High-risk work includes:

- tool/MCP execution;
- UE/MWORKS/Fab work;
- Git staging, merge, delete, move, or large import;
- auth/license/manual-review recovery;
- product proof B/C/D/E;
- any live multi-conversation dispatch after a context-changing decision.

## Post-Result Checks

Reject or require review when:

- result packet cites a superseded context pack;
- result packet omits context pack id/hash where the task packet required one;
- result packet proposes a context delta but no delta file exists;
- context delta changes shared assumptions without review owner;
- context delta is accepted but affected conversations are not named;
- accepted lesson is promoted from a draft, rejected, or superseded context.

## Output JSON

Required report shape:

```json
{
  "ok": false,
  "decision": "blocked_resume",
  "mode": "pre_resume",
  "task_id": "COAGENT-ARCH-LONGRUN-01",
  "context_delta_id": "CTXD-001",
  "normalized": {
    "acknowledgement_required": true,
    "affected_departments": ["ContextMemoryAgent"]
  },
  "finding_codes": ["CTX_ACK_MISSING"],
  "findings": [
    {
      "code": "CTX_ACK_MISSING",
      "severity": "error",
      "path": "acks/CTXD-001-ContextMemoryAgent.yaml",
      "message": "affected department has no acknowledgement record"
    }
  ],
  "resume_allowed": false,
  "next_action": "write acknowledgement or send context_refresh blocker"
}
```

Decisions:

- `pass`;
- `pass_with_warnings`;
- `blocked_resume`;
- `needs_review`;
- `reject_delta`;
- `reject_ack`;
- `needs_dependency`.

## Stable Finding Codes

| Code | Meaning |
|---|---|
| `CTX_DELTA_MISSING_FIELD` | required delta field absent |
| `CTX_DELTA_BAD_TASK` | task id mismatch |
| `CTX_DELTA_NO_CHANGE` | no changed fact/decision/summary |
| `CTX_SUPERSEDES_MISSING` | superseded source not named |
| `CTX_AFFECTED_SLICE_MISSING` | affected slice/dept/conversation absent |
| `CTX_ACK_REQUIRED_STATE_BAD` | ack required but state not pending/partial/complete/blocked |
| `CTX_ACK_MISSING` | required ack record absent |
| `CTX_ACK_HASH_MISMATCH` | ack hash does not match required context |
| `CTX_PAUSE_WITHOUT_RESUME` | pause set but resume condition missing |
| `CTX_REVIEWER_MISSING` | reviewer absent |
| `CTX_EVIDENCE_MISSING` | evidence paths absent |
| `CTX_RESULT_STALE_CONTEXT` | result cites superseded context |
| `CTX_PROMOTION_FROM_STALE` | knowledge promotion uses stale/draft/rejected context |
| `CTX_RAW_TRANSCRIPT_CONTEXT` | raw transcript used as context evidence |
| `CTX_SECRET_OR_PRIVATE_PATH` | secret/private path included |

## Fixture Matrix

Positive fixtures:

| Fixture | Expected |
|---|---|
| valid no-ack delta | `pass` |
| valid ack-required delta with complete ack records | `pass` |
| valid stale-context blocker | `pass_with_warnings` |

Negative fixtures:

| Fixture | Expected Codes |
|---|---|
| missing context pack hash | `CTX_DELTA_MISSING_FIELD` |
| no changed fact or decision | `CTX_DELTA_NO_CHANGE` |
| supersedes omitted | `CTX_SUPERSEDES_MISSING` |
| affected conversations omitted | `CTX_AFFECTED_SLICE_MISSING` |
| ack required but no ack file | `CTX_ACK_MISSING` |
| ack hash mismatch | `CTX_ACK_HASH_MISMATCH` |
| pause without resume condition | `CTX_PAUSE_WITHOUT_RESUME` |
| missing reviewer | `CTX_REVIEWER_MISSING` |
| result cites superseded context | `CTX_RESULT_STALE_CONTEXT` |
| promotion from stale context | `CTX_PROMOTION_FROM_STALE` |

## Integration Points

- Candidate A post-dispatch requires this checker for the required context
  delta and acknowledgement state.
- `context_index_and_assembly_design.md` should use checker output to decide
  whether a context pack is fresh, stale, or blocked.
- `mailbox_ledger_and_replay_design.md` should record context-refresh and ack
  messages as mailbox events.
- `handoff_workflow_validator_design.md` should reject high-risk resume when
  this checker returns `blocked_resume`.

## Implementation Boundary

The later implementation slice may add:

- read-only checker script;
- tiny context-delta and ack fixtures;
- tests for stable finding codes;
- optional JSON report output.

It may not add:

- automatic context generation;
- automatic dispatch or resume;
- conversation creation;
- app-server transport;
- runtime schema migration;
- vector search;
- tool/MCP calls;
- Git staging or commits.

## Design Decision

The existing context delta template is not enough by itself for long-running
multi-conversation safety. `COAGENT-IMPL-NEXT-02` should first implement a
read-only checker and fixture suite so stale-context resume failures become
machine-detectable before live proof or product automation expands.
