# COAGENT-ARCH-LONGRUN-01 Candidate D Git Heavy Change Proof Package

Date: 2026-05-30
Status: design blueprint for later Git/DevOps proof

## Purpose

Candidate D tests whether CoAgent can handle a Git-heavy rename, import, or
large reference batch without blocking the main conversation, staging too much,
or corrupting unrelated work.

This is design-only. It does not run broad Git commands, stage files, commit,
push, create worktrees, delete files, or move source trees.

## Proof Goal

```text
Given a large file-change situation, produce an integration package that
classifies changes by path family, assigns ownership, defines staged slices,
records large-file and generated-output policy, and blocks destructive or broad
Git actions until reviewed.
```

## Recommended Future Package Root

```text
Results/coagent_proofs/COAGENT-PROOF-GIT-HEAVY-CHANGE/
```

## Required Inputs

| File | Template Or Source | Purpose |
|---|---|---|
| `task_charter.yaml` | `task_charter.yaml` | canonical goal and non-goals |
| `context_pack.md` | task-local context | current Git policy, write scope, large-change rules |
| `change_inventory.md` | DevOpsReleaseAgent | path families, file counts, binary/generated/source/doc split |
| `worktree_binding.yaml` | `worktree_binding.yaml` | whether worktree is required and who owns integration |
| `integration_plan.yaml` | `integration_plan.yaml` | merge order, checks, rollback, final review |
| `blocker_packet_if_needed.yaml` | `blocker_notification.yaml` | approval, unsafe path, large-file, lock, or auth blocker |

## Required Dynamic Slices

| Slice | Owner | Required Output |
|---|---|---|
| Change Inventory | DevOpsReleaseAgent | path-family inventory and risk classification |
| Scope Review | DispatchAgent + SafetyComplianceAgent | allowed read/write scope and destructive-action gate |
| Slice Plan | DevOpsReleaseAgent | staged integration plan by small reviewed batches |
| Verification Plan | VerificationAgent | checks required before each staged slice |
| Context Delta | KnowledgeSecretaryAgent | reusable Git policy lesson or rejected practice |

## Workflow Graph Shape

```text
charter
  -> context_pack
  -> change_inventory
  -> scope_review
  -> worktree_binding_decision
  -> integration_plan
  -> verification_plan
  -> optional_approval_blocker
  -> closeout
```

No broad staging or commit node is allowed in the proof unless a later
implementation task explicitly approves execution.

## Required Classification

The inventory must classify files by:

- source code;
- documentation;
- generated outputs;
- binary assets;
- local review artifacts;
- external reference material;
- deleted/renamed paths;
- large-file candidates;
- ignored or untracked scope.

The proof must reject a plan that says only `git add -A`.

## Required Blocker Packets

| Blocker | Use When |
|---|---|
| `destructive_action_approval_required` | delete, broad move, force push, history rewrite, bulk cleanup |
| `approval_required` | LFS/ignore policy, staging 1000+ files, large binary tracking |
| `unsafe_path` | target path outside project boundary |
| `tool_unavailable` | Git lock/index corruption, Git command timeout, LFS unavailable |
| `manual_review_required` | user must decide whether to keep, ignore, or split a batch |

## Acceptance Rules

Verification must reject:

- broad `git add -A` across external or generated trees;
- staging large binary assets without LFS/ignore policy;
- deleting or moving broad source/reference trees without explicit approval;
- worktree ownership that lets a worker own the canonical task goal;
- two slices editing the same file without integration owner;
- closeout that lacks rollback or cleanup plan.

The proof can pass without committing if:

- inventory is complete enough to split work;
- risky paths are blocked or excluded;
- merge owner, review owner, and close owner are named;
- checks and rollback are explicit;
- next action is a small approved integration slice.

## Required Outputs

| Output | Meaning |
|---|---|
| `change_inventory.md` | what changed and how it is classified |
| `worktree_binding.yaml` | isolation decision and ownership |
| `integration_plan.yaml` | merge/stage plan, checks, rollback |
| `review_packet.yaml` | acceptance/rework/block decision |
| `blocker_packet.yaml` | if approval or unsafe action is required |
| `closeout.md` | what was proven and what remains gated |

## Result Interpretation

| Outcome | Meaning | Next Action |
|---|---|---|
| inventory-only pass | DevOps can classify the change safely | approve small staging slice |
| worktree required | shared workspace is too risky | approve manual/automated worktree creation later |
| approval blocker | user decision needed before destructive or large-file action | ask one concrete question |
| Git/tool blocker | Git state is unsafe or unavailable | stop Git work and preserve source state |
| scope failure | attempted path exceeds project boundary | stop and escalate safety |

## Design Decision

Candidate D should run as a read-only or dry-run proof first. Real staging,
commit, push, worktree creation, or destructive cleanup must remain separate
approved implementation work.
