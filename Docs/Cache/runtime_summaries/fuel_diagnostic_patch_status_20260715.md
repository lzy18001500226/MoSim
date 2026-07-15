# FUEL Diagnostic Patch Status 2026-07-15

This note prevents the four remaining FUEL diagnostic patch drafts from being
mistaken for reviewed, committable source changes.

## Accepted Patch

`Scripts/sunray/patches/fuel_hard_dynamic_feasibility.patch` is the only patch
from this group with a project-owned application route. It passed both
`git apply --numstat` and `git apply --check` against
`References/Lab/exploration_coverage/FUEL/fuel_planner`, and was committed with
`Scripts/sunray/apply_fuel_dynamic_feasibility_patch.sh` as its owner route.

## Deferred Drafts

| Patch | Current finding | Required recovery |
|---|---|---|
| `fuel_longrun_diagnostic.patch` | Corrupt unified diff; `git apply --numstat` fails at line 6 because several hunks have incomplete headers. | Rebuild from the exact instrumented source and its known base. |
| `fuel_longrun_fsm.patch` | Unified-diff syntax parses, but neither forward nor reverse `git apply --check` succeeds against the project FUEL snapshot. | Identify the exact runtime-source base, then regenerate and verify the patch. |
| `fuel_longrun_manager_stage.patch` | Unified-diff syntax parses, but neither forward nor reverse `git apply --check` succeeds against the project FUEL snapshot. | Identify the exact runtime-source base, then regenerate and verify the patch. |
| `fuel_visualization_gate.patch` | Unified-diff syntax parses, but neither forward nor reverse `git apply --check` succeeds against the project FUEL snapshot. | Identify the exact runtime-source base, then regenerate and verify the patch. |

The related runtime note identifies an external runtime source under
`/opt/mosim_work`, which is outside the project boundary and is not a verified
base for this Git cleanup. Do not stage these four drafts merely to empty the
worktree. Do not ignore them as ordinary generated output. Keep them visible
until a scoped source-reconstruction task produces complete patches that pass
both syntax and target-base checks.
