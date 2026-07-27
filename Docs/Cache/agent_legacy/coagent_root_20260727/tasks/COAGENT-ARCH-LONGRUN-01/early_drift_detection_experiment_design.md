# COAGENT-ARCH-LONGRUN-01 Early Drift Detection Experiment Design

Date: 2026-05-30
Status: phase 2 design draft

## Purpose

Define a concrete experiment package for detecting long-running task drift
before hours are lost.

This closes the design gap behind P10 and strengthens P29. Existing operating
metrics define what to measure. This file defines the negative scenarios that
must be caught, the first evidence sources to inspect, and the required
response.

This is design only. It does not implement a checker, create fixtures, dispatch
conversations, edit runtime schemas, or mark the active goal complete.

## Core Claim To Prove Later

CoAgent can detect these failures early from durable task files:

```text
wrong goal, stale context, no evidence progress, fake parallelism,
unmapped research, blocked work without blocker, and completion overclaim
```

The future experiment passes only if each failure becomes a specific finding,
review state, or blocker before the task can continue as normal.

## Experiment Inputs

The future experiment should use only project-owned files:

| Input | Required Use |
|---|---|
| `task_charter.md` | canonical goal and non-goals |
| `shared_task_board.md` | WIP, active streams, phase state, risk register |
| `architecture_problem_matrix.md` | problem ids and required outputs |
| `goal_requirement_audit_map.md` | partial requirements and weak evidence |
| `goal_creation_and_recovery_protocol.md` | goal setup-action rejection |
| `context_pack.md` and context delta files | freshness and acknowledgement |
| result packets | independent evidence and local goal restatement |
| blocker packets | safe stop/resume state |
| runtime events | checkpoint and edge closeout evidence |

No chat transcript or Codex UI state may be used as proof. If the experiment
needs information that exists only in chat, the expected finding is
`OMS_DATA_MISSING` or `GOAL_CREATE_PREFLIGHT_MISSING`.

## Negative Scenario Matrix

| Scenario | Injected Fault | Expected Finding | Expected State | Required Response |
|---|---|---|---|---|
| `goal_setup_shell` | canonical goal says "create a 10-hour task" instead of doing 10-hour architecture work | `GOAL_SETUP_ACTION_ONLY` | `rejected` | stop dispatch and recreate goal through preflight |
| `goal_scope_loss_on_recreate` | recreated goal drops context/memory, communication, safety, or external learning scope | `GOAL_SCOPE_COMPONENT_LOST_ON_RECREATE` | `rejected` | rewrite goal before checkpoint |
| `checkpoint_no_delta` | checkpoint records elapsed time or file count but no requirement advanced | `GOAL_CHECKPOINT_NO_DELTA` plus `OMS_CHECKPOINT_STALE` when repeated | `review_required` | require evidence delta or rescope |
| `fake_parallelism` | multiple departments are listed active but only MainAgent produces evidence | `OMS_FAKE_PARALLELISM` | `review_required` | shrink topology or require result packets |
| `serial_collapse` | task claims multi-conversation work but all decisions and artifacts are made in one lane | `OMS_SERIAL_COLLAPSE` | `review_required` | reclassify as single-lane or dispatch bounded review |
| `stale_context_resume` | worker result cites old context hash after accepted context delta | `OMS_CONTEXT_ACK_MISSING` or `CTX_ACK_MISSING` | `blocked` | pause high-risk work until acknowledgement |
| `research_unmapped` | external source summary lacks problem id and adoption decision | `OMS_RESEARCH_UNMAPPED` or `ADOPT_PROBLEM_MISSING` | `review_required` | create/reject adoption proposal |
| `blocked_without_packet` | tool/license/UI blocker appears with no blocker packet for more than 10 minutes | `OMS_BLOCKER_MISSING` | `blocked` | write blocker packet with last safe state |
| `timeout_no_closeout` | dispatch timeout has no process cleanup, edge closeout, or blocker | `OMS_TIMEOUT_NO_BLOCKER` or `TRN_TIMEOUT_NO_CLOSEOUT` | `blocked` | close edge or record timeout blocker |
| `completion_overclaim` | final audit says complete while requirements remain gated or unverified | `OMS_COMPLETION_OVERCLAIM` and `GOAL_COMPLETION_OVERCLAIM` | `rejected` | keep goal active and update final audit |
| `unsupported_tool_claim` | UE/Fab/MWORKS/Codex route is claimed usable from stale memory | `OMS_UNSUPPORTED_CLAIM` or `TOOL_CAPABILITY_STALE` | `rejected` | require fresh capability card or downgrade claim |
| `review_escape_repeat` | same class of user correction recurs without retrospective action | `RETRO_REQUIRED_MISSING` | `review_required` | create owned retrospective action |

