# COAGENT-ARCH-LONGRUN-01 Candidate A Proof Package Design

Date: 2026-05-30
Status: design blueprint for later validator or live proof

## Purpose

This document defines the proof package that must exist before running
Candidate A. The package turns the packet-chain blueprint into concrete files
and negative cases so the later proof tests the architecture rather than
inventing rules during execution.

This is design-only. It does not authorize live dispatch, automatic
conversation creation, automatic worktree creation, app-server transport,
email, UE/MWORKS/Fab execution, or broad Git operations.

## Package Root

Recommended future proof root:

```text
Results/coagent_proofs/COAGENT-PROOF-CANDIDATE-A/
```

This path is an execution output path for a later approved proof. The current
design task should only describe the package.

## Required Package Inputs

The exact minimal file and field contract is now defined in:

```text
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_minimal_package_contract.md
```

This document remains the proof-package design overview. The minimal package
contract is the source of truth for fixture generation and required fields.

| File | Template Or Source | Purpose |
|---|---|---|
| `task_charter.yaml` | `CoAgent/protocol/templates/task_charter.yaml` | canonical goal, non-goals, owner, close condition |
| `workflow_graph.yaml` | `CoAgent/protocol/templates/workflow_graph.yaml` | deterministic proof graph and required review nodes |
| `handoff_context.yaml` | `CoAgent/protocol/templates/handoff_mode.yaml` | Dispatch to ContextMemoryAgent |
| `handoff_verify.yaml` | `CoAgent/protocol/templates/handoff_mode.yaml` | Dispatch to VerificationAgent |
| `handoff_knowledge.yaml` | `CoAgent/protocol/templates/handoff_mode.yaml` | Dispatch to KnowledgeSecretaryAgent |
| `context_pack.md` | task-local curated context | compact worker context, not raw transcript |
| `result_packet_instruction.md` | `result_packet_contract_hardening.md` | flat text result packet contract |

## Required Package Outputs

| File | Producer | Required Meaning |
|---|---|---|
| `packets/context_result.txt` | ContextMemoryAgent | context sufficiency result or blocker |
| `packets/verify_review.yaml` | VerificationAgent | review decision and required rework if any |
| `packets/knowledge_result.txt` | KnowledgeSecretaryAgent | promotion candidate or rejected-idea result |
| `packets/context_delta.yaml` | ContextMemoryAgent or KnowledgeSecretaryAgent | at least one context change, stale notice, or lesson candidate |
| `packets/trace_eval.yaml` | VerificationAgent | process metrics and missing instrumentation |
| `closeout.md` | MainAgent + DispatchAgent | what was proven, what failed, what remains gated |

Result packets that target the current result router must use the flat text
packet contract. Review, context-delta, and trace-eval packets may use their
existing YAML templates if the later validator supports them explicitly.

## Workflow Graph Shape

Candidate A should have this minimum graph:

```text
charter
  -> context_review
  -> dispatch_context_result
  -> verification_review
  -> knowledge_promotion
  -> trace_eval
  -> closeout
```

Allowed parallelism:

- `verification_review` and `knowledge_promotion` may run in parallel after
  `context_review` if both receive the same context pack version;
- `closeout` must wait for all required packets or blocker packets.

Forbidden graph changes during proof:

- adding UE/MWORKS/Fab nodes;
- adding Git merge nodes;
- adding worktree creation nodes;
- adding automatic conversation creation nodes;
- changing the canonical goal from packet-chain proof to product work.

## Required Validation Checks

Before dispatch, a future validator should check:

1. `task_charter.yaml` has task id `COAGENT-PROOF-CANDIDATE-A`.
2. Canonical goal matches the Candidate A blueprint.
3. Non-goals include gated automation and product-tool exclusions.
4. Every handoff has `task_id`, `canonical_task_goal`, `context_pack_path`,
   `expected_result_packet_path`, `review_gate`, `return_path`, and
   forbidden-action coverage.
5. Every workflow node has owner, objective, input packet, output packet, and
   terminal-state plan.
6. Required result paths are unique and stay under the proof root or
   `Results/agent_packets/`.
7. Context pack excludes raw full transcript and secrets.
8. Review owner is `VerificationAgent`.
9. Context delta is mandatory.
10. Trace eval metrics include all required fields from
    `candidate_a_packet_chain_blueprint.md`.

After dispatch, a future validator should check:

1. every required worker produced either a valid output packet or a valid
   blocker packet;
2. at least two non-MainAgent packets were imported or explicitly blocked;
3. no packet mutated the canonical goal;
4. context delta is acknowledged or explicitly marked no-ack;
5. review decision is terminal;
6. closeout lists proven mechanism, failed mechanism, gated next work, and
   recommended next implementation slice.

## Negative Fixtures

The later validator should include these failing cases:

| Fixture | Expected Finding |
|---|---|
| missing `context_pack_path` in handoff | reject before dispatch |
| expected result path outside `Results/` | reject before dispatch |
| handoff has no review gate | reject before dispatch |
| workflow node changes canonical goal | reject before dispatch |
| context pack includes raw transcript | reject before dispatch |
| result packet uses nested YAML or custom status | reject or require repair |
| no context delta produced | proof fails |
| missing trace metric with no `needs_instrumentation` marker | proof fails |
| worker attempts UE/MWORKS/Fab/Git operation | proof blocks as scope violation |
| timeout without blocker packet | proof blocks as transport failure |

## Candidate A Result Interpretation

| Outcome | Meaning | Next Action |
|---|---|---|
| pass without packet repair | packet chain is strong enough for PX4 or UE gate proof | choose Candidate B or C |
| pass with packet repair | architecture is right, contract enforcement is weak | implement result-packet validator |
| preflight package fails | live proof is premature | implement proof-package validator |
| timeout with blocker | transport is still weak | implement transport timeout hardening |
| no context delta | context lifecycle not tested | revise proof package |
| review rejects evidence | proof output is not auditable | tighten charter and fixtures |

## Design Decision

Candidate A should be treated as a proof package first and a live
multi-conversation dispatch second. The next safe implementation slice is a
proof-package validator or fixture generator. Running the proof before that is
possible only with explicit user approval and should still use this package
shape.
