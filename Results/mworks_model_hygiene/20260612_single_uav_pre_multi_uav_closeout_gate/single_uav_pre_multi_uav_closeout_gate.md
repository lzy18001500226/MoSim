# Single-UAV Pre Multi-UAV Closeout Gate

Status: `single_uav_gate_ready_for_ue_prep`
Decision: `prepare_ue_replay_inputs_directly_when_user_authorized`

Read-only gate. It does not run MWORKS and does not authorize formation work.

## Current State

- Batch acceptance: `needs_iteration`; 11 accepted, 2 need iteration.
- Live MWORKS gate: `clean_preflight_available`.
- Rotor1 accepted candidates: `1`.
- Best rotor1 candidate: `linear_mpc_online_fault_allocation_sysblock` rmse=`0.167569`, health=`62.536015`.
- Current candidate rerun evidence: `current_rerun_accepted`; metrics=`Results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_linear_mpc_online_fault_allocation_sysblock/metrics/robust_rotor1_loss15_example1_linear_mpc_online_fault_allocation_sysblock.json`.

## Required Before Multi-UAV

- If the user has authorized this thread to continue, proceed to UE replay/render input preparation without waiting for PMO idleness.
- Prepare a UE replay/render input bundle from the accepted raw CSV, metrics JSON, replay JSON, and scene/map contract.
- Do not open UE editor/runtime/build or claim UE runtime success until the UE workflow gate authorizes that scope.
- Keep final report acceptance separate from engineering continuation; terminal report wording still needs its own final acceptance gate.
- If report wording needs current baseline comparison, rerun the two plain PID/AWFF rotor1_loss15 scenarios and acceptance checker.
- Keep the remaining needs-iteration rotor1_loss15 rows visible as negative or iteration evidence.

## Claim Boundary

- This closeout gate is read-only and does not run MWORKS itself.
- Current-rerun readiness is inferred only from metrics/raw artifacts, source labels, quality gates, and clean-sentinel timing.
- It may prepare UE replay inputs, but it does not authorize UE editor/runtime/build work.
- It does not start or authorize multi-UAV formation work.
- It does not grant final report acceptance.
