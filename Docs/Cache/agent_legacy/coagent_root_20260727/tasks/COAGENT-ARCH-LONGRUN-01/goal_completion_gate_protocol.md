# COAGENT-ARCH-LONGRUN-01 Goal Completion Gate Protocol

Date: 2026-05-30
Status: design gate for final long-run audit

## Purpose

The active goal is a long architecture-design goal, not a runtime
implementation goal. At the same time, it must not be closed just because many
documents exist. This protocol defines the final completion gate for
`COAGENT-ARCH-LONGRUN-01` so the user audit can decide completion by evidence,
not by activity volume or optimism.

This is design-only. It does not mark the goal complete, implement validators,
run live proofs, create conversations, call tools, stage Git, or change runtime
schemas.

## Completion Boundary

The goal may be completed only for this claim:

```text
CoAgent architecture design is ready for user audit and next implementation
approval.
```

The goal must not be completed for these claims unless separate evidence later
proves them:

- unattended multi-conversation execution works;
- Candidate A live proof passed;
- PX4 parameter identification is operational;
- UE scene truth is operational;
- Git-heavy merge automation works;
- auth/license interruption automation works;
- validators, fixture generators, mailbox replay, or metrics snapshots are
  implemented;
- app-server transport, auto conversation creation, auto worktree creation, or
  email notification are enabled.

## Completion Inputs

Final audit must inspect the current state of:

- `task_charter.md`;
- `goal_requirement_audit_map.md`;
- `ten_hour_audit_package.md`;
- `review_brief.md`;
- `shared_task_board.md`;
- `architecture_problem_matrix.md`;
- `post_design_implementation_backlog.md`;
- runtime task state from `mosim_agent_runtime.py show`;
- department packets and blockers under `Results/agent_packets/`;
- transport findings under `Results/coagent_transport/runs/`;
- latest command outputs from the required audit commands.

Chat memory is not completion evidence. It can only help locate files.

## Requirement Verdicts

Each active goal requirement receives one verdict:

| Verdict | Meaning | Can Close Design Goal? |
|---|---|---|
| `design_pass` | design requirement is coherently covered by current artifacts | yes |
| `design_pass_with_gated_followup` | design exists and remaining work is an implementation/proof slice with owner and gate | yes |
| `partial_design` | design is started but important decisions, owners, or acceptance rules are missing | no |
| `contradicted` | evidence conflicts with the claim or violates safety/scope | no |
| `missing` | no authoritative artifact proves the requirement | no |
| `user_deferred` | user explicitly accepts deferral as outside this design goal | yes, only with recorded decision |

`design_pass_with_gated_followup` is allowed because this task's objective is
architecture design. It is not allowed for missing design content. It is allowed
only when the remaining gap is a named later implementation, live proof,
validator, or user-decision item.

## Mandatory Design Requirements

All of these must be `design_pass`, `design_pass_with_gated_followup`, or
`user_deferred` before the goal can close:

1. task-first architecture;
2. multi-conversation and multi-agent collaboration;
3. dynamic task team routing;
4. context and memory indexing;
5. cross-conversation communication;
6. worktree and Git merge strategy;
7. review and testing gates;
8. safety boundaries;
9. human intervention;
10. external intelligence learning;
11. self-evolution mechanism;
12. reviewable architecture documents;
13. problem matrix and decision tradeoffs;
14. minimal closed-loop design;
15. department dispatch results or explicit blockers;
16. next-stage implementation breakdown;
17. ten-hour user audit package.

The list mirrors `goal_requirement_audit_map.md`. If the active goal changes,
this list must be updated instead of silently narrowing the audit.

## Evidence Strength Rules

Use this hierarchy:

1. current command output;
2. runtime task state and event records;
3. project-owned result, blocker, review, and transport packets;
4. task-local architecture design files;
5. indexed decision/backlog/status files;
6. chat memory.

Only levels 1-5 can prove completion. Level 6 cannot.