## Positive Control

The experiment also needs one healthy checkpoint fixture:

```yaml
scenario: healthy_design_checkpoint
canonical_goal_unchanged: true
evidence_delta:
  - early_drift_detection_experiment_design.md
requirements_advanced:
  - P10
  - P29
setup_actions_only: false
open_blockers: []
expected_state: ok
```

This prevents the future checker from rejecting every active long-running task
by default.

## Detection Order

Future implementation should run checks in this order:

1. path and source safety;
2. goal creation/recovery preflight;
3. canonical goal and scope component comparison;
4. checkpoint evidence delta;
5. context freshness and acknowledgement;
6. blocker presence and timeout closeout;
7. parallelism and topology evidence;
8. external adoption mapping;
9. product/tool evidence labels;
10. completion audit consistency;
11. retrospective requirement.

Reason: goal and safety failures must stop later interpretation. A task with a
wrong goal can make other metrics look healthy while still being misaligned.

## First Useful Experiment Package

The smallest package should live later under:

```text
CoAgent/tests/fixtures/operating_metrics/early_drift/
```

Required fixture folders:

- `healthy_design_checkpoint/`
- `goal_setup_shell/`
- `goal_scope_loss_on_recreate/`
- `checkpoint_no_delta/`
- `fake_parallelism/`
- `stale_context_resume/`
- `blocked_without_packet/`
- `completion_overclaim/`

Deferred fixture folders:

- `research_unmapped/`
- `unsupported_tool_claim/`
- `review_escape_repeat/`
- `timeout_no_closeout/`

The first fixture set is enough to prevent the most expensive failure modes:
wrong goal, fake work, stale context, blocked work, and false completion.

## Experiment Output

The future checker should emit:

```json
{
  "task_id": "COAGENT-ARCH-LONGRUN-01",
  "experiment": "early_drift_detection",
  "overall_state": "review_required",
  "scenario_results": [
    {
      "scenario": "goal_setup_shell",
      "expected_codes": ["GOAL_SETUP_ACTION_ONLY"],
      "actual_codes": ["GOAL_SETUP_ACTION_ONLY"],
      "decision": "pass"
    }
  ],
  "unexpected_passes": [],
  "unexpected_failures": [],
  "forbidden_side_effects": []
}
```

`unexpected_passes` are more dangerous than `unexpected_failures`: a drift
scenario that passes as healthy means CoAgent can waste hours with false
confidence.

## Manual Review Questions

When the user audits the experiment design, the key questions are:

1. Would this have caught the bad "create a 10-hour task" goal immediately?
2. Would this catch a PX4 task that studies papers for hours without producing
   identifiability or data-sufficiency evidence?
3. Would this catch a UE task that keeps trying Fab/UE routes without a
   capability card or blocker?
4. Would this catch a multi-conversation task where departments exist but no
   independent packets return?
5. Would this prevent final completion claims while the audit map still lists
   gated follow-ups?

## Relationship To Other Artifacts

| Artifact | Relationship |
|---|---|
| `operating_metrics_and_anti_drift_cadence.md` | metric definitions and cadence |
| `operating_metrics_snapshot_design.md` | future checker output model and `OMS_*` codes |
| `goal_creation_and_recovery_protocol.md` | setup-goal rejection and recovery rules |
| `goal_authority_and_decomposition_protocol.md` | goal hierarchy and non-substitution rules |
| `context_delta_checker_design.md` | context ack and stale-context semantics |
| `blocker_packet_validator_design.md` | blocker packet semantics |
| `external_adoption_store_checker_design.md` | external source mapping semantics |
| `evidence_label_doctor_design.md` | evidence-label overclaim rejection |
| `retrospective_and_improvement_closure_protocol.md` | repeated failure closure |

## Current Task Application

For `COAGENT-ARCH-LONGRUN-01`, this design adds concrete negative scenarios to
the existing metrics design. The active goal remains running. The next
implementation path is still a later approved read-only checker or fixture
generator; no runtime automation is approved here.
