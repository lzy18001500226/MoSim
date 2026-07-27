# G1-0 Controller Catalog Reconciliation

Date: 2026-07-28 CST
Scope: read-only reconciliation before the first G1 EquationBridge or Adapter
edit. This is a source/catalog fact record, not a `CheckModel` or simulation
result.

## Source Snapshot

| Source | SHA-256 |
| --- | --- |
| `Config/control_platform/formal_closed_loop_harness_map.json` | `ff2db4157ac04f5a4d3cdf66f4e65994964cb83396b26c2ae4c29ed113b62874` |
| `Config/control_platform/controller_route_interface_matrix.json` | `a6c0b036b679ad97f3ba719e3c78f5f056100ace52f31b89db2c53453def857a` |
| `Config/control_platform/control_scheme_catalog.json` | `07c5a36da6842a06e4b88d5f9b2d887a93c5bf99c36fb5465f17ff3024821f03` |
| `Config/control_platform/extended_control_scope_catalog.json` | `49232d57ce9c46bc49d4331d0e3e11a96c41b74f153b2eff5b88327c3f1997df` |
| `Config/control_platform/offline_composition_catalog.json` | `eddab7dfc7790ef19acbeddb81a902c5600bc5db4ba2399ac422e30a89e2e5d9` |

## Reconciled Counts

| Item | Count | Fact |
| --- | ---: | --- |
| Active catalog entries | 48 | 47 MWORKS profiles plus the `px4ctrl` engineering baseline. |
| Matrix-backed current MWORKS routes | 46 | 41 graphical controller cores and five named integrated whole-aircraft profiles. |
| Planned MWORKS profile without a current model | 1 | `pid_awff_linear_eso`; catalog state is `planned` / `not_runnable`, and it has no route-matrix row or G1 batch. |
| G0 MWORKS closure | 1 | `px4ctrl` is complete at `Results/control_platform/px4ctrl_baseline_verification/`; it is not part of G2. |
| Existing controller-specific formal shells | 7 | `official_pid` plus the six existing nominated paths: `cascade_pid`, `lqr_baseline`, `super_twisting_smc`, `linear_mpc`, `dfbc_high_order_attitude`, and `trained_neural_residual`. |
| Existing whole-aircraft profiles | 5 | `fixed_awff_pid`, `fixed_awff_l1_indi`, `fixed_awff_l1_residual`, `fixed_linear_mpc_l1_indi`, and `fixed_qp_nmpc_l1_indi_cbf`. These use named templates, not a new Adapter/Runner pair. |
| New Adapter/Bridge routes in the approved G1 batches | 32 | B1=7, B2=5, B3=5, B4=6, B5=5, B6=4. `ndi` is only B1. |
| User-approved overview skips | 2 | `smc_boundary_layer` and `nmpc_outer`: their current graphical models have hard-wired probe constants and only a scalar `command` output. No thin Adapter will be manufactured from them in G1. |
| Current-source MWORKS routes that can receive a G2 closure attempt | 44 | `7` existing formal shells + `5` embedded profiles + `32` new G1 routes. This excludes the two skips and the planned ESO item. |

Therefore, the catalog total remains **48**. It must not be reported as 48
completed MWORKS closures: after G1 there can be 44 current-source MWORKS
closure attempts plus the already-completed px4ctrl G0 baseline. Reaching the
literal 47-profile G2 denominator would require a separately authorized real
implementation for `pid_awff_linear_eso` and replacement of both skipped
overview-only entries with executable controller sources.

## Batch Contract

