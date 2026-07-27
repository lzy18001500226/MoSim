# COAGENT-ARCH-LONGRUN-01 Result Packet Contract Hardening

Date: 2026-05-30
Status: design draft from real packet failures

## Purpose

Prevent visible department conversations from returning useful conclusions in
an invalid packet shape. A result that cannot be routed is not durable
communication.

## Current Failure Modes Observed

| Task | Failure | Consequence |
|---|---|---|
| `COAGENT-ARCH-LONGRUN-01-CONTEXT-01` | worker wrote nested YAML and `status: complete` | router rejected schema; MainAgent repaired packet |
| `COAGENT-ARCH-LONGRUN-01-VERIFY-01` | worker wrote nested YAML and `canonical_status: completed_with_conditions` | router rejected schema; MainAgent repaired packet |
| `COAGENT-ARCH-LONGRUN-01-RUNTIME-01` | no packet within 60s | task blocked and process cleaned up |

## Router-Compatible Status Values

Workers must use only these terminal values unless the runtime contract is
changed:

- `completed`
- `review_required`
- `blocked`
- `failed`
- `canceled`
- `rejected`
- `superseded`

Do not use:

- `complete`
- `done`
- `completed_with_conditions`
- `accepted_with_conditions`
- custom status strings.

If conditions remain, use:

```text
status: completed
canonical_status: completed
review_status: needs_review
acceptance_state: partially_met
risks: ["condition 1", "condition 2"]
```

## Flat Text Packet Template

Use this exact shape for current router compatibility:

```text
[MoSim Result Packet]
task_id: <task id>
status: completed
canonical_status: completed
task_class: <clear_task | long_running_task | review_task>
summary: <single paragraph, no YAML block marker>
owner: <department or worker>
role: <department or worker role>
read_scope: ["path/or/scope"]
write_scope: ["path/or/scope"]
files_changed: ["path/or/output"]
commands_run: ["command or []"]
evidence: ["evidence item 1", "evidence item 2"]
risks: ["risk item if any"]
blockers: []
review_status: <not_required | pending | accepted | needs_review | rejected>
acceptance_state: <met | partially_met | not_met | unknown>
continue_or_stop: stop
next_recommended_action: <single paragraph>
events: []
```

Rules:

- list fields must be single-line JSON arrays;
- do not use nested YAML objects;
- do not use `>-` or `|` YAML block markers;
- keep evidence as short strings with paths and findings;
- put unresolved conditions in `risks`, not in custom statuses;
- use `review_status: needs_review` for conditional acceptance.

## Review Interpretation

| Worker Output | Router Result | Meaning |
|---|---|---|
| valid packet, no risks, evidence present | `accepted` | import can be trusted as mechanically clean |
| valid packet with risks | `needs_review` | import is durable, but PMO/reviewer must handle risks |
| invalid packet | `rejected` | communication failed; repair or re-dispatch required |
| missing packet after timeout | blocked task | transport/runtime failure, not worker acceptance |

## Dispatch Instruction Update

Future task packets should include this short hard instruction:

```text
Use the flat text Result Packet template. All list fields must be single-line
JSON arrays. Do not write nested YAML, YAML block scalars, or custom status
values. If the result is conditional, use review_status=needs_review,
acceptance_state=partially_met, and list conditions under risks.
```

## Negative Packet Fixtures To Add Later

The future validation test suite should include:

- nested YAML evidence object;
- `status: complete`;
- `canonical_status: completed_with_conditions`;
- terminal packet with no evidence;
- terminal packet with no next action;
- packet that changes canonical goal in summary;
- packet with stale context hash;
- packet with missing review owner for mutable output.

## Current Architecture Consequence

The next implementation slice should not expand automatic dispatch until
packet format drift is reduced. Result packet template enforcement is higher
priority than creating more conversations.
