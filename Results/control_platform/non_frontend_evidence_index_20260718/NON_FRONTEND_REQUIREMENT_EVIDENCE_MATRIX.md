# Non-Frontend Requirement-Evidence Matrix

更新时间：2026-07-18。此矩阵是当前收尾追踪表，不是把所有需求标记为完成的声明。

- Controller matrix: `{'accepted': 27, 'executed_blocked': 25, 'not_run': 15}`
- Final A/B counts: `{'accepted': 1, 'executed_blocked': 11, 'not_run': 2}`
- Scope: all current non-frontend engineering and submission work

| Requirement | Area | Status | Evidence | Claim ceiling |
|---|---|---|---|---|
| `REQ-MW-01/04/07/11` | MWORKS modeling, code generation, SIL and lifecycle | `verified_at_declared_tier` | `Results/control_platform/classic_controller_closeout_20260717/CLASSIC_CONTROLLER_FINAL_MATRIX.json` | The matrix records implementation, MWORKS/codegen/SIL state per controller; it does not imply Gazebo acceptance for blocked rows. |
| `REQ-CTRL-01..79` | Controller-family coverage | `partial` | `Results/control_platform/classic_controller_closeout_20260717/CLASSIC_CONTROLLER_FINAL_MATRIX.json` | 67 rows are visible: 27 accepted, 25 executed-blocked, 15 not-run; only accepted rows may be presented as selectable Gazebo controllers. |
| `REQ-TRAJ-01..04` | Takeoff, hover, step, figure-eight and spiral scenarios | `partial` | `Results/control_platform/classic_controller_closeout_20260717/CLASSIC_CONTROLLER_FINAL_MATRIX.json`<br>`Results/control_platform/final_controller_ab_20260718/FINAL_CONTROLLER_SEVEN_SCENARIO_AB.json` | Scenario evidence exists across accepted and blocked rows; the A/B matrix is an observed comparison, not a general superiority result. |
| `REQ-ROB-01/03` | Wind and parameter-mismatch robustness | `partial` | `Results/control_platform/final_controller_ab_20260718/FINAL_CONTROLLER_SEVEN_SCENARIO_AB.json`<br>`Results/control_platform/p9_learning_gazebo_r4_20260717/P9_LEARNING_RUNTIME_CLOSEOUT.json` | Wind injection evidence passed for both A/B profiles, but performance rows remain blocked; learning routes show report-worthy wind changes without stable overall superiority. |
| `REQ-FAULT-01/02/07/08/09` | Motor-efficiency fault, FDI, allocation, recovery and landing | `verified_at_declared_tier_with_scope` | `Results/control_platform/p7_ftc_generated_gazebo_r3_20260717/P7_FTC_RUNTIME_CLOSEOUT.json`<br>`Results/control_platform/final_controller_ab_20260718/FINAL_CONTROLLER_SEVEN_SCENARIO_AB.json` | P7 verifies rotor-1 effectiveness 0.65 with generated FDI/isolation/takeover/landing; the two C3 motor-fault A/B rows are not-run and complete outage or multi-fault recovery is not claimed. |
| `REQ-SAFE-01/04/05/06/07/08/09/10` | Safety filter, envelopes, geofence/failsafe and lifecycle safety | `verified_at_declared_tier` | `Results/control_platform/p6_safety_runtime_20260717/P6_SAFETY_RUNTIME_MATRIX.json` | Only the seven declared P6 safety modes are covered; this is not a claim for every optional CBF or reference-governor variant. |
| `REQ-SWARM-01/03/04/07/08` | Three-UAV formation deployment and separation safety | `verified_at_declared_tier` | `Results/control_platform/p8_formation_mode1_gazebo_r7_20260717/PX4CTRL_SWARM_BASIC_METRICS.json` | P8 covers bounded three-UAV formation modes; it does not claim autonomous exploration or every research formation algorithm. |
| `REQ-AI-01/02/05/07/08/10/15` | Fuzzy and learning enhancement routes | `partial` | `Results/control_platform/classic_controller_closeout_20260717/CLASSIC_CONTROLLER_FINAL_MATRIX.json`<br>`Results/control_platform/p9_learning_gazebo_r4_20260717/P9_LEARNING_RUNTIME_CLOSEOUT.json` | Fuzzy PID and selected learning routes are implemented/evidenced at their row ceilings; Neural Residual and RL Gain Scheduler remain selectable=false because strict performance acceptance is blocked. |
| `REQ-EVAL-01..16` | Run IDs, manifests, metrics, logs, figures and failure records | `in_progress` | `Results/control_platform/classic_controller_closeout_20260717/CLASSIC_CONTROLLER_FINAL_MATRIX.json`<br>`Results/control_platform/final_controller_ab_20260718/FINAL_CONTROLLER_SEVEN_SCENARIO_AB.json`<br>`Results/control_platform/p6_safety_runtime_20260717/P6_SAFETY_RUNTIME_MATRIX.json`<br>`Results/control_platform/p7_ftc_generated_gazebo_r3_20260717/P7_FTC_RUNTIME_CLOSEOUT.json`<br>`Results/control_platform/p8_formation_mode1_gazebo_r7_20260717/PX4CTRL_SWARM_BASIC_METRICS.json`<br>`Results/control_platform/p9_learning_gazebo_r4_20260717/P9_LEARNING_RUNTIME_CLOSEOUT.json` | Authoritative runtime evidence exists; final report figures, requirement index and submission package still require C5/C6 completion. |
| `REQ-OSS-01..05` | Upstream version, license and modification audit | `pending_final_qa` | - | Must be checked against the exact final submission paths before publication. |
| `REQ-EVAL-09/11/12/13/14` | Report, reproducibility and submission package | `pending` | - | C5/C6 deliverable; no final-submission-ready claim is allowed until generated and checked. |
| `REQ-UI-01..16` | Frontend, UE/QGC/Flight Console/Model Studio and embedding | `excluded_by_scope` | - | Explicitly excluded from the current non-frontend closeout goal; existing display evidence may be cited only as supporting visualization. |

## Global Claim Boundary

- This matrix is traceability evidence, not a blanket acceptance record.
- accepted, executed_blocked, and not_run remain distinct terminal classes.
- Static, MIL, SIL, screenshots, and metrics-only evidence cannot replace the declared Gazebo/runtime gate.
- Frontend work is excluded and must not block this closeout.

## Next Actions

1. retain the two motor-fault A/B rows as not_run under the versioned infrastructure blocker
2. generate report-ready figures and analysis from authority files
3. refresh manual, demo storyboard, reproducibility manifest and submission package
4. run final quality, license, secret, large-file and exact-path Git publication QA
