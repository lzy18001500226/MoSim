# COAGENT-ARCH-LONGRUN-01 Worktree Git Recovery Validator Design

Date: 2026-05-30
Status: design contract for `COAGENT-IMPL-NEXT-04` and `COAGENT-IMPL-NEXT-18`

## Purpose

Define the read-only validator family that prevents Git-heavy work from
blocking the main task, staging unsafe batches, losing user changes, or
claiming integration readiness without worktree, inventory, review, rollback,
and cleanup evidence.

This design combines:

- `worktree_git_integration_protocol.md`
- `worktree_merge_recovery_experiment_design.md`
- `candidate_d_git_heavy_change_proof_package.md`
- `blocker_packet_validator_design.md`
- `evidence_label_doctor_design.md`
- `validator_shared_envelope_design.md`

It is design-only. It does not create worktrees, run Git commands, stage files,
commit, push, delete, move, repair locks, edit ignore/LFS policy, call tools,
or dispatch DevOps work.

## Core Rule

```text
Git integration starts with inventory and ownership, not staging
```

The validator should decide whether a task is safe in the shared workspace,
requires a worktree, needs DevOps-owned integration, needs user approval, or
must stop because the Git/tool state is unsafe.

## Validator Family

| Validator | Backlog Item | Purpose |
|---|---|---|
| `worktree_binding_validator` | `COAGENT-IMPL-NEXT-04` | validates workspace mode, worktree binding, owners, scopes, base ref, cleanup, conflict policy |
| `git_heavy_change_validator` | `COAGENT-IMPL-NEXT-18` | validates Candidate D inventory, integration plan, risk snapshot, blockers, rollback, and closeout |

Both validators should share `GIT_*` finding codes and the shared validator
report envelope.

## Inputs

The future validators should accept:

```text
--task-id <task id>
--package-root <task or proof package directory>
--mode binding|inventory|integration|closeout|fixture
--json-output <optional path>
```

Input files:

| File | Required For | Purpose |
|---|---|---|
| `task_charter.yaml` | all modes | canonical goal, allowed paths, forbidden paths |
| `change_inventory.md` | inventory, integration, closeout | file counts, path families, binary/generated/source/doc split |
| `worktree_binding.yaml` | binding, integration, closeout | selected workspace mode, owners, scopes, base ref, cleanup |
| `git_risk_snapshot.md` | inventory, integration | large files, locks, slow commands, LFS/ignore state, external paths |
| `integration_plan.yaml` | integration, closeout | staged slice order, review, checks, rollback, blockers |
| `review_packet.yaml` | integration, closeout | accept/rework/block decision |
| `blocker_packet.yaml` | integration, closeout | destructive, large-file, unsafe path, lock, timeout, or approval blocker |
| `closeout.md` | closeout | merged/staged/held/discarded/superseded state and remaining risks |

The validator reads declared package files only. It must not run `git status`
or inspect the live working tree unless a later approved implementation slice
explicitly expands scope.

## Worktree Binding Record

`worktree_binding.yaml` should expose:

```yaml
task_id: COAGENT-ARCH-LONGRUN-01
slice_id: <optional scoped slice>
workspace_mode: shared_workspace | task_worktree | slice_worktree | review_worktree | arena_worktrees | integration_worktree
mode_reason: <why this mode is safe or required>
canonical_task_goal_ref: <task id or path>
worktree_path: <path or null when shared workspace>
base_ref: <branch, commit, or not_applicable>
read_scope:
  - <project path>
write_scope:
  - <project path>
forbidden_paths:
  - <project/external path family>
owners:
  task_owner: DispatchAgent
  merge_owner: DevOpsReleaseAgent
  review_owner: VerificationAgent
  close_owner: DevOpsReleaseAgent
role_waivers:
  - <explicit waiver with reason, if any>
same_file_policy:
  overlaps_detected: false
  integration_owner: <owner or null>
  sequence_plan: <plan or null>
shared_workspace_waiver:
  allowed: false
  reason: <only for low-risk shared workspace>
cleanup_plan:
  state: required | not_required
  close_condition: <how cleanup is verified>
claim_boundaries:
  - <what binding does not prove>
```

The binding record does not authorize creating the worktree. It only records
the decision that a later approved implementation may follow.

## Change Inventory Minimums

`change_inventory.md` or structured equivalent must classify:

- source code;
- documentation;
- design docs;
- generated outputs;
- binary assets;
- local review artifacts;
- external reference material;
- deleted paths;
- renamed paths;
- large-file candidates;
- ignored or untracked scope;
- files outside approved project scope.

For large or volatile changes, inventory should include counts by path family
and a recommended staging/integration slice plan.

## Required Checks

### Workspace Mode

Reject if:

