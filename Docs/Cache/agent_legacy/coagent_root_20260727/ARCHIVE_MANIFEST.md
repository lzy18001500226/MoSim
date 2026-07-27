# CoAgent Root Archive Manifest

> Archive record for the retired root-level CoAgent material. This is a path
> archive only: no file content, runtime behavior, or active project entry
> point was changed.

## Baseline

```text
baseline_commit: df19d3373d2eb58c544d833fa9a21ca46ff0b165
source_tree: CoAgent
source_tree_object: d3c58220bd95ec44dd6944ab379ca0c77b585a6b
tracked_file_count: 330
tracked_byte_count: 3040680
archive_path: Docs/Cache/agent_legacy/coagent_root_20260727
git_change_classification: R100 path-only renames
```

## Scope And Verification

- All 330 tracked files were moved mechanically from `CoAgent/` to this
  archive path and verified as 100 percent Git renames.
- The repository root no longer exposes `CoAgent/` as an active project entry.
  Git does not track the remaining empty directory skeleton.
- No MWORKS, ROS, Gazebo, PX4, MAVROS, QGC, UE, controller, planner, or replay
  runtime was started for this archive.
- This archive preserves historical trace-back material only. It must not be
  restored as an active multi-thread or automation route without an explicit
  dependency audit and user approval.

## Local Cache Handling

The 26 untracked Python bytecode cache files found under the former root were
not deleted. They were moved unchanged to the local-only cache location below
and are intentionally outside the archive's tracked file count:

```text
build/legacy_local_cache/coagent_root_20260727/
```

## Follow-Up Boundary

Factory L2, `build/`, `.tools/`, `image/`, and ROS workspaces were reviewed
separately. Their current consumers or evidence roles prevent a direct move or
deletion in this task; see `Docs/Workflows/project_structure_refactor.md`.
