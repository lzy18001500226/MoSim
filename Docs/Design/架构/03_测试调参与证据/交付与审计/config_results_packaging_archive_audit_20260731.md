# Config / Results Packaging Archive Audit

> Date: 2026-07-31 CST
> Scope: non-destructive packaging preparation for `Config/` and `Results/`.
> Machine-readable companion: `Docs/Design/架构/03_测试调参与证据/交付与审计/config_results_packaging_archive_manifest_20260731.json`.

## Decision

The deliverable must be split into a source package and one or more evidence
packages. The repository `.gitignore` excludes `Results/`, so cloning the
source alone does not reproduce the evidence set. This audit therefore does
not move, delete, rename, or rewrite existing configuration or result files.

The categories used below are:

- `keep_in_source_release`: required for the project-owned source package.
- `keep_in_evidence_bundle`: required to substantiate the current MWORKS
  delivery claims; copy it with hashes into an explicit evidence package.
- `retain_immutable_history`: preserve as trace-back or negative evidence, but
  keep it outside the minimal release bundle.
- `archive_candidate_after_dependency_audit`: candidate for a separate archive
  only after all code, document, and result references are replaced or pinned.
- `owner_locked`: belongs to the separately owned runtime/UI lane; this thread
  may not move or prune it.
- `exclude_from_source_release`: local transport, capture, cache, or generated
  state. Excluding it from a release is not permission to delete it.

## Config Classification

| Classification | Paths | Packaging decision | Reason / gate |
|---|---|---|---|
| `keep_in_source_release` | `Config/control_platform/`, `Config/profiles/`, `Config/plant/`, `Config/schemas/`, `Config/codegen/`, `Config/project_paths.json` | Include in the source package. | Contains the Studio task-route authority, interface contract, v2 experiment profiles, model entry map, plant profiles, schemas, and code-generation schema. Run the static manifest validator before bundling. |
| `keep_in_source_release` | `Config/scenarios/planning/`, `Config/scenarios/formation/` | Include while the corresponding MWORKS model and runner sources are included. | These are the project-owned planning/formation scenario surfaces. Do not infer live runtime acceptance from their presence. |
| `archive_candidate_after_dependency_audit` | `Config/controllers/`, `Config/scenarios/official/`, `Config/scenarios/robustness/`, `Config/scenarios/diagnostics/` | Keep in the repository now; prepare one compatibility archive batch with the matching legacy results. | The old Example1 scenarios and controller directories are still named by quality/compatibility scripts. Their archive must update or pin those references first. |
| `archive_candidate_after_dependency_audit` | `Config/legacy/`, `Config/protocol/` | Retain until the remaining capability and protocol references have a static replacement. | They are governance/legacy compatibility assets, not evidence of a current live session. |
| `owner_locked` | `Config/gazebo/`, `Config/runtime/`, `Config/ros2/`, `Config/rviz/`, `Config/rviz2/`, `Config/planners/`, `Config/scenarios/system/`, `Config/scenarios/ui/` | Exclude from the MWORKS-only source package unless their owner approves a joint release. Do not move or prune. | They are consumed by the separately owned ROS/Gazebo/PX4/QGC/visualization lanes. |

`Config/control_platform/mworks_app_entrypoints.json` remains a historical
design reference inside the source package. It must not be used as the active
Studio route selector; `model_studio_task_routes_v1.toml` remains authoritative.

## Results Classification

### Current MWORKS evidence bundle

The following paths are the minimum explicit current-evidence bundle. Preserve
their native result files, raw data, metrics, screenshots, run configuration,
and run record where present. Copy with SHA-256 manifests rather than relying
on Git:

| Evidence role | Paths |
|---|---|
| G2/G3 status | `Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_STATUS.json`, plus the immutable parent `phase2_full_48_climbpath/` record tree |
| Seven-scenario v2 A/B | `Results/control_platform/seven_scenario_ab_v2/SCENARIO_RMSE_MATRIX.pending_syslab.json` and its bound run records |
| Sensitivity | `Results/control_platform/sensitivity_analysis_long_v1/SENSITIVITY_LONG_V1_CLOSEOUT.json`, `Results/control_platform/sensitivity_wind_v1/SENSITIVITY_BATCH_STATUS.json` |
| px4ctrl model-to-C evidence | `Results/control_platform/px4ctrl_baseline_verification/`, `Results/control_platform/px4ctrl_graphical_completion_20260728/`, `Results/control_platform/px4ctrl_codegen_sil_v1/logs/CLOSED_LOOP_SIL_RESULT.json` |
| Current MWORKS multi-UAV review | `Results/control_platform/px4ctrl_three_uav_figure8_v1/`, `Results/planning/three_uav_openblocks_px4ctrl_ecbf_safety_20260731/` |
| Pending controller evidence | `Results/control_platform/pid_awff_linear_eso_baseline_20260731/`, `Results/control_platform/hinf_hover_wrench_repair_20260730/`, `Results/control_platform/tier1_formal_promotion_20260731/` |

