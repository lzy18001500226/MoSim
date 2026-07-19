# 控制器文档证据静态盘点（67项）

状态：静态文件盘点，不代表MWORKS现场验收。

- 权威矩阵：`Results/control_platform/classic_controller_closeout_20260717/CLASSIC_CONTROLLER_FINAL_MATRIX.json`
- 路线数：`67`
- 状态计数：`{"accepted": 27, "executed_blocked": 33, "not_run": 7}`
- 已有模型源码：`60`
- 已有图形模型截图：`50`
- 已有结果查看器截图：`39`
- 已有数值结果或指标：`62`
- 仓库内可见Result.msr：`4`
- 实现阻塞：`2`

## 边界

- This inventory is a static file-presence audit and does not run MWORKS.
- Graphical model screenshots and result-viewer screenshots are separate evidence classes.
- CSV or JSON evidence is not promoted to native Result.msr evidence.
- A blocked or negative result remains valid report evidence when its provenance is preserved.

## 逐项状态

| 家族 | 路线 | 矩阵状态 | 模型 | 图形截图 | 结果截图 | 数值结果 | MSR | 下一步 |
|---|---|---|---:|---:|---:|---:|---:|---|
| P1_PID | cascade_pid | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P1_PID | anti_windup | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P1_PID | feedforward_profile | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P1_PID | gain_scheduled_pid | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P1_PID | fuzzy_pid | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P1_PID | neural_pid | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P2_LINEAR_ROBUST | lqg | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P2_LINEAR_ROBUST | feedback_linearization | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P2_LINEAR_ROBUST | passivity_based_control | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P2_LINEAR_ROBUST | adaptive_backstepping | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P3_SLIDING_MODE | integral_smc | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P3_SLIDING_MODE | terminal_smc | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P3_SLIDING_MODE | nonsingular_terminal_smc | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P3_SLIDING_MODE | super_twisting_smc | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P3_SLIDING_MODE | adaptive_smc | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P3_SLIDING_MODE | fuzzy_smc | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P4_MPC | linear_mpc | accepted | 有 | 有 | 有 | 有 | 有 | document_ready_static_audit |
| P4_MPC | robust_mpc | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P4_MPC | adaptive_mpc | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P4_MPC | tube_mpc | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P4_MPC | explicit_gain_scheduled_mpc | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P4_MPC | ilqr | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P4_MPC | mppi | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P5_ENHANCEMENT | l1_adaptive | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P5_ENHANCEMENT | awff | executed_blocked | 有 | 有 | 有 | 有 | 有 | document_ready_static_audit |
| P5_ENHANCEMENT | complete_adrc | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P5_ENHANCEMENT | standardized_indi | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P5_ENHANCEMENT | parameter_scheduling | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P5_ENHANCEMENT | ilc | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| G9_CORE_COMPARISON | official_pid | executed_blocked | 有 | 有 | 缺 | 有 | 有 | capture_missing_mworks_screenshots |
| G9_CORE_COMPARISON | se3_basic | not_run | 缺 | 缺 | 缺 | 缺 | 待确认 | repair_or_rerun_required |
| G9_CORE_COMPARISON | dfbc_basic | not_run | 缺 | 缺 | 缺 | 缺 | 待确认 | repair_or_rerun_required |
| G9_CORE_COMPARISON | smc_boundary_layer | not_run | 缺 | 缺 | 缺 | 缺 | 待确认 | repair_or_rerun_required |
| G9_CORE_COMPARISON | pid_indi | not_run | 缺 | 缺 | 缺 | 缺 | 有 | repair_or_rerun_required |
| G9_CORE_COMPARISON | nmpc_outer | not_run | 缺 | 缺 | 缺 | 缺 | 待确认 | repair_or_rerun_required |
| P6_SAFETY | safety_supervisor_family | accepted | 有 | 缺 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P7_FTC | fdi_ftc_family | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P8_FORMATION | leader_follower | accepted | 有 | 缺 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P8_FORMATION | virtual_structure | accepted | 有 | 缺 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P8_FORMATION | consensus | accepted | 有 | 缺 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P8_FORMATION | containment | accepted | 有 | 缺 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P8_FORMATION | formation_tracking | accepted | 有 | 缺 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P8_FORMATION | formation_reconfiguration | accepted | 有 | 缺 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P8_FORMATION | fault_tolerant_formation | accepted | 有 | 缺 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P8_FORMATION | formation_cbf | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P8_FORMATION | distributed_mpc_formation | accepted | 有 | 缺 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P9_LEARNING | trained_neural_residual | executed_blocked | 有 | 缺 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P9_LEARNING | rl_gain_scheduler | executed_blocked | 有 | 有 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P10_CLASSIC_RECONCILIATION | lqr_baseline | executed_blocked | 有 | 有 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P10_CLASSIC_RECONCILIATION | lqi_baseline | executed_blocked | 有 | 有 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P10_CLASSIC_RECONCILIATION | hinf_hover_wrench | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | mu_synthesis | not_run | 缺 | 缺 | 缺 | 有 | 待确认 | bounded_implementation_gap_review |
| P10_CLASSIC_RECONCILIATION | so3_attitude | executed_blocked | 有 | 有 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P10_CLASSIC_RECONCILIATION | backstepping_baseline | executed_blocked | 有 | 有 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P10_CLASSIC_RECONCILIATION | dfbc_high_order_attitude | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | dfbc_high_order_bodyrate | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | dfbc_smooth_robust_attitude | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | dfbc_smooth_robust_bodyrate | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | l1_awff_minimal | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | dfbc_dob_eso_disabled | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | dfbc_dob_eso | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | neural_smc | not_run | 缺 | 缺 | 缺 | 有 | 待确认 | bounded_implementation_gap_review |
| P11_CLASSIC_ADDITIONS | pole_placement_luenberger | executed_blocked | 有 | 有 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P11_CLASSIC_ADDITIONS | mrac | executed_blocked | 有 | 有 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P11_CLASSIC_ADDITIONS | ndi | executed_blocked | 有 | 有 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P11_CLASSIC_ADDITIONS | fopid | executed_blocked | 有 | 有 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |
| P11_CLASSIC_ADDITIONS | h2_state_feedback | executed_blocked | 有 | 有 | 缺 | 有 | 待确认 | capture_missing_mworks_screenshots |

## 下一批

- 优先补齐已有模型和数值结果、但缺少图形或结果查看器截图的路线；不先重跑七场景。
- `mu_synthesis`与`neural_smc`保持实现阻塞，不阻塞其余65项证据整理。
