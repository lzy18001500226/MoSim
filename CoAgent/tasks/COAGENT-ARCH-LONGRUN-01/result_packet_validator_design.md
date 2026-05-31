# COAGENT-ARCH-LONGRUN-01 Result Packet Validator Design

Date: 2026-05-30
Status: design contract for `COAGENT-IMPL-NEXT-11`

## Purpose

Visible department conversations have already produced useful findings in
packet shapes that the router rejected. That turns real work into fragile
manual repair. This document defines the validator that should exist before
CoAgent spends more transport budget on multi-conversation proof work.

This is a design artifact. It does not implement the validator, change the
router, create conversations, dispatch work, or modify runtime transport.

## Core Rule

```text
no result packet is durable until it passes the result-packet validator
```

A useful prose answer is not a result packet. A result packet must be
machine-checkable, router-compatible, and safe to use as downstream context.

## Inputs

The future validator should accept:

```text
--packet-path <path>
--task-id <expected task id>
--expected-owner <optional department/conversation>
--expected-context-hash <optional hash>
--mode strict|review
--json-output <optional path>
```

`strict` is for dispatch closeout and automated import. `review` may allow
minor warnings but must still reject unsupported statuses, nested packet
objects, missing evidence, or canonical goal mutation.

## Required Fields

| Field | Required | Validation |
|---|---|---|
| `task_id` | yes | equals expected task id |
| `status` | yes | one of the router-compatible statuses |
| `canonical_status` | yes | one of the router-compatible statuses |
| `task_class` | yes | known task class |
| `summary` | yes | non-empty, single paragraph |
| `owner` | yes | department or worker identity |
| `role` | yes | role used for this task |
| `read_scope` | yes | JSON array |
| `write_scope` | yes | JSON array |
| `files_changed` | yes | JSON array, may be empty |
| `commands_run` | yes | JSON array, may be empty |
| `evidence` | yes | non-empty JSON array for terminal statuses |
| `risks` | yes | JSON array |
| `blockers` | yes | JSON array |
| `review_status` | yes | known review status |
| `acceptance_state` | yes | known acceptance state |
| `continue_or_stop` | yes | `continue` or `stop` |
| `next_recommended_action` | yes | non-empty |
| `events` | yes | JSON array, may be empty |

Conditional fields:

- `context_pack_id` and `context_hash` are required when the task packet
  provided a context pack.
- `review_owner` is required when `review_status` is `pending`,
  `needs_review`, or `rejected`.
- `blocker_type` is required when `status=blocked`.
- `repair_note` is required when a MainAgent repair converts an invalid packet
  into a router-compatible packet.

## Allowed Values

Terminal statuses:

- `completed`
- `review_required`
- `blocked`
- `failed`
- `canceled`
- `rejected`
- `superseded`

Review status:

- `not_required`
- `pending`
- `accepted`
- `needs_review`
- `rejected`

Acceptance state:

- `met`
- `partially_met`
- `not_met`
- `unknown`

Unsupported values must fail, not warn. Conditional completion is represented
with:

```text
status: completed
canonical_status: completed
review_status: needs_review
acceptance_state: partially_met
```

## Structural Rejections

Reject the packet if any of these appear:

- nested YAML objects under top-level fields;
- YAML block scalars `|` or `>-`;
- non-JSON list syntax in list fields;
- markdown code fence around the whole packet;
- duplicate top-level fields;
- multiple `[MoSim Result Packet]` sections;
- unsupported status synonyms such as `complete`, `done`,
  `completed_with_conditions`, or `accepted_with_conditions`;
- raw transcript pasted into evidence;
- external paths outside project scope unless the packet is a blocker about
  an explicitly approved infrastructure path.

## Semantic Rejections

Reject the packet if:

- `task_id` does not match the dispatched task;
- summary changes or narrows the canonical task goal;
- terminal status has no evidence;
- terminal status has no next recommended action;
- `review_status=needs_review` has no risk, blocker, or review owner;
- `status=blocked` has no blocker reference or resume condition;
- `acceptance_state=met` conflicts with unresolved risks or blockers;
- context hash is stale or missing when required;
- files changed outside write scope;
- commands run include forbidden actions without an approved blocker;
- result claims tool, MCP, UE, MWORKS, Fab, Git, email, or notification
  capability without evidence paths.

## Output JSON

The validator should write a small JSON object:

```json
{
  "ok": false,
  "decision": "reject",
  "packet_path": "Results/agent_packets/example.yaml",
  "task_id": "COAGENT-ARCH-LONGRUN-01",
  "finding_codes": ["RPKT_UNSUPPORTED_STATUS"],
  "findings": [
    {
      "code": "RPKT_UNSUPPORTED_STATUS",
      "severity": "error",
      "field": "status",
      "message": "status complete is not router-compatible"
    }
  ],
  "router_import_allowed": false,
  "review_required": true,
  "repair_allowed": true,
  "next_action": "repair packet or re-dispatch with validator feedback"
}
```