An unsuccessful record is still evidence. In particular, retain the original
G2 records, the v1 Official PID motor-fault diagnostic, and invalid v2
rotor-fault records. They must not be removed merely because a shorter release
bundle is desired.

### High-confidence archive candidates

| Candidate batch | Paths | Current observation | Required preconditions before any move |
|---|---|---|---|
| Legacy Example1 robustness process artifacts | `Results/robustness/` paired with `Config/controllers/` and `Config/scenarios/robustness/` | Ten `Example1` directories dated 2026-05 contain 218 SVG figures and mixed CSV/JSON/JSONL/MSR process outputs. They are not named by the current P0 evidence ledger or release checklist. | Produce a per-file SHA-256 manifest, retain a tombstone README/index at the original location, then update or pin the scripts that still refer to the paired configuration tree. |
| Historical controller batch results | Individual legacy children under `Results/control_platform/` such as pre-2026-07 G5/P-series/wave batches and `champion_candidate_recovery_20260727/` | The root mixes current delivery evidence, valid historical trace-back, and negative records. | Never move the root as a whole. Generate a child-level reference manifest and preserve all source/result bindings before selecting archive candidates. |
| Local tool state and old transport traces | `Results/tmp/`, `Results/cache/`, `Results/agent_*`, `Results/coagent_*`, `Results/codex_*`, `Results/context_packs/`, `Results/browser_captures/`, `Results/mworks_*capture/`, `Results/mworks_gui_*` | These directories are ignored by Git and are not part of the source release. Some may be active-task evidence. | Check active task references and retain only hash-bound captures cited by a durable result index. Delete nothing in this audit. |
| Quarantine/download/research workspaces | `Results/_quarantine/`, `Results/_scratch_stage_contract_probe/`, `Results/external_downloads/`, `Results/external_learning/`, `Results/paper_text_extracts/` | Local intake and research material, not current release evidence. | Confirm license/provenance and downstream references; then archive externally or retain a manifest only. |

### Owner-locked results

Do not repackage, archive, or prune these paths from this MWORKS/controller
thread: `Results/sunray_ros1/`, `Results/gazebo_*`, `Results/px4_gazebo/`,
`Results/ros2_*`, `Results/ue_*`, `Results/unreal_*`, `Results/ui/`,
`Results/ui_platform/`, and `Results/runs/`. They belong to the separate
runtime/UI ownership lane or include its live artifacts.

## Packaging Sequence

1. **B0 - Freeze manifests.** Run
   `Scripts/quality/validate_config_results_packaging_archive.py` and save its
   output under `Results/final_submission/`. Do not alter listed paths.
2. **B1 - Source package.** Include the `keep_in_source_release` Config paths,
   project-owned model/source trees, documentation, and the release checklist.
   Exclude `Results/` from the source archive by design.
3. **B2 - Evidence package.** Copy the selected current MWORKS evidence paths
   with a SHA-256 inventory and preserve directory-relative layout.
4. **B3 - Historical archive.** Perform a separate, reviewable move/copy task
   for one candidate batch at a time. Each batch needs a dependency report,
   hash manifest, archive destination, and original-location tombstone.
5. **B4 - Owner handoff.** Request the ROS/Gazebo/QGC/UI owner's decision for
   their Config/Results trees. Do not infer approval from file age.

## Materialized Archive Record

The first low-risk batch was materialized on 2026-07-31 as a verified external
copy. This is an archive receipt, not a source deletion or an evidence-status
change.

### Archive-Root Update (2026-08-10)

