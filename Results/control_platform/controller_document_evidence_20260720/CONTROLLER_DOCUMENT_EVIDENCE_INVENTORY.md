# 控制器文档证据静态盘点（67项）

状态：静态文件盘点，不代表MWORKS现场验收。

- 权威矩阵：`Results/control_platform/classic_controller_closeout_20260717/CLASSIC_CONTROLLER_FINAL_MATRIX.json`
- 路线数：`67`
- 状态计数：`{"accepted": 27, "executed_blocked": 33, "not_run": 7}`
- 已有模型源码：`65`
- 已有图形模型截图：`65`
- 已有结果查看器截图：`65`
- 已有数值结果或指标：`67`
- 仓库内可见Result.msr：`8`
- 实现阻塞：`2`
- 已形成终止阻塞证据：`2`

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
| G9_CORE_COMPARISON | official_pid | executed_blocked | 有 | 有 | 有 | 有 | 有 | document_ready_static_audit |
| G9_CORE_COMPARISON | se3_basic | not_run | 有 | 有 | 有 | 有 | 有 | document_ready_static_audit |
| G9_CORE_COMPARISON | dfbc_basic | not_run | 有 | 有 | 有 | 有 | 有 | document_ready_static_audit |
| G9_CORE_COMPARISON | smc_boundary_layer | not_run | 有 | 有 | 有 | 有 | 有 | document_ready_static_audit |
| G9_CORE_COMPARISON | pid_indi | not_run | 有 | 有 | 有 | 有 | 有 | document_ready_static_audit |
| G9_CORE_COMPARISON | nmpc_outer | not_run | 有 | 有 | 有 | 有 | 有 | document_ready_static_audit |
| P6_SAFETY | safety_supervisor_family | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P7_FTC | fdi_ftc_family | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P8_FORMATION | leader_follower | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P8_FORMATION | virtual_structure | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P8_FORMATION | consensus | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P8_FORMATION | containment | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P8_FORMATION | formation_tracking | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P8_FORMATION | formation_reconfiguration | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P8_FORMATION | fault_tolerant_formation | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P8_FORMATION | formation_cbf | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P8_FORMATION | distributed_mpc_formation | accepted | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P9_LEARNING | trained_neural_residual | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P9_LEARNING | rl_gain_scheduler | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | lqr_baseline | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | lqi_baseline | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | hinf_hover_wrench | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | mu_synthesis | not_run | 缺 | 缺 | 缺 | 有 | 待确认 | terminal_implementation_blocker_documented |
| P10_CLASSIC_RECONCILIATION | so3_attitude | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | backstepping_baseline | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | dfbc_high_order_attitude | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | dfbc_high_order_bodyrate | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | dfbc_smooth_robust_attitude | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | dfbc_smooth_robust_bodyrate | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | l1_awff_minimal | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | dfbc_dob_eso_disabled | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | dfbc_dob_eso | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P10_CLASSIC_RECONCILIATION | neural_smc | not_run | 缺 | 缺 | 缺 | 有 | 待确认 | terminal_implementation_blocker_documented |
| P11_CLASSIC_ADDITIONS | pole_placement_luenberger | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P11_CLASSIC_ADDITIONS | mrac | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P11_CLASSIC_ADDITIONS | ndi | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P11_CLASSIC_ADDITIONS | fopid | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |
| P11_CLASSIC_ADDITIONS | h2_state_feedback | executed_blocked | 有 | 有 | 有 | 有 | 待确认 | confirm_native_result_msr_in_live_session |

## 下一批

- 65条已实现路线的模型、图形截图、结果截图和数值证据已齐备；不先重跑七场景。
- `mu_synthesis`与`neural_smc`已有终止阻塞证据；在重开门槛满足前不生成伪模型或替代结果。
