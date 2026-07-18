# Non-Frontend Submission Package Manifest

Status: `package_boundary_audit_not_published`
Candidate files: `3450`
Missing required paths: `0`
Files over 100 MB: `0`
Package boundary ready: `True`

## Tracked Include Roots

- `Config`
- `Models`
- `Scripts/control_platform`
- `Scripts/mworks`
- `Scripts/quality`
- `Scripts/sunray`
- `Scripts/tests`

## Exclude Roots

- `apps/flight_console`
- `apps/model_studio`
- `UE5`
- `References`
- `.git`
- `Results/native_result_cache`
- `Results/agent_runs`
- `Docs/Cache/agent_legacy`

## Required Paths

| Path | Exists | Kind |
|---|---|---|
| `AGENTS.md` | True | `file` |
| `Docs/user_manual.md` | True | `file` |
| `Docs/Workflows/pre_submit_check.md` | True | `file` |
| `Docs/Workflows/mainline_operations_board.md` | True | `file` |
| `Docs/Workflows/sunray_ros1_current_runtime_lane.md` | True | `file` |
| `Docs/Workflows/sunray_ros1_execution_checklist.md` | True | `file` |
| `Models` | True | `directory` |
| `Config/control_platform` | True | `directory` |
| `Scripts/control_platform` | True | `directory` |
| `Scripts/sunray` | True | `directory` |
| `Results/control_platform/non_frontend_evidence_index_20260718/NON_FRONTEND_REQUIREMENT_EVIDENCE_MATRIX.json` | True | `file` |
| `Results/control_platform/non_frontend_evidence_index_20260718/NON_FRONTEND_REPORT_SOURCE.json` | True | `file` |
| `Results/control_platform/non_frontend_evidence_index_20260718/NON_FRONTEND_DELIVERY_MANIFEST.json` | True | `file` |

## Publication Actions

1. Review the exact candidate list before materializing the package.
2. Run license/source audit for selected References or third-party code before inclusion.
3. Run secret, path, and dependency checks on the final selected slice.
4. Materialize and publish only after exact-path review; this manifest does not do so.

## Claim Boundary

- This is a package-boundary audit, not a final submission package.
- It does not copy, delete, stage, commit, push, or publish files.
- A package can contain blocked evidence as long as its status and claim ceiling are preserved.