The C: paths in the 2026-07 receipt tables below are original historical
locations, not the current default archive root. New archive batches must use
`E:\刘致远18001500226\MoSim_Archive\<archive-id>\` according to
[`external_archive_policy.md`](../Workflows/external_archive_policy.md).

The verified reconciliation receipt is
`E:\刘致远18001500226\MoSim_Archive\20260810_desktop_archive_reconciliation\`.
Its manifest records a copy-only, source-retained transfer of 349 files
(1,605,933,452 bytes), with zero missing files and zero source or destination
SHA-256 mismatches. It explicitly records that source deletion is not
authorized.

| Field | Value |
|---|---|
| Archive candidate | `legacy_example1_robustness_pair` |
| Original archive location (legacy) | `C:\Users\HP\Desktop\MoSim_Archive\202605_example1_robustness\` |
| Included source-relative roots | `Results/robustness/`, `Config/controllers/`, `Config/scenarios/robustness/` |
| Copy mode | Copy only; all original repository files remain in place. |
| Verified content | 577 files, 398,562,113 bytes, source/destination SHA-256 checked per file. |
| External manifest | `ARCHIVE_MANIFEST.json`, SHA-256 `a00023774517b688a34cb837467e6ceb667cddbf08d6eab6b3098b95ae0f17b6` |
| Archive-side recovery metadata | `SHA256SUMS.txt` and `ARCHIVE_README.md` |

The external archive keeps repository-relative paths below its root. A later
removal from the working repository still requires the dependency audit,
original-location tombstone, and explicit review described above. The copy is
therefore a packaging-safe recovery point, not authorization to delete the
legacy sources or historical results.

## Claim Boundary

This document organizes packaging inputs only. It does not assert that a
controller passed, that a live MWORKS model is accepted, or that any
ROS/Gazebo/PX4/QGC/UE runtime route is complete.

## Follow-up Archive Execution

> Executed on 2026-07-31 after a direct user-authorized dependency audit.
> This section records only external archival of untracked local data. No
> tracked configuration, Modelica model, active evidence record, or
> owner-locked runtime/UI path was moved or rewritten.

### Completed external archives

| Archive ID | Original archive location (legacy) | Verified content | Source result |
|---|---|---:|---|
| `20260731_local_unreferenced_cache_phase1` | `C:\Users\HP\Desktop\MoSim_Archive\20260731_local_unreferenced_cache_phase1\` | 16,753 files; 2,621,010,763 bytes | All five source roots were SHA-256 verified, removed, and replaced by `ARCHIVED_EXTERNALLY.md` tombstones. |
| `20260731_historical_mworks_unreferenced_phase2` | `C:\Users\HP\Desktop\MoSim_Archive\20260731_historical_mworks_unreferenced_phase2\` | 345 files; 254,350,491 bytes | Fourteen of fifteen historical, untracked MWORKS-result roots were SHA-256 verified, removed, and tombstoned. |

The phase-1 manifest SHA-256 is
`8c130c5e8af1db3629e40f78a6d4e3350de2e712a314f9d32c0b15e29f1c29e6`.
The phase-2 manifest SHA-256 after recovery finalization is
`435cf3bf33ac7effd3bae4d8429af17ee6dd6d512f571f6ace38a4ff7dd5bd29`.
Both archives retain repository-relative file paths, `ARCHIVE_MANIFEST.json`,
`SHA256SUMS.txt`, and `ARCHIVE_README.md`.

### Retained blockers

| Path | Decision | Reason |
|---|---|---|
| `Results/research/` | Retain in working tree and external archive. | Its embedded legacy `.git/objects/pack` object rejected deletion with Windows access-denied. Its verified external copy exists, but the source root is deliberately left intact until a separate filesystem-repair cleanup is approved. |
| `Results/_quarantine/` and the five historical control-platform roots containing broken reparse points | Retain in working tree. | The dependency scan found inaccessible Windows reparse points. Do not delete or move them with ordinary cleanup tooling; handle only through a dedicated, path-by-path repair task. |

### Config decision after dependency scan

No `Config/` tree was moved. `Config/controllers/`,
`Config/scenarios/robustness/`, `Config/legacy/`, and `Config/protocol/` still
have direct project script, source, or document references; moving any of them
would make the packaged project incomplete. The current source release must
therefore retain the `keep_in_source_release` paths in this audit and preserve
the listed compatibility configuration until a future reference-rewrite task.

### Clean-package readiness

The current working tree cannot be released by packaging the entire Git tree.
The static audit observed 327,607 tracked files and 29,009,905,286 bytes:
`References/` alone accounts for 24,737,305,041 bytes, while tracked
`Results/`, `UE5/`, and `Config/` account for 958,823,818, 773,885,530, and
324,222,431 bytes respectively. A release needs an explicit B1 source-package
allowlist and a separate hash-bound B2 evidence package; do not use a bare
`git archive` or a whole-directory zip as the delivery artifact.

The audit also found 115 tracked-but-missing report figures, all below
`Docs/figures/第10章/`. They do not block loading the model package or Studio,
but they do block a claim that the report-figure bundle is complete. Resolve
that separate report-worktree state before publishing a final delivery archive.
