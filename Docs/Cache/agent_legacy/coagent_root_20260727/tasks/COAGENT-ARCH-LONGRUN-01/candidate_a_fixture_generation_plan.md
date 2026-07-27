# COAGENT-ARCH-LONGRUN-01 Candidate A Fixture Generation Plan

Date: 2026-05-30
Status: design plan for later implementation

## Purpose

Candidate A now has a proof-package overview, a minimal file contract, a
fixture specification, and a validator execution design. The remaining design
gap is the generation sequence: what files a later implementation should
create first, which values must be shared, which negative fixtures should be
derived by mutation, and where human review must stop the process.

This document makes fixture generation deterministic without implementing it.
It does not create fixture files, run validators, dispatch conversations,
create worktrees, call Codex, call MCP, stage Git, or change runtime schemas.

## Generation Objective

```text
Produce tiny deterministic Candidate A proof-package fixtures from one valid
base package plus controlled mutations.
```

The generator must prove package mechanics only. It must not prove product
work, live communication, transport reliability, UE/MWORKS/Fab readiness,
notification delivery, Git integration, or worktree isolation.

## Source Documents

The later implementation must treat these documents as ordered inputs:

1. `candidate_a_minimal_package_contract.md`
2. `candidate_a_fixture_spec.md`
3. `candidate_a_validator_execution_design.md`
4. `validator_dependency_and_rollout_plan.md`
5. `result_packet_validator_design.md`
6. `handoff_workflow_validator_design.md`
7. `context_delta_checker_design.md`
8. `evidence_label_doctor_design.md`

If these documents conflict, the generator should fail with
`FIXTURE_SOURCE_CONFLICT` rather than silently choosing one.

## Output Root

Future generated fixtures should live under:

```text
CoAgent/tests/fixtures/proof_packages/candidate_a/
```

Expected children:

```text
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

Every fixture directory should contain:

```text
fixture_expectation.yaml
task_charter.yaml
context_pack.md
workflow_graph.yaml
handoffs/
packets/
blockers/
reviews/
validator_reports/
closeout.md
```

Negative fixtures may intentionally omit one required file when omission is
the tested failure. In that case `fixture_expectation.yaml` must name the
omitted file and expected finding code.

## Shared Fixture Constants

The generator should write these constants from one source object:

```yaml
task_id: COAGENT-PROOF-CANDIDATE-A
candidate_id: candidate_a_packet_chain
task_class: architecture_packet_chain_proof
canonical_task_goal: >
  Prove that CoAgent can coordinate a minimal multi-conversation architecture
  packet chain using curated context, handoff records, result or blocker
  packets, review, trace evaluation, context delta, and closeout without
  product-tool execution or gated automation.
dispatch_owner: DispatchAgent
review_owner: VerificationAgent
close_owner: MainAgent
```

The same in-memory constants should populate charter, graph, handoffs,
expected packets, context delta, review, trace eval, and closeout. Manual
string duplication is a fixture-generation defect.

## Positive Fixture Build Order

The valid fixture should be built in this order:

1. Create fixture root and fixed subdirectories.
2. Write `fixture_expectation.yaml` with `expected_decision: pass_preflight`
   and `expected_codes: []`.
3. Write `task_charter.yaml` from shared constants and required forbidden
   actions.
4. Write `context_pack.md` with only curated project-local references.
5. Write `workflow_graph.yaml` with charter, context, verification,
   knowledge, trace, and closeout nodes.
6. Write `handoffs/context_memory.yaml`,
   `handoffs/verification.yaml`, and `handoffs/knowledge_secretary.yaml`.
7. Write post-dispatch placeholder packets under `packets/` only when
   generating a post-dispatch fixture variant.
8. Write `reviews/verification_review.yaml` and `reviews/trace_eval.yaml`
   only for post-dispatch fixture variants.
9. Write `closeout.md` with proven mechanism, failed mechanism, gated next
   work, and recommended next implementation slice.
10. Run the read-only fixture validator when implemented.

Preflight fixtures may include declared output paths without populated result
packets. Post-dispatch fixtures must include either valid packets or valid
blockers for each expected output.

## Negative Fixture Mutation Rules

Every negative fixture should be derived from `valid_minimal` by exactly one
primary mutation unless the fixture expectation says otherwise.

| Fixture | Primary Mutation | Expected Code |
|---|---|---|
| `missing_context_pack` | delete `context_pack.md` | `PREFLIGHT_CONTEXT_PACK_MISSING` |
| `goal_mismatch` | change one handoff canonical goal | `PREFLIGHT_GOAL_MISMATCH` |
| `external_result_path` | set one output path outside project/proof root | `PREFLIGHT_OUTPUT_PATH_UNSAFE` |
| `no_review_node` | remove the workflow review node | `PREFLIGHT_REVIEW_NODE_MISSING` |
| `raw_transcript_context` | add raw transcript marker to context pack | `PREFLIGHT_RAW_TRANSCRIPT_CONTEXT` |
| `forbidden_tool_node` | add a UE/MWORKS/Fab/Git/tool node | `PREFLIGHT_FORBIDDEN_ACTION_SCOPE` |
| `invalid_flat_result_status` | write unsupported result-packet status | `POST_UNSUPPORTED_RESULT_STATUS` |
| `missing_context_delta` | remove post-dispatch context delta | `POST_CONTEXT_DELTA_MISSING` |
| `timeout_without_blocker` | omit an expected packet and blocker | `POST_PACKET_OR_BLOCKER_MISSING` |

If a mutation causes extra structural failures, the validator may report them
as secondary findings, but the expected primary code must remain present.

## Fixture Expectation File

Each fixture should include:

```yaml
fixture_id: valid_minimal
candidate_id: candidate_a_packet_chain
mode: preflight
expected_decision: pass_preflight
expected_codes: []
primary_mutation: none
allowed_secondary_codes: []
forbidden_side_effects:
  - live_dispatch
  - codex_session_create
  - app_server_transport
  - tool_mcp_call
  - git_stage_commit_push
  - worktree_create
  - email_or_desktop_notification
