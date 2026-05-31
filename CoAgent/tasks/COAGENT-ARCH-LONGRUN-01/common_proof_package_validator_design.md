# COAGENT-ARCH-LONGRUN-01 Common Proof Package Validator Design

Date: 2026-05-30
Status: design blueprint for `COAGENT-IMPL-NEXT-20`

## Purpose

Define the common validator that future Candidate A-E proof packages should
pass before live dispatch or post-dispatch closeout. The validator prevents
each task line from inventing its own gate rules.

This is design-only. It does not implement the validator or execute proof
packages.

## Validator Inputs

Minimum input:

```text
proof_package_root
candidate_id
mode
```

Modes:

- `preflight`: validate package structure before dispatch;
- `post_dispatch`: validate produced packets and closeout after execution;
- `fixture`: run positive/negative fixtures without live dispatch.

Supported candidates:

- `candidate_a_packet_chain`;
- `candidate_b_px4_parameter`;
- `candidate_c_ue_scene_truth`;
- `candidate_d_git_heavy_change`;
- `candidate_e_auth_license_interruption`.

## Expected Package Layout

```text
Results/coagent_proofs/<proof-id>/
  task_charter.yaml
  context_pack.md
  workflow_graph.yaml
  handoffs/
    *.yaml
  inputs/
    ...
  packets/
    ...
  blockers/
    ...
  reviews/
    review_packet.yaml
    trace_eval.yaml
  closeout.md
```

Not every folder must contain files in `preflight`, but missing required files
for the selected candidate must be reported.

## Common Preflight Checks

| Code | Check | Severity |
|---|---|---|
| `PREFLIGHT_CANONICAL_GOAL_MISSING` | task charter has no canonical goal | error |
| `PREFLIGHT_GOAL_MISMATCH` | canonical goal differs between charter, workflow, and handoffs | error |
| `PREFLIGHT_CONTEXT_PACK_MISSING` | context pack path is missing or file absent | error |
| `PREFLIGHT_REVIEW_NODE_MISSING` | workflow graph has no review node | error |
| `PREFLIGHT_CLOSEOUT_NODE_MISSING` | workflow graph has no closeout or close condition | error |
| `PREFLIGHT_RESULT_PATH_MISSING` | required output path missing | error |
| `PREFLIGHT_OUTPUT_PATH_UNSAFE` | output path outside `Results/` or package root | error |
| `PREFLIGHT_OWNER_MISSING` | owner, reviewer, or integration owner missing | error |
| `PREFLIGHT_FORBIDDEN_ACTIONS_MISSING` | high-risk proof lacks forbidden actions | error |
| `PREFLIGHT_TEMPLATE_REFERENCE_MISSING` | required protocol template not referenced | warning or error by candidate |
| `PREFLIGHT_RAW_TRANSCRIPT_CONTEXT` | context pack includes raw transcript instead of curated context | error |
| `PREFLIGHT_SECRET_OR_PRIVATE_PATH` | context references secrets or private external paths | error |

## Common Post-Dispatch Checks

| Code | Check | Severity |
|---|---|---|
| `POST_PACKET_OR_BLOCKER_MISSING` | required packet absent and no blocker exists | error |
| `POST_UNSUPPORTED_RESULT_STATUS` | current flat result packet uses unsupported status | error |
| `POST_NESTED_YAML_FOR_FLAT_PACKET` | current router-bound result packet uses nested YAML | error |
| `POST_GOAL_MUTATION` | worker result changes canonical goal | error |
| `POST_CONTEXT_DELTA_MISSING` | proof requires context lifecycle but no delta exists | error |
| `POST_REVIEW_NON_TERMINAL` | review packet has no terminal decision | error |
| `POST_TRACE_METRIC_MISSING` | trace metric missing without `needs_instrumentation` | error |
| `POST_OPEN_BLOCKER_MARKED_COMPLETE` | open blocker exists while task is complete | error |
| `POST_PRODUCT_EVIDENCE_MISLABELED` | design/offline output claimed as tool/product evidence | error |
| `POST_MANUAL_REVIEW_USED_AS_TRUTH` | manual review substituted for product truth | error |
| `POST_CLOSEOUT_NEXT_ACTION_MISSING` | closeout lacks next action or gated follow-on decision | error |

