# CoAgent Result Router

## Purpose

This directory owns result-packet recovery after a department or dedicated task
conversation writes its output.

The router keeps result import separate from transport. Transport starts or
polls a visible conversation; the result router validates, imports, archives,
and summarizes the packet.

## Current Components

| File | Purpose |
|---|---|
| `result_router.py` | parse JSON/text result packets, validate required fields, run review gate, import into runtime, archive packet, and write summaries |

## Current Commands

```bash
python CoAgent/result_router/result_router.py validate --packet Results/agent_packets/<task_id>.yaml
python CoAgent/result_router/result_router.py import --packet Results/agent_packets/<task_id>.yaml
python CoAgent/result_router/result_router.py import --packet Results/agent_packets/<task_id>.yaml --notify-weixin
python CoAgent/result_router/result_router.py import --packet Results/agent_packets/<task_id>.yaml --notify-weixin --send-weixin
```

Archives are written under ignored `Results/agent_packets/archive/`.

Review gate files are written under ignored `Results/agent_packets/reviews/`.
When `--notify-weixin` is used, a notification packet is written under ignored
`Results/agent_packets/notifications/` and passed to the cc-connect Weixin
adapter in dry-run mode by default. Real sending requires explicit
`--send-weixin`.

Notification types:

- `completion_notification`: generated for accepted `canonical_status=completed`
  packets. This is required because task completion must notify the user even
  when no human review is needed.
- `blocker_notification`: generated for review-required, blocked, failed,
  auth-required, and other human-action states.

The end-to-end non-sending check is:

```bash
python CoAgent/tests/test_review_notification_loop.py
```

On import, the router also writes recoverability metadata back to the runtime
task: `review_status`, `human_needed`, `next_action`, summary/review/archive
paths, and notification packet path. This makes `status-board` useful after a
session loss without rereading the full result packet archive.

The gate is intentionally conservative:

- `accepted`: terminal packet has evidence and next action.
- `needs_review`: packet imported, but it has missing evidence, missing next
  action, concerns, blockers, failures, cancellation, or unresolved risks.
- `rejected`: required packet validation failed.

The gate does not replace human review. It prevents the main conversation from
treating every imported result as automatically accepted.
