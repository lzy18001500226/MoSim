# COAGENT-ARCH-LONGRUN-01 Mailbox Ledger And Replay Design

Date: 2026-05-30
Status: design contract for durable cross-conversation communication

## Purpose

CoAgent's conversations must communicate through durable artifacts instead of
hidden chat, raw transcript forwarding, or ad-hoc human memory. The existing
communication protocol defines allowed packet types and mailbox rules. This
document defines the missing mailbox ledger: how messages are stored, tracked,
acknowledged, retried, replayed, closed, and audited.

This is a design artifact. It does not implement app-server transport,
automatic conversation creation, or unattended dispatch.

## Core Rule

```text
if a message changes work state, it must be in the mailbox ledger
```

Raw chat can inspire a message, but it is not the message. A department or
task-scoped conversation may act only on messages that can be recovered from
project-owned files.

## Ledger Storage Model

Future implementation should use project-owned files first:

```text
CoAgent/mailbox/tasks/<task_id>/messages/<message_id>.yaml
CoAgent/mailbox/tasks/<task_id>/events.jsonl
CoAgent/mailbox/tasks/<task_id>/acks/<message_id>-<receiver>.yaml
CoAgent/mailbox/tasks/<task_id>/replay/<timestamp>.md
```

A SQLite or app-server transport may be added later only after the file ledger
passes Candidate A style proof.

## Message Identifier

Format:

```text
MSG-<task_id>-<sequence>-<short_type>
```

Examples:

- `MSG-COAGENT-PROOF-CANDIDATE-A-001-task-packet`
- `MSG-COAGENT-PROOF-CANDIDATE-A-004-review-request`
- `MSG-COAGENT-ARCH-LONGRUN-01-009-context-refresh`

The sequence is task-local and monotonic. DispatchAgent owns allocation.

## Required Message Fields

| Field | Required | Meaning |
|---|---|---|
| `message_id` | yes | stable id |
| `task_id` | yes | durable task id |
| `message_type` | yes | allowed type from communication protocol |
| `sender` | yes | department/conversation creating message |
| `receivers` | yes | one or more target departments/conversations |
| `created_at` | yes | timestamp |
| `context_pack_id` | conditional | required for task/context/review/result-sensitive messages |
| `context_hash` | conditional | required when context pack exists |
| `requires_ack` | yes | whether receiver must acknowledge |
| `ack_deadline` | optional | review/dispatch expectation |
| `expected_response_type` | optional | result, review, blocker, ack, closeout |
| `payload_path` | yes | path to task packet, blocker, result, or review artifact |
| `evidence_paths` | yes | source evidence used by message |
| `status` | yes | ledger message state |
| `dedupe_key` | optional | prevents repeated blocker/user prompts |
| `supersedes` | optional | message ids replaced by this message |
| `blocked_by` | optional | blocker ids preventing action |
| `review_owner` | conditional | required for mutable, risky, or closing messages |
| `close_condition` | conditional | required for task packet and closeout |

## Allowed Message Types

The ledger uses the communication protocol vocabulary:

- `task_packet`
- `context_refresh`
- `checkpoint`
- `blocker`
- `decision_required`
- `review_request`
- `integration_request`
- `result_packet`
- `closeout`

Future types require a protocol update and validator fixture.

## Message State Machine

| State | Meaning | Allowed Next |
|---|---|---|
| `draft` | message exists but not dispatchable | `queued`, `canceled` |
| `queued` | ready for receiver | `sent`, `superseded`, `canceled` |
| `sent` | delivered or placed for receiver | `acknowledged`, `timed_out`, `blocked`, `superseded` |
| `acknowledged` | receiver confirmed receipt/context | `responded`, `blocked`, `closed` |
| `responded` | expected response artifact exists | `reviewed`, `closed`, `rework_required` |
| `reviewed` | review packet accepted/rejected/rework | `closed`, `rework_required`, `blocked` |
| `rework_required` | receiver or reviewer must repair | `queued`, `superseded`, `blocked` |
| `timed_out` | ack/response missing after budget | `blocked`, `queued` after approved retry |
| `blocked` | blocker packet controls resume | `queued` after resume condition, `canceled` |
| `superseded` | replaced by newer message | terminal |
| `canceled` | no longer valid | terminal |
| `closed` | no response required or accepted response complete | terminal |

