# COAGENT-ARCH-LONGRUN-01 Candidate A Manual Rehearsal Plan

Date: 2026-05-30
Status: design plan for supervised rehearsal

## Purpose

Candidate A is the first useful multi-conversation proof, but the validator
and fixture generator are not implemented yet. This document defines a
supervised manual rehearsal path that can be used only if the user accepts the
risk of preflight errors. It prevents an improvised live dispatch from being
mistaken for a validated automated capability.

This is design-only. It does not dispatch conversations, generate proof
packages, create worktrees, call Codex, call MCP, stage Git, or change runtime
schemas.

## Rehearsal Objective

```text
Manually exercise the Candidate A packet-chain shape with explicit human
review and strict stop rules, while recording every gap as evidence for later
validators.
```

The rehearsal should answer one question:

```text
Can the architecture packet chain be followed by visible conversations when
all package files, handoffs, expected outputs, and closeout records are
prepared in advance?
```

It must not answer product questions about PX4, UE, MWORKS, Fab, Git merging,
email delivery, worktree isolation, or unattended automation.

## Preconditions

Manual rehearsal may start only when all are true:

1. `check_department_visibility.py` passes.
2. `task_charter.yaml`, `context_pack.md`, `workflow_graph.yaml`, and handoff
   records exist in a proof package or task-local rehearsal package.
3. The package shape follows `candidate_a_minimal_package_contract.md`.
4. The expected result paths are known before any message is sent.
5. The user approves manual rehearsal despite missing validators.
6. Dispatch records that this is `manual_rehearsal`, not `validated_live_proof`.

If any precondition fails, do not dispatch. Produce a blocker or repair the
package first.

## Rehearsal Package Root

Use a separate output root so manual rehearsal output cannot be confused with
validator fixtures:

```text
Results/coagent_proofs/COAGENT-PROOF-CANDIDATE-A/manual_rehearsal/
```

Required files before dispatch:

```text
task_charter.yaml
context_pack.md
workflow_graph.yaml
handoffs/context_memory.yaml
handoffs/verification.yaml
handoffs/knowledge_secretary.yaml
manual_rehearsal_approval.md
```

Expected files after dispatch:

```text
packets/context_result.txt
packets/knowledge_result.txt
packets/context_delta.yaml
reviews/verification_review.yaml
reviews/trace_eval.yaml
closeout.md
manual_rehearsal_findings.md
```

Blocker files may replace expected outputs only when they follow
`blocker_packet_templates.md`.

## Manual Approval Record

`manual_rehearsal_approval.md` should include:

```text
task_id
candidate_id
approved_by
approval_time
approved_scope
known_missing_validators
known_transport_risks
forbidden_claims
stop_rules
expected_output_paths
```

Forbidden claims must include:

- automated dispatch is proven;
- validator gate is proven;
- fixture generator is proven;
- transport is reliable unattended;
- product workflows are proven;
- result packet contract is fully enforced.

## Manual Dispatch Sequence

Use the smallest visible set:

1. MainAgent reviews package and approval record.
2. DispatchAgent creates mailbox-style task messages or copy/paste packets for
   ContextMemoryAgent, VerificationAgent, and KnowledgeSecretaryAgent.
3. ContextMemoryAgent receives the context handoff and returns either
   `packets/context_result.txt` plus `packets/context_delta.yaml`, or a
   blocker.
4. VerificationAgent receives the same context pack and either writes
   `reviews/verification_review.yaml` plus `reviews/trace_eval.yaml`, or a
   blocker.
5. KnowledgeSecretaryAgent records one promotion candidate, rejected lesson, or
   blocker in `packets/knowledge_result.txt`.
6. DispatchAgent imports or summarizes outputs without repairing their content.
7. MainAgent writes `closeout.md` and `manual_rehearsal_findings.md`.

No step may add UE/MWORKS/Fab/Git/tool/product work.

## Stop Rules

Stop immediately and record a blocker when:

- any expected output path points outside the project or rehearsal root;
- a worker changes the canonical goal;
- a worker asks to run UE, MWORKS, Fab, Git, MCP, email, or worktree commands;
- a result packet is missing after the approved time budget;
- a result packet uses an unsupported status and no invalid-packet blocker is
  recorded;
- context pack contents are stale or include raw transcript/private paths;
- Codex visibility check fails;
- transport times out without a closeout record;
- user intervention is required and the ask is ambiguous.

Do not continue by "just trying again". Retry requires a changed condition and
a blocker/resume record.

## Manual Review Checklist

Before closeout, MainAgent and VerificationAgent should answer:

| Check | Acceptable Evidence |
|---|---|
| canonical goal preserved | all packets cite the same goal or no goal mutation |
| context sufficient | ContextMemoryAgent result or blocker |
| review performed | VerificationAgent review file |
| context lifecycle exercised | context delta exists or proof fails |
| knowledge route tested | promotion/rejection result exists |
| missing instrumentation named | trace eval uses `needs_instrumentation` |
| blockers durable | blocker packets include last safe state and resume condition |
| transport outcome explicit | result, timeout, invalid packet, or blocker recorded |
| no product scope creep | no UE/MWORKS/Fab/Git/tool node executed |

Any failed row becomes a finding. It does not have to invalidate the rehearsal,
but it prevents claiming a clean proof.

## Result Interpretation

| Outcome | Meaning | Next Action |
|---|---|---|
| all packets valid by manual review | manual rehearsal supports validator implementation | implement fixtures/validators next |
| packets need repair | packet instructions or result validator are priority | implement `COAGENT-IMPL-NEXT-11` |
| timeout occurs | transport hardening is priority | implement `COAGENT-IMPL-NEXT-12` |
| context delta missing | context lifecycle checker is priority | implement `COAGENT-IMPL-NEXT-02` |
| blocker is vague | blocker validator is priority | implement `COAGENT-IMPL-NEXT-05` |
| product scope appears | rehearsal is rejected as scope drift | revise package and handoff rules |

## Evidence Labels

Manual rehearsal output must use these labels:

```text
design_only
manual_rehearsal
runtime_metadata
manual_review
```

It must not label output as `validated_live_proof`, `automated_dispatch`,
`UE_MCP`, `MWORKS_MCP`, `MWORKS_GUI`, or `Fab_manual_import`.

## Recommended Default

Default path:

```text
Do not run manual rehearsal yet.
Implement fixture generation and dependency-aware preflight validation first.
```

Manual rehearsal is useful only when the user wants to inspect visible
multi-conversation behavior before implementation. If used, it must be framed
as supervised evidence with known gaps, not proof that the automated CoAgent
runtime is ready.
