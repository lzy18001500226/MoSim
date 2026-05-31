# COAGENT-ARCH-LONGRUN-01 Candidate A Fixture Spec

Date: 2026-05-30
Status: design fixture specification for later validator work

## Purpose

Turn Candidate A from a proof-package idea into concrete positive and negative
fixtures. A later validator should be able to read these fixtures, produce
deterministic findings, and prove that the architecture packet chain is safe
to run before spending live conversation transport budget.

This is design-only. It does not create fixture files, run live dispatch,
create conversations, stage Git, call tools, or change runtime schemas.

## Fixture Root Convention

Fixture file contents should instantiate the exact package shape defined in:

```text
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_minimal_package_contract.md
```

This file defines which fixtures pass or fail. The minimal package contract
defines what each valid fixture file should contain.

Future implementation should place fixtures under:

```text
CoAgent/tests/fixtures/proof_packages/candidate_a/
  valid_minimal/
  missing_context_pack/
  goal_mismatch/
  external_result_path/
  no_review_node/
  raw_transcript_context/
  forbidden_tool_node/
  invalid_flat_result_status/
  missing_context_delta/
  timeout_without_blocker/
```

Each fixture should be a small package shaped like:

```text
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

## Valid Minimal Fixture

Fixture: `valid_minimal`

Expected result:

```text
decision: pass
ok: true
errors: []
warnings: []
```

Required properties:

- `task_id` is `COAGENT-PROOF-CANDIDATE-A`;
- the canonical goal is identical in `task_charter.yaml`,
  `workflow_graph.yaml`, and every handoff;
- context pack is curated and references only task-local design files;
- workflow has `context_review`, `verification_review`,
  `knowledge_promotion`, `trace_eval`, and `closeout` nodes;
- all output packet paths are under the fixture package root or
  `Results/agent_packets/`;
- no tool, UE, MWORKS, Fab, Git stage, worktree creation, or notification node
  exists;
- at least two non-MainAgent packets exist;
- one `context_delta.yaml` exists and references the source packet;
- final review decision is terminal;
- `closeout.md` lists proven mechanism, failed mechanism, gated next work, and
  recommended next implementation slice.

## Negative Fixture Matrix

| Fixture | Broken Field | Expected Code | Expected Decision |
|---|---|---|---|
| `missing_context_pack` | context pack file absent | `PREFLIGHT_CONTEXT_PACK_MISSING` | `fail_before_dispatch` |
| `goal_mismatch` | handoff canonical goal differs from charter | `PREFLIGHT_GOAL_MISMATCH` | `fail_before_dispatch` |
| `external_result_path` | result packet path points outside package/`Results/` | `PREFLIGHT_OUTPUT_PATH_UNSAFE` | `fail_before_dispatch` |
| `no_review_node` | workflow has no review node | `PREFLIGHT_REVIEW_NODE_MISSING` | `fail_before_dispatch` |
| `raw_transcript_context` | context pack includes raw chat transcript marker | `PREFLIGHT_RAW_TRANSCRIPT_CONTEXT` | `fail_before_dispatch` |
| `forbidden_tool_node` | workflow adds UE/MWORKS/Fab/Git/tool node | `PREFLIGHT_FORBIDDEN_ACTION_SCOPE` | `fail_before_dispatch` |
| `invalid_flat_result_status` | result packet uses `complete` or nested YAML | `POST_UNSUPPORTED_RESULT_STATUS` or `POST_NESTED_YAML_FOR_FLAT_PACKET` | `rejected` |
| `missing_context_delta` | packets omit context delta | `POST_CONTEXT_DELTA_MISSING` | `blocked_after_dispatch` |
| `timeout_without_blocker` | expected packet missing and no blocker exists | `POST_PACKET_OR_BLOCKER_MISSING` | `blocked_after_dispatch` |

## Required Error Code Addition

`common_proof_package_validator_design.md` should include this Candidate A
specific preflight code:

```text
PREFLIGHT_FORBIDDEN_ACTION_SCOPE
```

Meaning:

```text
Candidate A attempted to add product tools, UE/MWORKS/Fab/Git operations,
worktree creation, notification, or other gated automation to a proof whose
scope is only packet, context, review, trace, and closeout mechanics.
```

Severity: error.

## Validator Order For Candidate A

The future validator should run in this order:

1. parse package root and required file presence;
2. compare canonical goal across charter, graph, and handoffs;
3. check path safety for all declared inputs and outputs;
4. scan context pack for raw transcript and private/secret path markers;
5. validate workflow graph node types and required review/closeout nodes;
6. apply Candidate A forbidden-scope checks;
7. validate handoff fields and return paths;
8. validate pre-existing packets when mode is `post_dispatch`;
9. require context delta and trace eval in `post_dispatch`;
10. produce one JSON report with stable finding codes.

Rationale:

```text
Fail cheap and structural checks before inspecting packets. Do not spend
transport or live conversation budget on a package that cannot pass the
preflight file/goal/path/review/scope gates.
```

## Fixture Acceptance For Implementation

The later implementation slice may claim Candidate A fixture support only when:

- all fixtures above exist as tiny deterministic files;
- fixture paths contain no private external paths or secrets;
- fixture validation does not call Codex, MCP, UE, MWORKS, Fab, Git stage,
  worktree, email, or notification tools;
- every negative fixture fails with the expected stable code;
- the validator JSON output includes `candidate_id`, `mode`,
  `proof_package_root`, `decision`, `ok`, `findings`, and `next_action`;
- the test suite covers both `preflight` and `post_dispatch` modes.

## Design Decision

Candidate A should not be run live until either this fixture set is implemented
or the user explicitly accepts that the live proof may expose avoidable
preflight/package errors. The preferred next implementation is still a
read-only validator and fixture harness, not another live dispatch attempt.