No message may jump from `sent` to `closed` when `requires_ack=true`.

## Ack Record

Required fields:

```yaml
ack_id:
message_id:
task_id:
receiver:
acknowledged_at:
acknowledged_by:
context_pack_id:
context_hash:
ack_status: accepted | stale_context | unsupported_message | blocked
notes:
```

If `ack_status=stale_context`, the receiver must not proceed. Dispatch sends a
`context_refresh` or records a blocker.

## Replay Contract

A replay must reconstruct:

1. current canonical goal;
2. open messages;
3. blocked messages and blockers;
4. required acknowledgements;
5. expected result/review/integration packets;
6. superseded or canceled messages;
7. unresolved contradictions;
8. next safe action.

Replay output should be human-readable and source-linked:

```text
CoAgent/mailbox/tasks/<task_id>/replay/<timestamp>.md
```

Replay is not allowed to infer hidden state from chat. If an expected response
does not exist as a file or runtime event, replay marks it missing.

## Timeout And Retry Rules

- one timeout creates a `transport_timeout` or mailbox timeout blocker;
- retry requires a changed condition, such as repaired visibility, packet
  template fix, or explicit timeout class change;
- duplicate blockers use the same `dedupe_key`;
- no `retry_forever`;
- repeated timeout across the same receiver and message type should escalate to
  RuntimePlatformAgent and VerificationAgent review.

## Contradiction Handling

When two messages conflict:

1. mark both messages `review_required`;
2. create a `review_request` message;
3. freeze affected downstream messages if continuing could corrupt work;
4. reviewer records accepted resolution;
5. ContextMemoryAgent publishes context delta if assumptions changed;
6. supersede or close the losing message with evidence.

Contradiction resolution must not edit history. It appends review and
supersession records.

## Closeout Rules

A task-scoped conversation can close only when:

- all messages it owns are `closed`, `superseded`, `canceled`, or `blocked`
  with accepted deferral;
- all required result/review packets exist;
- no open message expects that conversation to respond;
- context deltas from its work are either accepted or rejected;
- integration and knowledge-promotion messages are routed if needed.

## Recovery Rules

After session loss or context compaction:

1. load task state from `mosim_agent_runtime.py show`;
2. load mailbox replay for the task;
3. load open blocker packets;
4. inspect result/review packets only for open or latest messages;
5. resume from the next safe action.

Do not search chat history first. Chat can be used only to locate missing files
after the ledger and runtime state have been checked.

## Future Implementation Slice

Add a later implementation item:

```text
COAGENT-IMPL-NEXT-23: Mailbox Ledger And Replay Checker
```

Scope:

- define message, ack, and replay schemas;
- add a read-only validator for required fields, state transitions, duplicate
  dedupe keys, missing ack, missing expected response, and forbidden message
  types;
- add a replay generator for one task from mailbox files plus runtime state;
- add fixtures for normal result flow, timeout, stale context, contradiction,
  duplicate blocker, and closeout.

Acceptance:

- a valid Candidate A mailbox chain replays to one next safe action;
- missing ack fails when `requires_ack=true`;
- contradictory result messages create review-required state;
- duplicate blocker dedupe keys do not create repeated user asks;
- closed task with open expected response fails;
- no app-server transport, automatic conversation creation, or message delivery
  is implemented.

## Open Questions

- Whether mailbox storage stays YAML/JSONL or moves to SQLite should be decided
  after the file-ledger proof.
- Some Codex App features may later expose native conversation events, but they
  must not replace the project-owned ledger as source of truth.
- Message volume must be measured. If the ledger becomes noisy, add compaction
  through replay summaries rather than deleting original messages.