| Batch | Build count | Exact route set | Boundary/template |
| --- | ---: | --- | --- |
| B1 | 7 | `lqi_baseline`, `lqg`, `h2_state_feedback`, `hinf_hover_wrench`, `pole_placement_luenberger`, `mrac`, `ndi` | LQR-style attitude/thrust bridge, DFBC-style acceleration projection, or Wrench as specified below. |
| B2 | 5 | `backstepping_baseline`, `adaptive_backstepping`, `feedback_linearization`, `passivity_based_control`, `fopid` | Attitude/thrust bridge; `fopid` follows direct-output Template A. `ndi` is not repeated. |
| B3 | 5 | `integral_smc`, `terminal_smc`, `nonsingular_terminal_smc`, `adaptive_smc`, `fuzzy_smc` | Attitude/thrust acceleration-projection bridge. `smc_boundary_layer` is skipped. |
| B4 | 6 | `robust_mpc`, `adaptive_mpc`, `tube_mpc`, `explicit_gain_scheduled_mpc`, `ilqr`, `mppi` | Attitude/thrust acceleration-projection bridge. `nmpc_outer` is skipped; `fixed_qp_nmpc_l1_indi_cbf` remains its existing integrated profile. |
| B5 | 5 | `se3_basic`, `dfbc_basic`, `dfbc_smooth_robust_attitude`, `dfbc_smooth_robust_bodyrate`, `dfbc_high_order_bodyrate` | `se3_basic` / `dfbc_basic` use the existing P10 DFBC-family CFunction paths; body-rate entries use `PartialBodyRateThrustController`. |
| B6 | 4 | `gain_scheduled_pid`, `fuzzy_pid`, `neural_pid`, `rl_gain_scheduler` | Build complete cascade shells around the PID/gain-scheduling subblocks before the thin outer Adapter. |

## Route Fact Matrix

`fixed` means the current graphical model has no public trajectory ports and
the EquationBridge must reproduce its law from the graphical model without
mutating that model. `explicit` means the graphical surface already publishes
its interface ports. All target runners use `Sunray150Assembly` and the
shared ClimbPath reference contract.

