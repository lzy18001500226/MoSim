# COAGENT-ARCH-LONGRUN-01 Proof Ladder And Validator Order

Date: 2026-05-30
Status: design consolidation

## Purpose

CoAgent now has several proof-package designs. This document keeps them in one
ordered ladder so future work does not jump into high-risk product automation
before the communication, context, review, and blocker mechanisms are proven.

## Proof Ladder

| Candidate | Proof | Primary Risk Tested | Default Order |
|---|---|---|---|
| A | Architecture packet chain | multi-conversation communication, context delta, result/review/trace packet chain | first |
| B | PX4 parameter identification | data sufficiency, identifiability, evidence labeling, optional simulation gate | after A |
| C | UE scene truth | scene source, UE/MCP capability, planning truth versus rendering, manual import blockers | after A |
| D | Git-heavy change | large change inventory, worktree/integration policy, broad staging/destructive blockers | after A or before any large Git work |
| E | Auth/license interruption | blocker/resume semantics, exact PMO user ask, retry circuit breaker, safe parallel work | before notifications or unattended tool loops |

## Common Proof Package Contract

Every proof package should define:

- package root under `Results/coagent_proofs/<proof-id>/`;
- task charter;
- context pack;
- workflow graph;
- handoff records where multiple conversations are used;
- required input artifacts;
- required output packets;
- blocker packet classes;
- review owner;
- trace evaluation;
- closeout;
- non-goals and forbidden actions;
- pass, block, and rejection rules;
- follow-on decision table.

## Shared Preflight Checks

A future validator should reject a proof package before live dispatch when:

1. canonical task goal is missing or differs across files;
2. context pack path is missing;
3. workflow graph has no review node or closeout node;
4. result packet paths are missing or outside approved output roots;
5. forbidden actions are absent for a high-risk proof;
6. owner, reviewer, or integration owner is missing;
7. required template files are not referenced;
8. a product proof lacks evidence-label rules;
9. a Git/tool proof lacks blocker classes;
10. raw transcript, secrets, or external private paths are included as context.

## Shared Post-Dispatch Checks

After live dispatch, a future validator should reject or block when:

1. required packet is missing and no blocker packet exists;
2. result packet uses unsupported status or nested YAML when routed through the
   current flat contract;
3. canonical goal is mutated by a worker;
4. context delta is missing for a proof that should test context lifecycle;
5. review decision is non-terminal;
6. trace metrics omit fields without `needs_instrumentation`;
7. an open blocker is hidden in risks but task is marked complete;
8. product evidence is claimed from design-only material;
9. manual review is substituted for tool/product truth;
10. closeout lacks next action or gated follow-on decision.

## Validator Implementation Order

Recommended order:

1. `COAGENT-IMPL-NEXT-11`: result packet contract hardening.
2. `COAGENT-IMPL-NEXT-15`: Candidate A proof-package validator.
   Use `candidate_a_fixture_spec.md` as the fixture source of truth.
3. `COAGENT-IMPL-NEXT-13`: handoff mode and workflow graph validators.
4. `COAGENT-IMPL-NEXT-02`: context delta template/checker.
5. `COAGENT-IMPL-NEXT-09`: read-only operating metrics snapshot.
6. `COAGENT-IMPL-NEXT-12`: transport timeout and plugin-sync hardening.
7. Product proof validators:
   - `COAGENT-IMPL-NEXT-16`: Candidate B PX4;
   - `COAGENT-IMPL-NEXT-17`: Candidate C UE.
8. Operational-risk validators:
   - `COAGENT-IMPL-NEXT-18`: Candidate D Git-heavy change;
   - `COAGENT-IMPL-NEXT-19`: Candidate E auth/license interruption.

Reason:

- invalid result packets already caused real repair work;
- Candidate A is the lowest-risk multi-conversation proof;
- handoff/workflow/context validators are shared infrastructure;
- metrics and transport hardening reduce long-run drift;
- PX4/UE/Git/auth proofs should build on the shared packet chain.

## When To Deviate From The Order

Allowed deviations:

- run Candidate D before B/C if the user starts a large rename/import/Git
  cleanup task;
- run Candidate E before B/C if MWORKS, UE/Fab, or Codex transport hits a real
  login/license/manual-review blocker;
- run Candidate C before B if UE scene truth becomes the product bottleneck;
- run Candidate B before C if PX4 parameter work becomes the product
  bottleneck.

Not allowed without explicit approval:

- enabling unattended dispatch before transport timeout hardening;
- enabling email/desktop notification before Candidate E semantics are proven;
- running UE/MWORKS/Fab tool loops under Candidate A;
- broad Git staging under Candidate D proof design;
- claiming product readiness from a design-only proof.

## Review Questions For The User

At audit time, ask:

1. Is Candidate A the right first live proof?
2. Should PX4 (B) or UE (C) be the first product-adjacent proof after A?
3. Should Git-heavy change handling (D) be moved earlier because the repository
   is already noisy?
4. Should auth/license interruption (E) be tested before any MWORKS/UE work?
5. Which implementation slice should be approved first: packet validator,
   proof-package validator, context delta checker, metrics snapshot, or
   transport hardening?

## Design Decision

The proof ladder is now the default bridge from architecture design to
implementation. New task types should either fit one existing candidate, extend
the common proof-package contract, or create a new candidate with the same
preflight, post-dispatch, blocker, review, and closeout discipline.
