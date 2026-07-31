# Syslab分析汇总报告

生成时间: 2026-07-30 18:00:32 UTC

## 控制器统计

- G3有效记录总数：48 个
- accepted（有效 pass）控制器：28 个
- 非 accepted 有效记录：20 个
- 数据边界：本报告仅汇总 G3 的 ClimbPath50s 最小闭环证据，不构成七场景、部署或运行时性能结论。

## 位置RMSE汇总表

| 控制器 | 族 | RMSE (m) | 状态 |
|---|---|---:|---|
| official_pid | PID族 | 0.17297014794091128 | ✅ accepted |
| official_pid_yaw_authority_mapped | PID族 | 0.3392670612206072 | ✅ accepted |
| h_2_state_feedback | 线性/鲁棒族 | 0.08974783356659308 | ✅ accepted |
| lqg | 线性/鲁棒族 | 0.2427607354330561 | ✅ accepted |
| lqi | 线性/鲁棒族 | 0.21221954634435075 | ✅ accepted |
| lqr_baseline | 线性/鲁棒族 | 0.20429428437790634 | ✅ accepted |
| adaptive_backstepping | 非线性/自适应族 | 2.289471013723613 | ✅ accepted |
| backstepping_baseline | 非线性/自适应族 | 1.8004411559773 | ✅ accepted |
| feedback_linearization | 非线性/自适应族 | 2.162091102107092 | ✅ accepted |
| ndi | 非线性/自适应族 | 0.10351048768735834 | ✅ accepted |
| passivity_based_control | 非线性/自适应族 | 2.162091102107092 | ✅ accepted |
| adaptive_smc | 滑模族 | 2.0461191600375335 | ✅ accepted |
| fuzzy_smc | 滑模族 | 2.7051715450671203 | ✅ accepted |
| integral_smc | 滑模族 | 2.0516091179139857 | ✅ accepted |
| nonsingular_terminal_smc | 滑模族 | 1.4528915119346768 | ✅ accepted |
| terminal_smc | 滑模族 | 2.554592212814691 | ✅ accepted |
| explicit_gain_scheduled_mpc | 优化/预测族 | 0.2042904972194766 | ✅ accepted |
| ilqr | 优化/预测族 | 0.2185471293759734 | ✅ accepted |
| mppi | 优化/预测族 | 0.20497592464335546 | ✅ accepted |
| robust_mpc | 优化/预测族 | 0.20281091203054682 | ✅ accepted |
| tube_mpc | 优化/预测族 | 0.22660286891945042 | ✅ accepted |
| dfbc_basic | 几何/微分平坦族 | 0.2760519080261363 | ✅ accepted |
| dfbc_high_order | 几何/微分平坦族 | 0.3576972701279664 | ✅ accepted |
| dfbc_high_order_body_rate | 几何/微分平坦族 | 0.35747079266089554 | ✅ accepted |
| dfbc_smooth_robust | 几何/微分平坦族 | 1.6336244568153713 | ✅ accepted |
| dfbc_smooth_robust_body_rate | 几何/微分平坦族 | 1.6370127034475108 | ✅ accepted |
| se_3_basic | 几何/微分平坦族 | 0.2765318225908831 | ✅ accepted |
| px4ctrl | 工程基线 | 0.2766961601143172 | ✅ accepted |

## 生成的图表清单

- `adaptive_backstepping/trajectory_xy.svg`
- `adaptive_smc/trajectory_xy.svg`
- `backstepping_baseline/trajectory_xy.svg`
- `controller_radar_chart.svg`
- `controller_status_matrix.svg`
- `dfbc_basic/trajectory_xy.svg`
- `dfbc_high_order/trajectory_xy.svg`
- `dfbc_high_order_body_rate/trajectory_xy.svg`
- `dfbc_smooth_robust/trajectory_xy.svg`
- `dfbc_smooth_robust_body_rate/trajectory_xy.svg`
- `explicit_gain_scheduled_mpc/trajectory_xy.svg`
- `feedback_linearization/trajectory_xy.svg`
- `fuzzy_smc/trajectory_xy.svg`
- `geometric_family_comparison/figures/climbpath_rmse_bar.svg`
- `geometric_family_comparison/figures/climbpath_trajectory_overlay.svg`
- `geometric_family_comparison/figures/control_energy_bar.svg`
- `geometric_family_comparison/figures/terminal_error_bar.svg`
- `h_2_state_feedback/trajectory_xy.svg`
- `ilqr/trajectory_xy.svg`
- `integral_smc/trajectory_xy.svg`
- `linear_family_comparison/figures/climbpath_rmse_bar.svg`
- `linear_family_comparison/figures/climbpath_trajectory_overlay.svg`
- `linear_family_comparison/figures/control_energy_bar.svg`
- `linear_family_comparison/figures/terminal_error_bar.svg`
- `lqg/trajectory_xy.svg`
- `lqi/trajectory_xy.svg`
- `lqr_baseline/trajectory_xy.svg`
- `mpc_family_comparison/figures/climbpath_rmse_bar.svg`
- `mpc_family_comparison/figures/climbpath_trajectory_overlay.svg`
- `mpc_family_comparison/figures/control_energy_bar.svg`
- `mpc_family_comparison/figures/terminal_error_bar.svg`
- `mppi/trajectory_xy.svg`
- `ndi/trajectory_xy.svg`
- `nonlinear_family_comparison/figures/climbpath_rmse_bar.svg`
- `nonlinear_family_comparison/figures/climbpath_trajectory_overlay.svg`
- `nonlinear_family_comparison/figures/control_energy_bar.svg`
- `nonlinear_family_comparison/figures/terminal_error_bar.svg`
- `nonsingular_terminal_smc/trajectory_xy.svg`
- `official_pid/altitude_z.svg`
- `official_pid/control_input.svg`
- `official_pid/position_error.svg`
- `official_pid/trajectory_xy.svg`
- `official_pid_yaw_authority_mapped/trajectory_xy.svg`
- `passivity_based_control/trajectory_xy.svg`
- `pid_family_comparison/figures/climbpath_rmse_bar.svg`
- `pid_family_comparison/figures/climbpath_trajectory_overlay.svg`
- `pid_family_comparison/figures/control_energy_bar.svg`
- `pid_family_comparison/figures/terminal_error_bar.svg`
- `px4ctrl/altitude_z.svg`
- `px4ctrl/control_input.svg`
- `px4ctrl/position_error.svg`
- `px4ctrl/trajectory_xy.svg`
- `rmse_heatmap.svg`
- `robust_mpc/trajectory_xy.svg`
- `se_3_basic/trajectory_xy.svg`
- `smc_family_comparison/figures/climbpath_rmse_bar.svg`
- `smc_family_comparison/figures/climbpath_trajectory_overlay.svg`
- `smc_family_comparison/figures/control_energy_bar.svg`
- `smc_family_comparison/figures/terminal_error_bar.svg`
- `terminal_smc/trajectory_xy.svg`
- `tube_mpc/trajectory_xy.svg`
