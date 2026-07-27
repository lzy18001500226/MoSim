# COAGENT-ARCH-LONGRUN-01 Candidate A Validator Execution Design

Date: 2026-05-30
Status: design contract for `COAGENT-IMPL-NEXT-15`

## Purpose

Candidate A already has a packet-chain blueprint, proof-package design, and
fixture specification. This document defines how the later validator should
execute those rules without inventing behavior during implementation.

The exact minimal file and field contract consumed by this validator is:

```text
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_minimal_package_contract.md
```

This is design-only. It does not create fixtures, run validators, dispatch
conversations, create worktrees, stage Git, or call tools/MCP.

## Validator Objective

```text
decide whether Candidate A is structurally safe to run or close
```

The validator should make live dispatch cheaper and safer by rejecting bad
packages before transport starts, and by rejecting bad closeout after packets
return.

## CLI Shape

Future command shape:

```bash
python3 CoAgent/validators/candidate_a_validator.py \
  --proof-root Results/coagent_proofs/COAGENT-PROOF-CANDIDATE-A \
  --mode preflight \
  --json-output Results/coagent_proofs/COAGENT-PROOF-CANDIDATE-A/validator_preflight.json
```

Modes:

- `preflight`: package can be checked before any live dispatch;
- `post_dispatch`: package outputs can be checked after conversations return;
- `fixture`: fixture directory is checked against expected decision and codes.

The command is read-only except for optional JSON report output.

## Required Package Layout

The validator should expect:

```text
<proof-root>/
  task_charter.yaml
  context_pack.md
  workflow_graph.yaml
  handoffs/
    context.yaml
    verification.yaml
    knowledge.yaml
  packets/
    context_result.txt
    knowledge_result.txt
    context_delta.yaml
  reviews/
    verify_review.yaml
    trace_eval.yaml
  closeout.md
```

`preflight` requires inputs and declared output paths, but output packet files
may be absent. `post_dispatch` requires either every declared packet or a valid
blocker packet.

## Validation Pipeline

Run checks in this order:

1. load package manifest from filesystem;
2. verify required input files for selected mode;
3. parse task charter and canonical goal;
4. parse workflow graph and compare canonical goal;
5. parse handoffs and compare task id, goal, context path, result path,
   review gate, return path, and forbidden actions;
6. check every declared path is under the proof root or approved `Results/`
   root;
7. scan context pack for raw transcript markers, private paths, secret
   markers, and stale/rejected assumption omissions;
8. enforce Candidate A non-goals: no UE, MWORKS, Fab, Git stage, worktree
   creation, notification, app-server, automatic conversation creation, or
   tool/MCP execution nodes;
9. in `post_dispatch`, validate result packets through the future result
   packet validator;
10. in `post_dispatch`, validate mailbox state through the future mailbox
    ledger checker when mailbox files exist;
11. in `post_dispatch`, require context delta and trace evaluation;
12. require closeout to name proven mechanism, failed mechanism, gated next
    work, and recommended next implementation slice.

The validator should stop after structural parse failure, but otherwise collect
all findings so the user receives one repair list.

## Dependency Boundaries

The Candidate A validator may call or import future read-only validators:

| Dependency | Allowed Use | Not Allowed |
|---|---|---|
| result packet validator | validate `packets/*_result.txt` | repair packet automatically |
| handoff/workflow validator | validate graph and handoff schema | execute graph |
| context delta checker | validate context delta fields | generate context |
| mailbox checker | verify ack/response/closeout state | deliver messages |
| common proof validator | run common preflight/post checks | dispatch conversations |

If a dependency is not implemented yet, Candidate A validator must report
`needs_dependency` rather than silently weakening the gate.

## Output JSON

Required report fields:

```json
{
  "ok": false,
  "candidate_id": "candidate_a_packet_chain",
  "mode": "preflight",
  "proof_package_root": "Results/coagent_proofs/COAGENT-PROOF-CANDIDATE-A",
  "decision": "fail_before_dispatch",
  "dependency_state": {
    "result_packet_validator": "available",
    "mailbox_checker": "missing"
  },
  "findings": [
    {
      "code": "PREFLIGHT_CONTEXT_PACK_MISSING",
      "severity": "error",
      "path": "context_pack.md",
      "message": "context pack is required before dispatch"
    }
  ],
  "checked_files": [],
  "next_action": "fix_package_before_dispatch"
}
```

Allowed decisions:

- `pass_preflight`;
- `pass_post_dispatch`;
- `pass_with_warnings`;
- `fail_before_dispatch`;
- `blocked_after_dispatch`;
- `needs_dependency`;
- `needs_review`;
- `rejected`.

## Candidate A Specific Finding Codes

Reuse common proof-package codes and add:

| Code | Meaning |
|---|---|
| `A_REQUIRED_HANDOFF_MISSING` | context, verification, or knowledge handoff absent |
| `A_REQUIRED_PACKET_MISSING` | required result/review/context/trace packet absent |
| `A_NON_MAIN_PACKET_COUNT_LOW` | fewer than two non-MainAgent packet/blocker outputs |
| `A_CONTEXT_DELTA_MISSING` | no context delta in post-dispatch mode |
| `A_TRACE_EVAL_MISSING` | trace evaluation absent |
| `A_CLOSEOUT_INCOMPLETE` | closeout lacks proven/failed/gated/next fields |
| `A_FORBIDDEN_SCOPE_NODE` | proof includes product/tool/Git/notification scope |
| `A_DEPENDENCY_MISSING` | required read-only validator is not available |
| `A_MAILBOX_OPEN_RESPONSE` | mailbox has open required response at closeout |

Stable codes matter more than wording. They allow future regressions to fail
for the right reason.

## Fixture Execution

Fixture mode should read a small expectation file in each fixture:

```yaml
expected_decision: fail_before_dispatch
expected_codes:
  - PREFLIGHT_CONTEXT_PACK_MISSING
```

Fixture mode passes only when:

- the actual decision equals `expected_decision`;
- all expected codes are present;
- no unexpected `error` finding appears in a positive fixture;
- the fixture command performs no live dispatch or tool calls.

## Live Proof Gate

Candidate A live proof may start only when one of these is true:

1. validator `preflight` passes; or
2. user explicitly approves live proof despite listed validator gaps.

If dependency validators are missing, default decision is:

```text
needs_dependency
```

This means architecture progress can continue through implementation of the
missing validator, but live proof should not proceed by default.

## Post-Dispatch Closeout Gate

Candidate A closeout may be accepted only when:

- required packets or blocker packets exist;
- result packets pass the result-packet validator;
- at least two non-MainAgent outputs exist;
- context delta exists;
- trace evaluation exists or marks missing instrumentation explicitly;
- mailbox checker reports no open required response, when mailbox files exist;
- closeout names proven mechanism, failed mechanism, gated next work, and
  recommended next implementation slice.

If any of these fail, closeout decision is `blocked_after_dispatch` or
`needs_review`, not `pass_post_dispatch`.

## Implementation Boundary

The implementation slice may add:

- validator script;
- tiny fixture files;
- unit tests;
- JSON report output.

It may not add:

- app-server transport;
- automatic conversation creation;
- automatic dispatch;
- worktree creation;
- Git stage/commit/push;
- email or desktop notification;
- UE/MWORKS/Fab/tool/MCP calls;
- router semantic expansion beyond reading result-packet validation results.

## Design Decision

Candidate A is the correct next live proof only after preflight validation is
real or after explicit user acceptance of validation risk. The default next
implementation remains `COAGENT-IMPL-NEXT-11` and
`COAGENT-IMPL-NEXT-15`, not live dispatch.