Decisions:

- `accept`: safe to import;
- `accept_needs_review`: safe to import but requires review;
- `reject`: not durable communication;
- `block`: packet or transport state requires a blocker.

## Stable Finding Codes

| Code | Meaning |
|---|---|
| `RPKT_MISSING_FIELD` | required field absent |
| `RPKT_UNSUPPORTED_STATUS` | status or canonical status not allowed |
| `RPKT_NESTED_STRUCTURE` | nested YAML/object shape not router-compatible |
| `RPKT_BAD_LIST` | list field is not a single-line JSON array |
| `RPKT_EMPTY_EVIDENCE` | terminal packet lacks evidence |
| `RPKT_EMPTY_NEXT_ACTION` | no next recommended action |
| `RPKT_GOAL_MUTATION` | summary changes canonical goal |
| `RPKT_STALE_CONTEXT` | context hash missing or stale |
| `RPKT_SCOPE_VIOLATION` | file or command exceeds read/write scope |
| `RPKT_BLOCKER_INCOMPLETE` | blocked result lacks blocker/resume fields |
| `RPKT_REVIEW_OWNER_MISSING` | review-needed result has no reviewer |
| `RPKT_CAPABILITY_OVERCLAIM` | capability claim lacks evidence |
| `RPKT_RAW_TRANSCRIPT` | raw chat pasted as evidence |
| `RPKT_DUPLICATE_FIELD` | duplicate top-level field |
| `RPKT_REPAIR_NOTE_MISSING` | repaired packet lacks repair note |

Finding codes are stable test-contract values. User-facing wording may change;
codes should not change casually.

## Fixture Matrix

Positive fixtures:

| Fixture | Expected |
|---|---|
| valid completed packet with evidence | `accept` |
| valid completed packet with risks and review owner | `accept_needs_review` |
| valid blocked packet with blocker reference and resume condition | `block` |
| valid repaired packet with repair note | `accept_needs_review` |

Negative fixtures:

| Fixture | Expected Codes |
|---|---|
| nested YAML evidence object | `RPKT_NESTED_STRUCTURE` |
| `status: complete` | `RPKT_UNSUPPORTED_STATUS` |
| `canonical_status: completed_with_conditions` | `RPKT_UNSUPPORTED_STATUS` |
| terminal result with empty evidence | `RPKT_EMPTY_EVIDENCE` |
| terminal result with no next action | `RPKT_EMPTY_NEXT_ACTION` |
| summary rewrites task goal | `RPKT_GOAL_MUTATION` |
| stale or missing context hash | `RPKT_STALE_CONTEXT` |
| files changed outside write scope | `RPKT_SCOPE_VIOLATION` |
| blocked packet without resume condition | `RPKT_BLOCKER_INCOMPLETE` |
| needs-review packet without reviewer | `RPKT_REVIEW_OWNER_MISSING` |
| tool capability claim without evidence | `RPKT_CAPABILITY_OVERCLAIM` |
| raw chat transcript in evidence | `RPKT_RAW_TRANSCRIPT` |
| duplicate top-level field | `RPKT_DUPLICATE_FIELD` |

## Repair Policy

Repair is allowed only when:

- the packet content is clear;
- repair does not change the conclusion;
- unsupported shape is the only issue;
- a `repair_note` names original packet, reason, actor, and timestamp;
- repaired packet preserves original risks and unknowns.

Repair is forbidden when:

- conclusion is ambiguous;
- evidence is missing;
- canonical goal changed;
- blocked state lacks resume condition;
- capability claims are unsupported;
- write scope was exceeded.

Forbidden repairs require re-dispatch or a blocker packet.

## Integration With Other Contracts

- `result_packet_contract_hardening.md` defines the current packet template.
- `blocker_packet_templates.md` defines blocker packets when validation fails
  due to timeout, invalid result, auth/license, manual review, or destructive
  actions.
- `mailbox_ledger_and_replay_design.md` should record validator decision and
  repaired/superseded packet references as mailbox events.
- `common_proof_package_validator_design.md` should require clean result
  packet validation before a proof package can close.
- `candidate_a_fixture_spec.md` should include result-packet fixture cases
  before live Candidate A dispatch.

## Future Implementation Slice

This document tightens:

```text
COAGENT-IMPL-NEXT-11: Result Packet Contract Hardening
```

Implementation should add only a read-only validator and fixtures first.
It must not create conversations, dispatch packets, modify router semantics
opportunistically, send notifications, stage Git, or execute tool/MCP work.

## Open Questions

- Whether the current flat text packet should later become strict YAML or JSON
  can be decided after the validator proves the failure modes.
- Nested packet support may be useful later, but it should be a deliberate
  router/schema migration with fixtures, not an accidental acceptance path.
- Context hash validation needs the context-delta checker to become fully
  authoritative; until then, stale-context findings may depend on explicit
  expected hash input.