- long or broad task uses shared workspace without a waiver;
- review or integration work lacks clean surface requirement;
- worktree identity is treated as task authority;
- base ref, owner, or cleanup plan is missing when a worktree mode is selected;
- shared workspace waiver omits why conflict, large-file, and broad-stage risk
  are low.

### Scope And Path Safety

Reject if:

- write scope includes the whole repository for a narrow slice;
- external paths are included without explicit approved exception;
- forbidden paths are omitted for Git-heavy work;
- generated, binary, reference, and source files are not separated.

### Role Separation

High-risk Git work must name:

- task owner;
- merge owner;
- review owner;
- close owner;
- safety owner when destructive, credential, external-path, or large-file
  decisions are involved.

Reject role collapse unless an explicit waiver and risk rationale exists.

### Integration Plan

Reject if:

- plan says only `git add -A`;
- slice order is missing;
- same-file overlaps lack sequence, section ownership, or integration owner;
- rollback plan is missing;
- cleanup state is missing;
- checks are not tied to specific slice types;
- user changes during an active slice are not reconciled by refresh/review.

### Blockers

Destructive, large-file, external-path, lock, timeout, or unsafe tool state
must produce a blocker packet or equivalent blocker record.

Reject repeated Git retries when:

- lock state is unresolved;
- command timeout has no closeout;
- LFS/ignore policy is unknown;
- destructive cleanup needs approval;
- the main thread would block on broad Git work.

### Evidence Labels

Git metadata, inventory, and review packets are process evidence. They do not
prove product correctness, successful simulation, tool reliability, or safe
runtime behavior.

Reject label inflation from Git inventory into product proof.

## Decisions

The validator should emit exactly one high-level decision:

| Decision | Meaning |
|---|---|
| `pass_shared_workspace_allowed` | low-risk shared workspace is acceptable |
| `pass_worktree_required` | worktree or isolated surface is required before mutation |
| `pass_inventory_only` | inventory/split plan is safe, but no Git mutation approved |
| `needs_review` | reviewer must accept, rework, or block the integration plan |
| `blocked_user_approval` | destructive, large-file, broad, or policy decision needs PMO/user approval |
| `blocked_tool_state` | Git lock, timeout, LFS, ignore, or command state blocks work |
| `reject_unsafe_plan` | unsafe plan must be replaced before integration |
| `needs_dependency` | required packet, blocker, evidence, tool, or runbook report is absent |

## Stable Finding Codes

| Code | Meaning |
|---|---|
| `GIT_BINDING_MISSING` | worktree binding is missing |
| `GIT_WORKTREE_UNNEEDED` | worktree isolation is proposed without reason |
| `GIT_TASK_WORKTREE_MISSING` | task-level worktree required but absent |
| `GIT_SLICE_SCOPE_UNBOUND` | scoped slice lacks isolated or waived write scope |
| `GIT_REVIEW_SURFACE_MISSING` | review needs clean surface but none is recorded |
| `GIT_INTEGRATION_SURFACE_MISSING` | accepted slices lack integration surface |
| `GIT_WORKTREE_AS_AUTHORITY` | worktree is treated as owner of canonical task goal |
| `GIT_SCOPE_TOO_BROAD` | read/write scope is broader than slice requires |
| `GIT_EXTERNAL_PATH_REJECTED` | external path appears without approval |
| `GIT_INVENTORY_MISSING` | change inventory missing or incomplete |
| `GIT_PATH_FAMILY_UNCLASSIFIED` | path families are not classified |
| `GIT_BROAD_STAGE_REJECTED` | plan relies on broad staging such as `git add -A` |
| `GIT_LARGE_FILE_POLICY_MISSING` | large binary/generated policy missing |
| `GIT_DESTRUCTIVE_APPROVAL_MISSING` | delete, broad move, force, or cleanup lacks approval |
| `GIT_SAME_FILE_OWNER_MISSING` | same-file overlap lacks sequence or integration owner |
| `GIT_ROLE_COLLAPSE_UNWAIVED` | high-risk merge/review/close ownership collapses without waiver |
| `GIT_ROLLBACK_MISSING` | rollback plan missing |
| `GIT_CLEANUP_STATE_MISSING` | cleanup or hold state missing |
| `GIT_LOCK_UNRESOLVED` | lock/index state lacks safe closeout |
| `GIT_TIMEOUT_WITHOUT_CLOSEOUT` | slow/timed-out command lacks blocker or split plan |
| `GIT_USER_CHANGE_UNRECONCILED` | user changes during active slice are not reconciled |
| `GIT_THIRD_PARTY_REFORMAT_RISK` | external/reference source would be mass reformatted |
| `GIT_MAIN_THREAD_BLOCKING` | plan keeps main orchestration thread blocked on broad Git work |
| `GIT_EVIDENCE_LABEL_INFLATED` | Git/process metadata is claimed as product/tool proof |
| `GIT_DEPENDENCY_MISSING` | required validator/report dependency is missing |
| `GIT_FORBIDDEN_SIDE_EFFECT` | validator attempted or declared Git/file mutation |