Design files can prove design requirements. They cannot prove runtime
capabilities. Runtime capabilities require packets, logs, validators, tests, or
live proof records.

## Accepted Gated Follow-Up Requirements

For a `design_pass_with_gated_followup`, the audit must name:

```text
requirement
design artifact
remaining gap
backlog item or proof candidate
owner
acceptance gate
forbidden claim
```

Example:

```text
Requirement: cross-conversation communication
Design artifact: mailbox_ledger_and_replay_design.md
Remaining gap: checker/replay not implemented
Backlog: COAGENT-IMPL-NEXT-23
Owner: DispatchAgent + VerificationAgent
Acceptance gate: valid Candidate A mailbox chain replays to one next safe action
Forbidden claim: durable mailbox transport is implemented
```

If any of these fields are missing, use `partial_design`.

## Final Audit Commands

Run before final closeout:

```bash
python3 CoAgent/doctor/check_department_visibility.py
python3 CoAgent/doctor/check_design_gate.py
python3 CoAgent/tests/test_design_surface_docs.py
python3 CoAgent/runtime/mosim_agent_runtime.py show --task-id COAGENT-ARCH-LONGRUN-01
git diff --check -- CoAgent/tasks/COAGENT-ARCH-LONGRUN-01 CoAgent/STATUS.md PROGRESS.md
```

If a command fails:

- map the failure to a known blocker/backlog item if it is outside design
  scope;
- fix it if it contradicts current design-state claims;
- do not close if the failure makes a mandatory design requirement
  unverifiable.

Recurring Codex visibility drift may be repaired only through the registered
`sync-visible --apply` path for active department threads. Unknown sessions,
provider config, credentials, or broad Codex history must not be modified.

## Closeout Artifact

Before marking the goal complete, write or update:

```text
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/final_goal_completion_audit.md
```

Required sections:

```text
Objective
Audit Time
Command Results
Requirement Verdict Table
Accepted Gated Follow-Ups
Rejected Or Forbidden Claims
Remaining Implementation Queue
User Review Decisions
Completion Decision
```

`Completion Decision` may be:

- `complete_design_goal`;
- `needs_design_rework`;
- `needs_user_decision`;
- `blocked_by_external_state`.

Only `complete_design_goal` allows `update_goal(status="complete")`.

## Completion Decision Rules

Use `complete_design_goal` only when:

- the minimum 10-hour appetite has elapsed or the user explicitly accepts the
  delivered audit earlier;
- every mandatory requirement has an allowed verdict;
- every implementation/proof/runtime gap is named as gated follow-up;
- required commands pass or failures are mapped to accepted blockers;
- no forbidden claim is present in `review_brief.md`, audit map, status, or
  final summary;
- `final_goal_completion_audit.md` exists and points to authoritative evidence;
- the user-facing summary clearly separates design completion from runtime or
  implementation completion.

Use `needs_design_rework` when:

- a requirement is missing or partial;
- the problem matrix has stale contradictions;
- a stress-test flow lacks owners, gates, or acceptance rules;
- next implementation work is too broad to review safely.

Use `needs_user_decision` when:

- a design branch depends on user direction;
- a deferral changes project strategy;
- the user must choose whether manual rehearsal, implementation, or live proof
  comes next.

Use `blocked_by_external_state` only when the strict blocked-audit rule is met.

## Forbidden Completion Shortcuts

Do not mark complete because:

- many documents exist;
- checks pass but do not cover a requirement;
- the 10-hour duration elapsed;
- the user is absent;
- implementation backlog exists but design artifacts are incomplete;
- a manual rehearsal was planned but not approved;
- department conversations are visible;
- Candidate A is specified but not audited against this protocol.

## Design Decision

The goal is complete only when the architecture-design package is coherent,
auditable, and honest about remaining implementation/proof gaps. Runtime
automation gaps may remain open, but they must be named, owned, gated, and
explicitly excluded from the completion claim.
