# CoAgent DevOps Helpers

This directory owns project-local helper tools for release, Git integration,
and repository hygiene around CoAgent.

Current helper:

```bash
python3 CoAgent/devops/git_batch_plan.py --markdown-output Results/coagent_status/git_batch_plan.md
python3 CoAgent/devops/git_batch_plan.py \
  --markdown-output Results/coagent_status/<task>.git_batch_plan.md \
  --batch-list-dir Results/coagent_status/git_batches/<task>
python3 CoAgent/devops/git_split_index_check.py \
  --paths-file Results/coagent_status/git_batches/<task>/<batch>.staged.paths \
  --output Results/coagent_status/git_batches/<task>/<batch>.split_index_check.json \
  --json
python3 CoAgent/devops/git_split_commit_dry_run.py \
  --batch-list-dir Results/coagent_status/git_batches/<task> \
  --output Results/coagent_status/git_batches/<task>/split_commit_dry_run.json \
  --json
python3 CoAgent/devops/git_split_commit_apply.py \
  --batch-list-dir Results/coagent_status/git_batches/<task> \
  --output Results/coagent_status/git_batches/<task>/split_commit_apply_plan.json \
  --json
```

The helper is read-only. It inspects the current Git index/worktree and groups
CoAgent changes into reviewable batches so large staged sets can be committed
deliberately instead of by broad `git add -A` or one oversized commit.
When `--batch-list-dir` is set, it also writes per-batch path lists plus an
`overlap.paths` file for paths that have both staged and worktree changes.
Use those lists for later small-batch inspection and integration instead of
reconstructing long pathspecs from chat history.

DevOps split tasks must distinguish temporary isolation from completion.
Putting a huge tree behind `.gitignore` is only a throttle that keeps Git usable
while batches are reviewed and committed. Do not report a split task as done
only because `git ls-files --others --exclude-standard` returns 0 or the IDE
source-control view is quiet. Before closeout, audit `.gitignore` and remove or
narrow every temporary broad tree rule unless it is justified as a long-term
ignore for a concrete class: files over GitHub's 100 MiB hard limit,
credentials/secrets, generated/cache/runtime outputs, missing LFS assets, or
manifest-only external materials. If the large surface is already tracked or
appears as 10k+ modifications from a rename/move, `.gitignore` is not a
solution; classify and commit those tracked changes in path-limited batches.

Use the handoff packet when the current Git surface is already broad and needs
DevOps/reviewer ownership before any commit:

```bash
python3 CoAgent/devops/git_handoff_packet.py \
  --task-id COAGENT-IMPL-LONGRUN-20260531 \
  --output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.git_handoff.json \
  --markdown-output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.git_handoff.md
```

The handoff packet is also read-only. It records non-goals, blockers, batch
risks, review gates, inspection commands, verification commands, and path
families. It does not stage, commit, push, create worktrees, or clean files.

Git safety note: do not use `git commit -- <pathspec>` to split commits in the
live worktree when a path has both staged and worktree changes. Git can commit
the current worktree content for that path, not only the already staged version.
Use a temporary-index split builder or first reach a reviewed clean
index/worktree boundary.

`git_split_index_check.py` is the current safe preflight for that temporary
index route. It builds a temporary index under `Results/tmp`, reads HEAD into
it, overlays the current staged object IDs for the declared batch paths, and
runs `git write-tree`. It does not create commits, update refs, mutate the live
index, or touch the worktree.

`git_split_commit_dry_run.py` extends that preflight across all batches in the
review order. It starts from HEAD in a temporary index, applies each batch's
current staged entries, writes the next tree, and records per-batch diff
summaries. It verifies that HEAD and the live index fingerprint are unchanged.
It still does not create commits, update refs, mutate the live index, or touch
the worktree. Like the lower-level checker, it may create unreachable temporary
tree objects through `git write-tree`.
The live-index safety check is based on the live index tree OID, not the raw
`.git/index` file hash, because ordinary read-only Git commands may refresh
index stat-cache metadata without changing the staged tree.

`git_split_commit_apply.py` is the explicit Git-write step. By default it only
builds a split-commit plan and verifies that the live index tree equals the
latest sequential dry-run final tree. With `--apply`, it creates commit objects
for non-empty batches with `git commit-tree`, then performs one guarded
`git update-ref` from the original HEAD to the final split commit. It does not
mutate the live index or worktree. Do not run `--apply` unless the current
batch lists, split-index check, sequential dry-run, and full doctor are fresh.
Plan mode may return `commit_count=0` after the staged surface has already been
integrated; that is a valid clean planning state. Real `--apply` still refuses
to run when there are no non-empty batches.

Avoid running split dry-run/apply-plan commands in parallel with other live
Git commands. They are designed not to write refs, the live index, or the
worktree, but concurrent Git reads can refresh index metadata and make low-level
fingerprint auditing noisy. Use sequential commands for final evidence.
