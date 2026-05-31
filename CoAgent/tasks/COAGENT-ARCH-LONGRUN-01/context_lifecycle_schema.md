# COAGENT-ARCH-LONGRUN-01 Context Lifecycle Schema

Date: 2026-05-30
Status: design draft from ContextMemoryAgent review

## Purpose

Make context freshness machine-checkable across visible Codex conversations.
The design must not rely on a worker remembering that a context pack was
superseded in raw chat.

## Required Context Objects

### Context Pack Record

Required fields:

- `context_pack_id`
- `task_id`
- `context_pack_version_or_hash`
- `created_at`
- `created_by`
- `source_paths`
- `accepted_decisions`
- `excluded_stale_assumptions`
- `required_acknowledgement`
- `superseded_by`
- `valid_for_slices`
- `risk_level`

Rule:

```text
No scoped conversation starts without a context_pack_id and version/hash.
```

### Context Delta Record

Required fields:

- `context_delta_id`
- `task_id`
- `created_at`
- `created_by`
- `change_type`
- `changed_fact_or_decision`
- `supersedes`
- `affected_slices`
- `affected_departments`
- `acknowledgement_required`
- `pause_until_refresh`
- `reviewer`
- `resume_condition`
- `evidence_paths`

Rule:

```text
A context delta changes task state only after Dispatch records it on the
shared board or mailbox.
```

### Acknowledgement Record

Required fields:

- `ack_id`
- `context_delta_id`
- `task_id`
- `department`
- `conversation_or_worker_id`
- `acknowledged_context_pack_version_or_hash`
- `acknowledged_at`
- `acknowledged_by`
- `resume_allowed`
- `resume_reason`

Rule:

```text
High-risk work cannot resume from a stale context until the affected
conversation has an acknowledgement record with resume_allowed=true.
```

## State Transitions

| State | Trigger | Allowed Next State |
|---|---|---|
| `fresh` | context pack created and no superseding delta exists | `stale`, `superseded` |
| `stale` | delta affects this slice and acknowledgement is required | `paused_for_refresh`, `superseded` |
| `paused_for_refresh` | Dispatch pauses affected slice | `acknowledged`, `blocked` |
| `acknowledged` | affected conversation records version/hash acknowledgement | `fresh` |
| `superseded` | newer context pack replaces old pack | closed only |

## Dispatch Gate

Before sending or resuming a task packet, Dispatch must verify:

- the packet has `context_pack_id`;
- the context pack version/hash matches current task board state;
- no open `pause_until_refresh` applies to the target slice;
- if an acknowledgement is required, the acknowledgement record exists;
- result packet path and review owner are still current.

If any check fails, Dispatch sends a `context_refresh` or `blocker` packet
instead of normal work.

## Doctor Check Draft

The future doctor check should fail when:

- an active task packet lacks context version/hash;
- a context delta marks a slice affected but no acknowledgement exists;
- a high-risk task resumes while `pause_until_refresh=true`;
- a result packet cites a superseded context pack;
- accepted knowledge is promoted from a context record marked draft or
  superseded.

## Current Architecture Consequence

`COAGENT-ARCH-LONGRUN-01-CONTEXT-01` is accepted only as a design review, not
as final context enforcement. The next architecture slice must convert these
fields into templates and checks before automatic long-running dispatch is
considered reliable.
