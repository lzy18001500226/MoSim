# COAGENT-ARCH-LONGRUN-01 Verification Gate Hardening

Date: 2026-05-30
Status: design draft from VerificationAgent review

## Purpose

Turn verification from advisory review into an executable gate for long-running
multi-conversation work.

## Required Result Packet Extensions

Future task/result packets should carry these fields when the task is
long-running or multi-conversation:

- `canonical_goal_restatement`
- `context_pack_id`
- `context_pack_version_or_hash`
- `evidence_manifest`
- `process_metrics`
- `scope_changes`
- `blocker_history`
- `context_deltas_consumed`
- `review_owner`
- `closeout_artifacts`

If these fields are absent for a long-running task, the review state should be
`review_required` or `rejected`, depending on risk.

## Process Metric Thresholds

Initial thresholds for design experiments:

| Metric | Initial Gate |
|---|---|
| `critical_path_time_without_checkpoint` | fail if over 60 minutes |
| `blocked_time_without_blocker_packet` | fail if over 10 minutes |
| `fake_parallelism_count` | review if greater than 0 |
| `serial_collapse_count` | review if a multi-lane task has no independent result packet |
| `handoff_failure_count` | review if greater than 0, fail if repeated twice |
| `context_refresh_latency` | fail if high-risk slice resumes before acknowledgement |
| `rework_count` | review if same assumption causes rework twice |
| `review_escape_count` | fail if issue appears after acceptance and had missing evidence |
| `closeout_latency` | review if accepted work is not integrated or documented within one checkpoint |

These thresholds are deliberately conservative. They can be tuned only after
real task data exists.

## Negative Drift Tests

The verification gate must reject or require review for packets that:

- omit required evidence;
- change the canonical task goal locally;
- resume from a stale context without acknowledgement;
- claim product evidence from design-only material;
- mark a task complete while an open blocker exists;
- close a task with no imported result packet or review packet;
- report broad research summaries without decision mapping.

## PX4 Evidence Template Requirements

The PX4 parameter-identification workflow needs mandatory templates for:

- log signal inventory;
- parameter identifiability matrix;
- method selection table;
- uncertainty and residual report;
- simulation tuning record;
- MWORKS/Sysplorer evidence label;
- non-identifiable parameter list.

Template:

```text
CoAgent/protocol/templates/px4_parameter_identifiability_matrix.yaml
```

Acceptance must distinguish:

- directly observed;
- estimated;
- calibrated;
- assumed;
- non-identifiable;
- behavior-matched.

## UE Scene Truth Template Requirements

The UE scene-truth workflow needs mandatory templates for:

- scene-source capability card;
- import/provenance record;
- collision export manifest;
- navmesh export manifest;
- occupancy/grid or mesh truth manifest;
- coordinate frame definition;
- planning-consumer contract;
- manual visual review sign-off.

Templates:

```text
CoAgent/protocol/templates/ue_scene_truth_capability_card.yaml
CoAgent/protocol/templates/scene_truth_artifact_manifest.yaml
```

Rendering screenshots cannot satisfy truth acceptance.

## Gate Output States

| Condition | Output State |
|---|---|
| All required evidence and metrics present, no active risks | `accepted` |
| Evidence present but thresholds unresolved | `needs_review` |
| Context stale, blocker open, or canonical goal changed | `blocked` or `rejected` |
| Missing product evidence for a product claim | `rejected` |
| Missing process evidence for a long-running task | `review_required` |

## Current Architecture Consequence

`COAGENT-ARCH-LONGRUN-01-VERIFY-01` is accepted as a useful review result with
conditions. It explicitly does not prove that the current process is already
self-enforcing. The next design slice must create template files and at least
one negative drift-packet test.