## Fixture Matrix

Positive fixtures:

| Fixture | Expected |
|---|---|
| small docs edit with shared workspace waiver | `pass_shared_workspace_allowed` |
| broad multi-file task with task worktree binding, owners, cleanup, and no Git mutation | `pass_worktree_required` |
| Candidate D inventory-only package with split plan, blockers for large files, and rollback | `pass_inventory_only` |
| integration plan with same-file sequence and DevOps merge owner | `needs_review` or `pass_inventory_only` by mode |

Negative fixtures:

| Fixture | Expected Codes |
|---|---|
| no binding for long multi-file task | `GIT_BINDING_MISSING`, `GIT_TASK_WORKTREE_MISSING` |
| shared workspace for high-risk batch without waiver | `GIT_TASK_WORKTREE_MISSING` |
| plan says only `git add -A` | `GIT_BROAD_STAGE_REJECTED` |
| binary assets tracked without LFS/ignore/asset policy | `GIT_LARGE_FILE_POLICY_MISSING` |
| external path appears in plan | `GIT_EXTERNAL_PATH_REJECTED` |
| same file edited by two slices without integration owner | `GIT_SAME_FILE_OWNER_MISSING` |
| review owner and merge owner collapse without waiver | `GIT_ROLE_COLLAPSE_UNWAIVED` |
| no rollback or cleanup state | `GIT_ROLLBACK_MISSING`, `GIT_CLEANUP_STATE_MISSING` |
| Git timeout is retried without blocker | `GIT_TIMEOUT_WITHOUT_CLOSEOUT`, `GIT_MAIN_THREAD_BLOCKING` |
| user changes during slice are ignored | `GIT_USER_CHANGE_UNRECONCILED` |
| third-party reference batch is mass-formatted | `GIT_THIRD_PARTY_REFORMAT_RISK` |
| Git inventory claims UE/MWORKS simulation proof | `GIT_EVIDENCE_LABEL_INFLATED` |

## Output

The validator should emit the shared validator envelope, for example:

```json
{
  "schema_version": "coagent.validator_report.v1",
  "validator": "git_heavy_change_validator",
  "task_id": "COAGENT-PROOF-GIT-HEAVY-CHANGE",
  "mode": "integration",
  "decision": "reject_unsafe_plan",
  "ok": false,
  "finding_codes": ["GIT_BROAD_STAGE_REJECTED"],
  "findings": [
    {
      "code": "GIT_BROAD_STAGE_REJECTED",
      "severity": "error",
      "path": "integration_plan.yaml",
      "message": "integration plan uses broad staging instead of reviewed slices",
      "remediation": "replace with path-family inventory and staged slice plan"
    }
  ],
  "dependency_reports": [
    {
      "validator": "blocker_packet_validator",
      "decision": "needs_dependency",
      "required_for": "large-file and destructive-action blockers"
    }
  ],
  "evidence_paths": [
    "CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/worktree_merge_recovery_experiment_design.md"
  ],
  "side_effects": {
    "declared": ["read_project_files", "write_validator_report"],
    "forbidden": ["git_stage", "git_commit", "git_push", "worktree_create", "file_delete", "file_move", "lock_repair"]
  },
  "claim_boundaries": [
    {
      "claim": "Git integration plan is safe",
      "supported": false,
      "limitations": "validator does not stage, commit, push, create worktrees, or prove product correctness"
    }
  ],
  "next_action": "create reviewed path-family slice plan or blocker packet"
}
```

## Implementation Boundary

The first implementation should be read-only and fixture-backed. It may read
project package files and write validator reports under
`Results/coagent_validators/`.

It must not:

- run live Git status/diff/stage/commit/push;
- create or remove worktrees;
- delete, move, rename, or format files;
- edit `.gitignore`, LFS policy, or Git config;
- repair locks or kill Git processes;
- call MCP/tools or dispatch conversations;
- read external paths unless an approved infrastructure exception exists;
- mutate runtime task state;
- send notifications.

Live Git inspection and actual integration remain separate approved DevOps
tasks with explicit scope and user-facing approval when destructive, large,
or external-path decisions are involved.

## Rollout Position

Run the worktree binding validator before any multi-conversation mutable slice
starts. Run the Git-heavy validator before Candidate D, large imports, broad
renames, generated-output batches, or any plan that could otherwise tempt
`git add -A`.

These validators feed:

- runbook readiness;
- implementation approval;
- Candidate D proof closeout;
- blocker packet validation;
- retrospective closure when Git problems recur.