```

Negative fixtures should set `mode`, `expected_decision`, `expected_codes`,
and `primary_mutation` explicitly.

## Path Safety Rules

Generated fixture files may reference only:

- paths inside the fixture directory;
- project-local design paths under `CoAgent/`;
- future proof output paths under `Results/coagent_proofs/`;
- future agent packet paths under `Results/agent_packets/`.

Generated fixtures must not reference:

- `/home/linux/.codex`;
- `/mnt/c/Users/HP/.codex`;
- browser caches, account caches, tokens, SSH paths, provider config, or raw
  session logs;
- any path outside `/mnt/c/Users/HP/Desktop/MoSim`.

The only allowed mention of Codex metadata is a generic statement that Codex
visibility state is not product evidence.

## Dependency Behavior

The fixture generator should not require all validators to exist. It should
still generate fixtures, but its self-check report must classify missing
validators as:

```text
needs_dependency
```

It must not weaken fixture expectations because a dependency is unavailable.

## Manual Review Stop Points

The implementation should stop for user or PMO review if:

1. a generated fixture would need to mention external/private paths;
2. a negative fixture requires multiple primary mutations to fail;
3. expected codes conflict across source documents;
4. a fixture would require live dispatch to validate;
5. a validator tries to repair fixture contents automatically;
6. a proposed fixture expands Candidate A into product-tool work.

## Implementation Slice

This plan should be implemented as a small gated slice:

```text
COAGENT-IMPL-NEXT-24: Candidate A Fixture Generator
```

Suggested scope:

- generate Candidate A fixture directories from shared constants;
- generate `fixture_expectation.yaml`;
- derive negative fixtures by controlled mutation;
- write a read-only self-check report;
- run only local unit tests and validators that already exist;
- do not run live dispatch or tool calls.

Acceptance:

- `valid_minimal` and all listed negative fixtures exist;
- fixture expectations match `candidate_a_fixture_spec.md`;
- generated files stay inside `CoAgent/tests/fixtures/proof_packages/candidate_a/`;
- missing validator dependencies are reported as `needs_dependency`;
- generated fixtures contain no private paths, account caches, raw transcript,
  credentials, live session ids, or external writes;
- no runtime transport, conversation creation, worktree creation, Git
  staging, MCP, UE, MWORKS, Fab, email, or desktop notification is invoked.

## Design Decision

Candidate A should advance in this order:

1. implement shared validator envelope;
2. implement or stub dependency-aware fixture validation;
3. generate Candidate A fixtures from this plan;
4. run fixture validator locally;
5. only then consider live Candidate A multi-conversation proof.

Skipping fixture generation is allowed only if the user explicitly approves a
manual live proof with higher preflight-error risk.
