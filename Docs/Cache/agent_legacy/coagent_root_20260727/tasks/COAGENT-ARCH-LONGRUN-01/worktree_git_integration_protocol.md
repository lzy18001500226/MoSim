# COAGENT-ARCH-LONGRUN-01 Worktree And Git Integration Protocol

Date: 2026-05-30
Status: phase 2 draft

## Purpose

Define how CoAgent handles file isolation, Git ownership, merge gates, and
large-change safety when multiple conversations work under one task.

## Core Rule

```text
worktree = file isolation surface
task = authority surface
conversation = execution surface
DevOps = integration owner
```

A worktree never owns the task goal.

## Default Modes

| Mode | Use When | Owner |
|---|---|---|
| shared workspace | small docs/design changes, no conflict risk | current task owner |
| task worktree | one long task may change many files | Dispatch + DevOps |
| slice worktree | one scoped conversation edits isolated files | slice owner + DevOps |
| review worktree | independent review/test needs clean view | Verification or DevOps |
| arena worktrees | bounded competing approaches need comparison | Dispatch + Verification |
| integration worktree | merging accepted slices | DevOpsReleaseAgent |

## Worktree Creation Gate

Before creating a worktree, record:

- task id;
- parent task goal;
- conversation owner;
- read scope;
- write scope;
- base branch or commit;
- merge owner;
- review owner;
- expected artifact paths;
- close condition;
- cleanup plan.

Do not create a worktree for read-only research unless a clean checkout is
needed for reproducibility.

## Merge Gate

DevOpsReleaseAgent may integrate a slice only when:

- result packet exists;
- review packet accepts or explicitly waives review;
- write scope matches actual diff;
- large files are checked;
- generated artifacts are intended;
- no secrets or local credentials are present;
- required checks pass or failure is documented;
- rollback plan exists for high-risk changes.

## Large-Change Policy

For large imports, renames, generated outputs, or external reference batches:

1. Inventory first.
2. Ignore or keep untracked by default.
3. Stage reviewed slices only.
4. Avoid `git add -A` across broad external trees.
5. Separate source, generated, binary, and documentation changes.
6. Record large-file decisions before staging.
7. Use LFS/ignore policy only after review.

## Same-File Conflict Policy

If two slices may edit the same file:

- Dispatch must sequence them, or
- split by section with explicit ownership, or
- assign one integration owner to edit the file after result packets arrive.

Do not let two scoped conversations independently patch the same design source
without an integration plan.

## Git Ownership

| Git Action | Owner |
|---|---|
| inspect status/diff | task owner or DevOps |
| broad staging | DevOps only |
| commit | DevOps or main agent after scoped review |
| push | DevOps or main agent if auth works |
| force push/history rewrite | user explicit approval only |
| cleanup after interrupted broad operations | DevOps + Safety if risk exists |

## Recovery

If Git is slow, huge, locked, or unclear:

1. stop broad Git operations;
2. record current command and state;
3. inventory changed files by path family;
4. split into smaller integration tasks;
5. ask user only if destructive cleanup or external state is required.

## Closeout

A worktree-bound slice closes when:

- diff is merged, discarded, or archived;
- result packet and review packet are linked;
- context delta is accepted or rejected;
- integration queue state is updated;
- worktree cleanup state is recorded.