## Candidate-Specific Extensions

### Candidate A

Extra checks:

- at least two non-MainAgent result or blocker packets;
- at least one context delta;
- required conversations match the blueprint unless optional lanes are
  justified;
- no UE/MWORKS/Fab/Git nodes.
- no tool execution, worktree creation, notification, or other gated automation
  in the Candidate A graph.

Extra error code:

| Code | Check | Severity |
|---|---|---|
| `PREFLIGHT_FORBIDDEN_ACTION_SCOPE` | Candidate A attempts to include product tools, UE/MWORKS/Fab/Git operations, worktree creation, notification, or gated automation | error |

### Candidate B

Extra checks:

- `px4_parameter_identifiability_matrix.yaml` exists;
- every estimated row has uncertainty and validation residual fields;
- non-identifiable rows are allowed and visible;
- `offline_script` cannot satisfy `MWORKS_MCP` evidence;
- simulation tuning requires prior tool-health evidence.

### Candidate C

Extra checks:

- capability card exists before truth manifest;
- planning readiness false unless truth artifacts exist;
- coordinate frame and unit scale are present for truth artifacts;
- visual review does not substitute for collision/navmesh/occupancy/SDF or
  equivalent truth;
- Fab/manual import blockers are recorded when required.

### Candidate D

Extra checks:

- change inventory exists;
- no broad `git add -A` plan;
- large binary/generated/external batches have policy;
- destructive actions have approval blocker;
- rollback plan exists;
- same-file overlap has integration owner.

### Candidate E

Extra checks:

- blocker packet has last safe state, exact PMO user ask, resume condition,
  dedupe key, retry policy, and safe parallel work decision;
- duplicate ask count is reported;
- suspected login/license blocker has no unapproved retry loop;
- no secrets or credential material are echoed;
- notification transport is not enabled by the proof.

## Output Format

The validator should output JSON:

```json
{
  "ok": false,
  "candidate_id": "candidate_a_packet_chain",
  "mode": "preflight",
  "proof_package_root": "Results/coagent_proofs/COAGENT-PROOF-CANDIDATE-A",
  "findings": [
    {
      "code": "PREFLIGHT_CONTEXT_PACK_MISSING",
      "severity": "error",
      "path": "context_pack.md",
      "message": "context pack is required before dispatch"
    }
  ],
  "next_action": "fix_package_before_dispatch"
}
```

Allowed high-level decisions:

- `pass`;
- `pass_with_warnings`;
- `fail_before_dispatch`;
- `blocked_after_dispatch`;
- `needs_review`;
- `rejected`.

## Fixture Matrix

Minimum future fixtures:

| Fixture | Candidate | Expected |
|---|---|---|
| valid minimal Candidate A package | A | pass |
| missing context pack | common | fail before dispatch |
| external output path | common | fail before dispatch |
| goal mismatch | common | fail before dispatch |
| missing review node | common | fail before dispatch |
| invalid flat result packet status | common | blocked/rejected after dispatch |
| PX4 all-identifiable overclaim | B | rejected |
| UE screenshot-as-truth | C | rejected |
| Git broad add-A plan | D | rejected |
| auth retry loop with no user confirmation | E | blocked/rejected |

Candidate A fixtures are specified in:

```text
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_fixture_spec.md
```

## Implementation Boundary

The validator must be read-only by default:

- no live dispatch;
- no tool/MCP calls;
- no automatic conversation creation;
- no worktree creation;
- no Git stage/commit/push;
- no email or desktop notification;
- no GUI/login/license automation.

## Design Decision

The common proof package validator should be implemented before running
Candidate A as the default live proof. If the user wants a manual live proof
first, the proof still should be judged against these checks and any missing
validator behavior should become an explicit finding.
