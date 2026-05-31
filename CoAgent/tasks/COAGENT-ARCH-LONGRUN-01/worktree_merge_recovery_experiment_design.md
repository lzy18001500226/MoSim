# COAGENT-ARCH-LONGRUN-01 Worktree Merge Recovery Experiment Design

Date: 2026-05-30
Status: design-only experiment plan

## Purpose

Turn the current worktree and Git policy into a concrete experiment design for
large, conflicting, slow, or risky Git work.

This document covers the user-facing failure mode where a task produces huge
renames, imports, generated outputs, large assets, lock files, or same-file
conflicts and the main conversation loses hours inside Git instead of keeping
the engineering task moving.

## Boundary

This is design-only. It does not:

- create Git worktrees;
- stage files;
- commit or push;
- delete, move, or rewrite user files;
- run `git add -A`;
- repair Git locks;
- call external tools;
- automate DevOpsReleaseAgent dispatch.

The experiment is a future read-only or dry-run proof. Real Git operations
remain separately approved implementation work.

## Covered Problems

| Problem | How This Experiment Covers It |
|---|---|
| P08 worktree mapping | tests when no worktree, task worktree, slice worktree, review worktree, and integration worktree are required |
| P09 large Git changes | tests inventory-first handling for imports, renames, generated outputs, binaries, and large files |
| P37 Git-heavy proof | turns Candidate D into deterministic scenarios and validator outcomes |
| P62 merge recovery | adds recovery-specific cases for conflicts, locks, broad staging, cleanup, and owner collapse |

## Experiment Goal

```text
Given a simulated Git-heavy task state, CoAgent can decide the correct
workspace mode, produce a safe integration plan, block unsafe Git actions,
assign review/merge/close owners, and recover to the next safe action without
using broad staging or hiding unresolved Git state.
```

## Required Inputs

| Input | Required Fields |
|---|---|
| `task_charter.yaml` | task id, canonical goal, non-goals, allowed paths, forbidden paths |
| `change_inventory.md` | path families, counts, deleted/renamed paths, generated/binary/source/docs split |
| `worktree_binding.yaml` | selected mode, read scope, write scope, base ref, owner, cleanup plan |
| `integration_plan.yaml` | slice order, merge owner, review owner, checks, rollback, blocker policy |
| `git_risk_snapshot.md` | large files, locks, slow commands, LFS/ignore state, external paths |
| `review_packet.yaml` | accept/rework/block decision and evidence |
| `closeout.md` | merged/staged/held/discarded/superseded state and remaining risk |

## Scenario Matrix

| ID | Scenario | Expected Decision | Required Finding If Wrong |
|---|---|---|---|
| GIT-001 | Small project-owned docs edit with no conflict risk | shared workspace, no worktree | `GIT_WORKTREE_UNNEEDED` if it creates isolation without reason |
| GIT-002 | Long task may edit many project files over time | task worktree required before implementation approval | `GIT_TASK_WORKTREE_MISSING` |
| GIT-003 | Scoped conversation edits disjoint files | slice worktree or explicit shared-workspace waiver | `GIT_SLICE_SCOPE_UNBOUND` |
| GIT-004 | Reviewer needs clean comparison | review worktree or clean read-only checkout requirement | `GIT_REVIEW_SURFACE_MISSING` |
| GIT-005 | DevOps integrates accepted slices | integration worktree or equivalent isolated integration plan | `GIT_INTEGRATION_SURFACE_MISSING` |
| GIT-006 | Two slices edit the same file | sequence work, split sections, or assign integration owner | `GIT_SAME_FILE_OWNER_MISSING` |
| GIT-007 | Plan says only `git add -A` | reject plan | `GIT_BROAD_STAGE_REJECTED` |
| GIT-008 | Large binary or generated tree appears | block until LFS/ignore/asset policy is approved | `GIT_LARGE_FILE_POLICY_MISSING` |
| GIT-009 | External path appears in staging plan | reject and escalate safety | `GIT_EXTERNAL_PATH_REJECTED` |
| GIT-010 | Delete or broad move is requested | blocker packet with exact target and approval ask | `GIT_DESTRUCTIVE_APPROVAL_MISSING` |
| GIT-011 | Git status/diff is slow or times out | stop broad Git, record blocker, split inventory | `GIT_TIMEOUT_WITHOUT_CLOSEOUT` |
| GIT-012 | `index.lock` or equivalent lock residue exists | stop Git, preserve source state, require DevOps/Safety review | `GIT_LOCK_UNRESOLVED` |
| GIT-013 | Merge owner and reviewer collapse for high-risk change | reject or require explicit waiver | `GIT_ROLE_COLLAPSE_UNWAIVED` |
| GIT-014 | Worktree cleanup is missing from closeout | hold closeout | `GIT_CLEANUP_STATE_MISSING` |
| GIT-015 | Accepted work has no rollback plan | reject integration readiness | `GIT_ROLLBACK_MISSING` |
| GIT-016 | User changes files while slice is active | pause integration, refresh inventory, require conflict review | `GIT_USER_CHANGE_UNRECONCILED` |
| GIT-017 | Third-party source has whitespace/style issues | do not mass-format; scope checks or record upstream state | `GIT_THIRD_PARTY_REFORMAT_RISK` |
| GIT-018 | Git operation would block main thread | route to DevOps/GitIntegrator task and keep main critical path moving | `GIT_MAIN_THREAD_BLOCKING` |

