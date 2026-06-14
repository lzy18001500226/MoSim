# Long-Run Single-Thread Execution Plan

Status: active, 2026-06-12 CST.

Goal: finish the MWORKS simulation, result extraction, metrics, figures/replay,
and evidence gate before moving to UE replay/rendering preparation.

Visible thread dispatch is disabled for this run. Logical sub-agent roles are
planning roles only and run inline in this conversation.

## Critical Path

1. Confirm MWORKS GUI/sentinel state is clean.
2. Rerun the two current `rotor1_loss15` iteration targets.
3. Recalculate quality and single-UAV acceptance.
4. If plain PID/AWFF remain `needs_iteration`, use the accepted rotor-loss
   candidate matrix to pick the next bounded candidate rerun.
5. Close the single-UAV pre-multi-UAV gate or preserve a blocker.
6. Start UE replay/rendering preparation only with accepted or explicitly
   diagnostic MWORKS result inputs.

## Logical Sub-Agent Plan

| Role | Status | Responsibility |
|---|---|---|
| Planner | inline | Maintain the critical path and stop before overclaiming. |
| MWORKS runner | inline | Run bounded MWORKS scenarios and preserve evidence. |
| Quality checker | inline | Run acceptance and closeout gates. |
| UE transition auditor | inline later | Prepare display-only UE replay inputs after MWORKS gate. |

## Current First Targets

- `Config/scenarios/robustness/example1_rotor1_loss15_pid_baseline.yaml`
- `Config/scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml`

## Stop Triggers

- MWORKS login, license, authorization, unknown window, or GUI error surface.
- Missing raw/metrics artifacts after rerun.
- Model or solver failure without preserved logs.
- Any UE step that would require editor/build/runtime without a separate gate.
