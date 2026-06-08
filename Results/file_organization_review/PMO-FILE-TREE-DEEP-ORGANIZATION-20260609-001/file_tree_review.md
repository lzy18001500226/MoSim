# PMO File Tree Deep Organization Review 20260609

Scope: project file-tree cleanup only. No MWORKS, ROS2, UE live runtime, visible-thread lifecycle, downstream dispatch, or business model edits were performed.

## Top-Level Root

The project root no longer contains these loose generated or backup directories:

- `.codex-title-backups`: deleted after moving to a deletion-candidate area and confirming it was obsolete Codex title-backup state.
- `build`: moved to `Results/tmp/ros2_colcon_root_outputs_20260609/build`.
- `install`: moved to `Results/tmp/ros2_colcon_root_outputs_20260609/install`.
- `log`: moved to `Results/tmp/ros2_colcon_root_outputs_20260609/log`.

The root now keeps source, docs, models, references, scripts, results, and project config at the top level.

## Docs Cache

`Docs/Cache/session_memory_migration` is now classified by migration stage:

- `00_index`: 3 files. Plan, coverage matrix, and completion audit.
- `01_round1_capture`: 8 files. First-round candidate memory capture.
- `02_round2_review`: 13 files. Second-round evidence review.
- `03_round3_disposition`: 2 files. Promotion/rejection disposition.
- `assets`: 1 file. Non-text evidence asset for the cache.

This removes the previous flat pile of round files while keeping the migration workflow readable from the bottom level.

## Results Root

`Results` root now intentionally keeps only two human-facing entry files:

- `README.md`: Results directory entry.
- `人工审核清单.csv`: human review index.

`Results/tmp_agent_projects_list.txt` was moved to `Results/file_organization_review/legacy_agent_project_lists/tmp_agent_projects_list.txt`.

## Agent Packets

`Results/agent_packets` now keeps workflow lanes at root and moves request/task packets into `tasks/*`.

Stable lanes kept at root:

- `returns`
- `blockers`
- `notifications`
- `manual`
- `maintenance`
- `archive`
- `reviews`
- `summaries`
- `closeouts`
- `tasks`

Task/request packet categories:

- `tasks/architecture_sync`: 1 file.
- `tasks/archived_wechat`: 4 files.
- `tasks/audit`: 5 files.
- `tasks/coagent_architecture`: 4 files.
- `tasks/coagent_devops_git`: 10 files.
- `tasks/coagent_implementation`: 4 files.
- `tasks/coagent_smoke`: 7 files.
- `tasks/mworks`: 90 files.
- `tasks/ops_coagentops`: 8 files.
- `tasks/ops_codex`: 1 file.
- `tasks/reference_learning`: 2 files.
- `tasks/ros2`: 72 files.
- `tasks/sunray_pbr`: 8 files.
- `tasks/ue`: 34 files.

`returns` and `blockers` were not moved because current workflows and expected packet paths use them as stable evidence lanes.

## Results Tmp

`Results/tmp` now has no root-level loose files and no root `tmp*` or `test_p0_slice_*` directories.

Important cleanup categories:

- `ros2_colcon_root_outputs_20260609`: old root `build`, `install`, and `log` generated outputs.
- `p0_test_slice_runs`: formerly root `test_p0_slice_*` temporary directories.
- `random_temp_dirs_20260531_20260606`: formerly root random `tmp*` temporary directories.
- `delegation_launchers_20260606`: loose dispatch helper scripts.
- `ue_*`: UE probes, dry runs, editor probes, renderer probes, and loopback evidence.
- `ros2_*`: ROS2 probe files, adapter smoke files, LiDAR probe files, and Fast-LIO probe files.
- `sunray_dispatch_and_review_tmp`: Sunray dispatch/review temporary files.
- `legacy_*`: older snapshots, research notes, review queues, and model snapshots.
- `session_memory_migration_index_cache`: large generated session-memory index cache.

ROS2 workspaces under `Results/tmp/*_ws` remain in place because scripts and historical command examples may refer to their `install/setup` files.

## Kept Stable By Design

- `Models`, `References`, and `Scripts` were not reorganized in this task; the user identified them as acceptable or already clear enough for now.
- `Results/agent_packets/returns` and `Results/agent_packets/blockers` remain stable current workflow paths.
- Existing high-volume result families such as `Results/agent_runtime`, `Results/coagent_status/git_batches`, and domain evidence folders remain grouped by their current domain. They may need separate deep cleanup, but they are not root-level clutter.

## Verification Notes

- `Results/tmp` loose file count: 0.
- `Results/tmp` root random `tmp*` and `test_p0_slice_*` directory count: 0.
- `Results/agent_packets` loose task/request packet count: 0.
- `Docs/Cache/session_memory_migration` root loose file count: 0.
- `.codex-title-backups`, `build`, `install`, and `log` are absent from project root.

## Residual Follow-Up

- Some historical evidence files may still contain old path strings as historical records. Current operating docs and this review point to the new categories.
- A future task can further normalize tracked historical result families if needed, but this pass fixed the named messy areas and root-level clutter without touching live runtime state.
