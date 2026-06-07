# COAGENT-DEVOPS-GIT-REFERENCES-SKILLS-CLOSEOUT-20260606 stage 20260607-c

Status: running

Scope: `References` and `Docs/Skills`, path-limited Git drain.

Pushed batches this stage:

- `c28a2b54cb` `devops: add sdk typescript reference subset` - 675 files.
- `84b2a2fe8b` `devops: add plandex reference subset` - 577 files.
- `07a4b6bc3f` `devops: add superagi reference subset` - 604 files.
- `14fb1dbb26` `devops: add playwright mcp gateway tail` - 28 files.

Checks:

- Each submitted batch stayed under 1000 staged files.
- Each submitted batch passed `git diff --cached --check`.
- No submitted batch had a staged file at or above 100 MB.
- Each submitted batch was pushed to `main`.
- Closeout probe: cached index `0`, `.git/index.lock` absent, upstream ahead/behind `0 0`.

Deferred:

- Third-party upstream whitespace-gate files are recorded under `Results/agent_runtime/*diffcheck_failed*20260607.txt`.
- Local config fixtures, generated outputs, dependency folders, missing-object assets, pointer-only assets, and very large UE/AirSim content remain excluded from normal Git batches.
- `Docs/Skills` remaining ignored inventories are mostly local environments, generated UE intermediate files, or missing-object asset pointers.

Next:

- Continue with small `References/Agent` project groups under 1000 files after filtering generated/local-only outputs.
- Good next targets: narrow `References/Agent/Gateway/cua` slices, split `References/Agent/SDK/openai-cookbook`, or narrower `References/Agent/Memory` candidates.