## Workspace Mode Decision Rules

| Condition | Mode |
|---|---|
| Read-only research or tiny docs edit | shared workspace |
| One long task changes many project-owned files | task worktree |
| One conversation owns disjoint write scope | slice worktree |
| Independent review/test needs clean state | review worktree |
| Competing approaches require comparison | arena worktrees |
| Accepted slices need integration and conflict resolution | integration worktree |

If the mode is `shared workspace`, the package must record why conflict,
large-file, and broad-stage risk are low.

## Recovery State Machine

```text
inventory_pending
  -> mode_selected
  -> integration_plan_ready
  -> review_ready
  -> merge_ready | blocked | rework_required
  -> integrated | staged_pending | held | discarded | superseded
  -> closeout_recorded
```

Blocked states must include:

- last safe state;
- exact command or proposed action that failed or was rejected;
- affected paths;
- owner;
- user action if required;
- resume condition;
- safe parallel work decision.

## Required Output Decisions

Every experiment run must produce exactly one high-level decision:

| Decision | Meaning |
|---|---|
| `pass_inventory_only` | inventory and split plan are safe; no Git action taken |
| `pass_worktree_required` | worktree isolation is required before implementation |
| `pass_shared_workspace_allowed` | shared workspace is acceptable with recorded waiver |
| `needs_review` | safe enough to continue only after reviewer decision |
| `blocked_user_approval` | destructive, broad, large-file, or policy choice needs user approval |
| `blocked_tool_state` | Git lock, timeout, LFS, or command state blocks Git work |
| `reject_unsafe_plan` | plan attempts unsafe broad stage, external path, missing owner, or missing rollback |

## Validator Contract For Later Implementation

Future `COAGENT-IMPL-NEXT-04` and `COAGENT-IMPL-NEXT-18` should share this
contract:

- read package files only;
- never stage, commit, push, delete, move, or create a worktree;
- reject missing role separation for high-risk changes;
- reject worktree identity as task authority;
- reject integration plans without rollback and cleanup;
- emit stable `GIT_*` finding codes;
- report dependency gaps as `needs_dependency`;
- write a JSON report and a short Markdown summary.

## Relationship To Candidate D

`candidate_d_git_heavy_change_proof_package.md` defines the proof-package
shape. This document defines the recovery experiment and negative scenarios
that make that proof testable.

Candidate D should not execute real Git. It should prove the decision logic
for when Git work is safe, when DevOps must take over, and when the user must
approve or unblock a risky operation.

## Relationship To Human Review

MainAgent asks the user only when the package has reduced the question to one
concrete decision, such as:

```text
Approve tracking this large binary batch through LFS, or keep it ignored and
document it as local review material?
```

It should not ask vague questions like:

```text
What should I do about Git?
```

## Acceptance For This Design Slice

This design slice is acceptable when:

- P08, P09, P37, and P62 point to this experiment;
- the task board records the artifact;
- the final audit and goal audit include the new Git recovery evidence;
- the implementation backlog separates worktree-binding validation from
  Candidate D Git-heavy validation;
- verification commands pass.