| Route | Family | Current graphical/whole-aircraft source | I/O and target boundary | Bridge + Adapter / Runner fact | G1 action and dependencies |
| --- | --- | --- | --- | --- | --- |
| `px4ctrl` | engineering baseline | `Control/Implementations/Sysblocks/PX4CTRL_Core_AttitudeThrust_EquationBridge_Sysblock.mo` | `ATTITUDE_THRUST` | Existing `Px4CtrlAttitudeThrustAdapter` / `Px4CtrlFormalRunner` | G0 complete; shared allocator and `Sunray150Assembly`. |
| `official_pid` | PID reference | `PidFamily/AWFF_PID_Sysblock_Demo.mo` | explicit, `ROTOR_COMMAND` | Existing `OfficialPIDRotorAdapter` / `OfficialPidFormalRunner` | Existing baseline; shared rotor runner and Plant. |
| `cascade_pid` | PID | `PidFamily/MoSim_PID_CASCADE_PID_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | Existing `PidAttitudeThrustCFunction`, `CascadePidAttitudeThrustAdapter` / `CascadePidFormalRunner` | Existing nominated path. |
| `lqr_baseline` | linear/robust | `ClassicRobust/MoSim_G5_LQR_DIRECT_GRAPHICAL_MIL.mo` | explicit, `ATTITUDE_THRUST` | Existing `LqrBaselineEquationBridge`, `LqrBaselineAttitudeThrustAdapter` / `LqrBaselineFormalRunner` | Existing nominated path. |
| `super_twisting_smc` | sliding mode | `SlidingMode/MoSim_P3_SUPER_TWISTING_SMC_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | Existing `SuperTwistingSmcCFunction`, `SuperTwistingSmcAttitudeThrustAdapter` / `SuperTwistingSmcFormalRunner` | Existing nominated path. |
| `linear_mpc` | predictive | `Optimization/MoSim_P4_LINEAR_MPC_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | Existing `LinearMpcCFunction`, `LinearMpcAttitudeThrustAdapter` / `LinearMpcFormalRunner` | Existing nominated path. |
| `dfbc_high_order_attitude` | geometric/flatness | `GeometricFlatness/MoSim_G5_DFBC_HIGH_ORDER_ATTITUDE_DIRECT_GRAPHICAL_MIL.mo` | explicit, `ATTITUDE_THRUST` | Existing `DfbcHighOrderEquationBridge`, `DfbcHighOrderAttitudeThrustAdapter` / `DfbcHighOrderFormalRunner` | Existing nominated path. |
| `trained_neural_residual` | learning | `Learning/MoSim_P9_TRAINED_NEURAL_RESIDUAL_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | Existing `TrainedNeuralResidualCFunction`, `TrainedNeuralResidualAttitudeThrustAdapter` / `TrainedNeuralResidualFormalRunner` | Existing nominated path. |
| `fixed_awff_pid` | PID integrated | `Experiment/Templates/IntegratedChains/FixedAwffPid.mo` | whole-aircraft embedded | Existing named template and embedded Sysblock | G2 executes the template; no new Adapter. |
| `fixed_awff_l1_indi` | PID integrated | `Experiment/Templates/IntegratedChains/FixedAwffL1Indi.mo` | whole-aircraft embedded | Existing named template and embedded Sysblock | G2 executes the template; no new Adapter. |
| `fixed_awff_l1_residual` | PID integrated | `Experiment/Templates/IntegratedChains/FixedAwffL1Residual.mo` | whole-aircraft embedded | Existing named template and embedded Sysblock | G2 executes the template; no new Adapter. |
| `fixed_linear_mpc_l1_indi` | predictive integrated | `Experiment/Templates/IntegratedChains/FixedLinearMpcL1Indi.mo` | whole-aircraft embedded | Existing named template and embedded Sysblock | G2 executes the template; no new Adapter. |
| `fixed_qp_nmpc_l1_indi_cbf` | predictive integrated | `Experiment/Templates/IntegratedChains/FixedQpNmpcL1IndiCbf.mo` | whole-aircraft embedded | Existing named template and embedded Sysblock | G2 executes the template; no new Adapter. |
| `lqi_baseline` | linear/robust | `ClassicRobust/MoSim_G5_LQI_DIRECT_GRAPHICAL_MIL.mo` | explicit, `ATTITUDE_THRUST` | New Template A bridge + thin attitude/thrust Adapter + FormalRunner | B1; source has position/velocity/reference/acceleration ports. |
| `lqg` | linear/robust | `ClassicRobust/MoSim_P2_LQG_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | New Template B acceleration bridge + Adapter + FormalRunner | B1; source output is desired acceleration. |
| `h2_state_feedback` | linear/robust | `ClassicRobust/MoSim_G5_H2_STATE_FEEDBACK_DIRECT_GRAPHICAL_MIL.mo` | explicit, `ATTITUDE_THRUST` | New Template A bridge + Adapter + FormalRunner | B1. |
| `hinf_hover_wrench` | linear/robust | `ClassicRobust/MoSim_G5_HINF_HOVER_WRENCH_DIRECT_GRAPHICAL_MIL.mo` | explicit, `WRENCH` | New wrench EquationBridge + `PartialWrenchController` Adapter + FormalRunner | B1; uses `OfflineWrenchAllocator`. |
| `pole_placement_luenberger` | linear/robust | `ClassicRobust/MoSim_G5_POLE_PLACEMENT_LUENBERGER_DIRECT_GRAPHICAL_MIL.mo` | explicit, `ATTITUDE_THRUST` | New Template A bridge + Adapter + FormalRunner | B1. |
| `mrac` | nonlinear/adaptive | `ClassicRobust/MoSim_G5_MRAC_DIRECT_GRAPHICAL_MIL.mo` | explicit, `ATTITUDE_THRUST` | New Template B bridge + Adapter + FormalRunner | B1. |
| `ndi` | nonlinear/adaptive | `ClassicRobust/MoSim_G5_NDI_DIRECT_GRAPHICAL_MIL.mo` | explicit, `ATTITUDE_THRUST` | New Template B bridge + Adapter + FormalRunner | B1 only; duplicate B2 mention removed. |
| `backstepping_baseline` | nonlinear/adaptive | `ClassicRobust/MoSim_G5_BACKSTEPPING_DIRECT_GRAPHICAL_MIL.mo` | explicit, `ATTITUDE_THRUST` | New acceleration-projection bridge + Adapter + FormalRunner | B2. |
| `adaptive_backstepping` | nonlinear/adaptive | `ClassicRobust/MoSim_P2_ADAPTIVE_BACKSTEPPING_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | New Template B bridge + Adapter + FormalRunner | B2; preserve graphical source unchanged. |
| `feedback_linearization` | nonlinear/adaptive | `ClassicRobust/MoSim_P2_FEEDBACK_LINEARIZATION_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | New Template B bridge + Adapter + FormalRunner | B2. |
| `passivity_based_control` | nonlinear/adaptive | `ClassicRobust/MoSim_P2_PASSIVITY_BASED_CONTROL_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | New Template B bridge + Adapter + FormalRunner | B2. |
| `fopid` | PID | `ClassicRobust/MoSim_G5_FOPID_DIRECT_GRAPHICAL_MIL.mo` | explicit, `ATTITUDE_THRUST` | New Template A bridge + Adapter + FormalRunner | B2; direct fractional PID output path. |
| `integral_smc` | sliding mode | `SlidingMode/MoSim_P3_INTEGRAL_SMC_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | New acceleration-projection bridge + Adapter + FormalRunner | B3. |
| `terminal_smc` | sliding mode | `SlidingMode/MoSim_P3_TERMINAL_SMC_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | New acceleration-projection bridge + Adapter + FormalRunner | B3. |
| `nonsingular_terminal_smc` | sliding mode | `SlidingMode/MoSim_P3_NONSINGULAR_TERMINAL_SMC_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | New acceleration-projection bridge + Adapter + FormalRunner | B3. |
| `adaptive_smc` | sliding mode | `SlidingMode/MoSim_P3_ADAPTIVE_SMC_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | New acceleration-projection bridge + Adapter + FormalRunner | B3. |
| `fuzzy_smc` | sliding mode | `SlidingMode/MoSim_P3_FUZZY_SMC_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | New acceleration-projection bridge + Adapter + FormalRunner | B3. |
| `smc_boundary_layer` | sliding mode | `SlidingMode/MoSim_G9_SMC_BOUNDARY_LAYER_GRAPHICAL_OVERVIEW.mo` | fixed constants, scalar command only | No Adapter or FormalRunner in G1 | Explicit user skip; available P10 CFunction is not substituted without a new scope decision. |
| `robust_mpc` | predictive | `Optimization/MoSim_P4_ROBUST_MPC_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | New acceleration-projection bridge + Adapter + FormalRunner | B4. |
| `adaptive_mpc` | predictive | `Optimization/MoSim_P4_ADAPTIVE_MPC_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | New acceleration-projection bridge + Adapter + FormalRunner | B4. |
| `tube_mpc` | predictive | `Optimization/MoSim_P4_TUBE_MPC_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | New acceleration-projection bridge + Adapter + FormalRunner | B4. |
| `explicit_gain_scheduled_mpc` | predictive | `Optimization/MoSim_P4_EXPLICIT_GAIN_SCHEDULED_MPC_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | New acceleration-projection bridge + Adapter + FormalRunner | B4. |
| `ilqr` | predictive | `Optimization/MoSim_P4_ILQR_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | New acceleration-projection bridge + Adapter + FormalRunner | B4. |
| `mppi` | predictive | `Optimization/MoSim_P4_MPPI_GRAPHICAL_MIL.mo` | fixed, `ATTITUDE_THRUST` | New acceleration-projection bridge + Adapter + FormalRunner | B4. |
| `nmpc_outer` | predictive | `Optimization/MoSim_G9_NMPC_OUTER_GRAPHICAL_OVERVIEW.mo` | fixed constants, scalar command only | No Adapter or FormalRunner in G1 | Explicit user skip; available P10 CFunction is not substituted without a new scope decision. |
| `se3_basic` | geometric/flatness | `GeometricFlatness/MoSim_G9_SE3_GRAPHICAL_OVERVIEW.mo` | fixed overview, `ATTITUDE_THRUST` target | Existing P10 DFBC-family CFunction controller-id 2, new thin Adapter + FormalRunner | B5; the P10 core, not the hard-wired overview, is the executable source. |
| `dfbc_basic` | geometric/flatness | `GeometricFlatness/MoSim_G9_DFBC_GRAPHICAL_OVERVIEW.mo` | fixed overview, `ATTITUDE_THRUST` target | Existing P10 DFBC-family CFunction controller-id 3, new thin Adapter + FormalRunner | B5; the P10 core, not the hard-wired overview, is the executable source. |
| `dfbc_smooth_robust_attitude` | geometric/flatness | `GeometricFlatness/MoSim_G5_DFBC_SMOOTH_ROBUST_ATTITUDE_DIRECT_GRAPHICAL_MIL.mo` | explicit, `ATTITUDE_THRUST` | New DFBC-family bridge + Adapter + FormalRunner | B5. |
| `dfbc_smooth_robust_bodyrate` | geometric/flatness | `GeometricFlatness/MoSim_G5_DFBC_SMOOTH_ROBUST_BODYRATE_DIRECT_GRAPHICAL_MIL.mo` | explicit, `BODY_RATE_THRUST` | New DFBC-family bridge + `PartialBodyRateThrustController` Adapter + FormalRunner | B5; uses `OfflineBodyRateAllocator`. |
| `dfbc_high_order_bodyrate` | geometric/flatness | `GeometricFlatness/MoSim_G5_DFBC_HIGH_ORDER_BODYRATE_DIRECT_GRAPHICAL_MIL.mo` | explicit, `BODY_RATE_THRUST` | New DFBC-family bridge + `PartialBodyRateThrustController` Adapter + FormalRunner | B5; uses `OfflineBodyRateAllocator`. |
| `gain_scheduled_pid` | PID | `PidFamily/MoSim_PID_GAIN_SCHEDULED_PID_GRAPHICAL_MIL.mo` | fixed PID subblock, `ATTITUDE_THRUST` target | New cascade composition + thin Adapter + FormalRunner | B6; not a standalone vehicle controller. |
| `fuzzy_pid` | PID | `PidFamily/MoSim_PID_FUZZY_PID_GRAPHICAL_MIL.mo` | fixed PID subblock, `ATTITUDE_THRUST` target | New cascade composition + thin Adapter + FormalRunner | B6; not a standalone vehicle controller. |
| `neural_pid` | PID | `PidFamily/MoSim_PID_NEURAL_PID_GRAPHICAL_MIL.mo` | fixed PID subblock, `ATTITUDE_THRUST` target | New cascade composition + thin Adapter + FormalRunner | B6; not a standalone vehicle controller. |
| `rl_gain_scheduler` | learning | `Learning/MoSim_P9_RL_GAIN_SCHEDULER_GRAPHICAL_MIL.mo` | fixed scheduler subblock, `ATTITUDE_THRUST` target | New cascade composition + thin Adapter + FormalRunner | B6; scheduler must retain a deterministic fallback. |
| `pid_awff_linear_eso` | PID | no current `.mo` source | no route / no boundary | No EquationBridge, Adapter, or Runner exists | Planned/not runnable. It is outside B1-B6 until a real graphical implementation is approved. |

## G2 and G3 Acceptance Contract

1. G2 creates a controller-specific FormalRunner for every newly built
   Adapter and runs each of the 44 reconciled current-source MWORKS routes on
   the common 50 s `ClimbPath`.
2. Every attempt writes `pass` or `fail`, `position_rmse_m`,
   `terminal_position_error_norm`, and a concrete failure reason to
   `Results/control_platform/phase2_full_47_climbpath/`. The directory name is
   retained from the user instruction; the manifest must state the actual
   reconciled denominator rather than implying 47 runs.
3. G3 may only repair numerical divergence, an interface defect, or terminal
   position error above 5 m. It may not tune for comparative performance.
4. Do not start seven-scenario A/B, code export, Gazebo/ROS validation, G7,
   R1, or performance gain tuning before every reconciled G3 row has a final
   record and the user provides the next instruction.
