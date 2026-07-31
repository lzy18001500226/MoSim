# -*- coding: utf-8 -*-
"""Hand-authored captions for the 60 aggregate figures in chapters 7-9.

Keyed by image path suffix. Each caption states what the figure shows and,
where a measured value carries the point, cites it.
"""

CAP = {
 # ---- 7.3 performance distribution (5) ----
 '第10章/controller_dist_rmse_box.png':
   '图 xx　冻结 G3 快照的 28 条达标控制器位置 RMSE 的分族箱线分布',
 '第10章/controller_dist_terminal_box.png':
   '图 xx　冻结 G3 快照的 28 条达标控制器终端位置误差的分族箱线分布',
 '第10章/controller_dist_rmse_hist.png':
   '图 xx　冻结 G3 快照的 28 条达标控制器位置 RMSE 的总体直方分布',
 '第10章/controller_dist_terminal_hist.png':
   '图 xx　冻结 G3 快照的 28 条达标控制器终端位置误差的总体直方分布',
 '第10章/controller_ranking_rmse.png':
   '图 xx　冻结 G3 快照的 28 条达标控制器按位置 RMSE 的排名',

 # ---- 7.5 family comparison, 6 families x 4 (24) ----
 'pid_family_comparison/figures/climbpath_rmse_bar.png':
   '图 xx　PID 族 2 条达标条目的位置 RMSE（0.173 至 0.339 m）',
 'pid_family_comparison/figures/climbpath_trajectory_overlay.png':
   '图 xx　PID 族 ClimbPath 轨迹叠加',
 'pid_family_comparison/figures/control_energy_bar.png':
   '图 xx　PID 族控制能量（8.39×10⁵ 至 8.50×10⁵）',
 'pid_family_comparison/figures/terminal_error_bar.png':
   '图 xx　PID 族终端位置误差（0.007 至 0.054 m）',

 'linear_family_comparison/figures/climbpath_rmse_bar.png':
   '图 xx　线性与鲁棒状态反馈族 4 条条目的位置 RMSE（0.090 至 0.243 m）',
 'linear_family_comparison/figures/climbpath_trajectory_overlay.png':
   '图 xx　线性与鲁棒状态反馈族 ClimbPath 轨迹叠加',
 'linear_family_comparison/figures/control_energy_bar.png':
   '图 xx　线性与鲁棒状态反馈族控制能量（8.32×10⁵ 至 8.40×10⁵）',
 'linear_family_comparison/figures/terminal_error_bar.png':
   '图 xx　线性与鲁棒状态反馈族终端位置误差（0.001 至 0.022 m）',

 'nonlinear_family_comparison/figures/climbpath_rmse_bar.png':
   '图 xx　非线性与自适应族 5 条条目的位置 RMSE（0.104 至 2.289 m）',
 'nonlinear_family_comparison/figures/climbpath_trajectory_overlay.png':
   '图 xx　非线性与自适应族 ClimbPath 轨迹叠加',
 'nonlinear_family_comparison/figures/control_energy_bar.png':
   '图 xx　非线性与自适应族控制能量（8.36×10⁵ 至 8.37×10⁵）',
 'nonlinear_family_comparison/figures/terminal_error_bar.png':
   '图 xx　非线性与自适应族终端位置误差（0.001 至 2.421 m）',

 'smc_family_comparison/figures/climbpath_rmse_bar.png':
   '图 xx　滑模族 5 条条目的位置 RMSE（1.453 至 2.705 m，全族无一进入达标区间）',
 'smc_family_comparison/figures/climbpath_trajectory_overlay.png':
   '图 xx　滑模族 ClimbPath 轨迹叠加',
 'smc_family_comparison/figures/control_energy_bar.png':
   '图 xx　滑模族控制能量（9.46×10⁵ 至 1.195×10⁶，为唯一整体高于其余各族的族）',
 'smc_family_comparison/figures/terminal_error_bar.png':
   '图 xx　滑模族终端位置误差（1.458 至 2.843 m）',

 'mpc_family_comparison/figures/climbpath_rmse_bar.png':
   '图 xx　最优与预测控制族 5 条条目的位置 RMSE（0.203 至 0.227 m，族内极差 0.024 m）',
 'mpc_family_comparison/figures/climbpath_trajectory_overlay.png':
   '图 xx　最优与预测控制族 ClimbPath 轨迹叠加',
 'mpc_family_comparison/figures/control_energy_bar.png':
   '图 xx　最优与预测控制族控制能量（8.367×10⁵ 至 8.380×10⁵）',
 'mpc_family_comparison/figures/terminal_error_bar.png':
   '图 xx　最优与预测控制族终端位置误差（0.004 至 0.006 m）',

 'geometric_family_comparison/figures/climbpath_rmse_bar.png':
   '图 xx　几何与微分平坦族 6 条条目的位置 RMSE（0.276 至 1.637 m）',
 'geometric_family_comparison/figures/climbpath_trajectory_overlay.png':
   '图 xx　几何与微分平坦族 ClimbPath 轨迹叠加',
 'geometric_family_comparison/figures/control_energy_bar.png':
   '图 xx　几何与微分平坦族控制能量（8.05×10⁵ 至 8.38×10⁵，族内最低值出现在 `dfbc_high_order`）',
 'geometric_family_comparison/figures/terminal_error_bar.png':
   '图 xx　几何与微分平坦族终端位置误差（0.002 至 1.676 m）',

 # ---- 7.5 radar (9) ----
 '第10章/controller_radar_chart.png':
   '图 xx　八族代表控制器的四维雷达总图',
 'controller_radar/radar_01_pid.png':
   '图 xx　PID 族四维雷达',
 'controller_radar/radar_02_linear.png':
   '图 xx　线性与鲁棒状态反馈族四维雷达',
 'controller_radar/radar_03_nonlinear.png':
   '图 xx　非线性与自适应族四维雷达',
 'controller_radar/radar_04_sliding.png':
   '图 xx　滑模族四维雷达',
 'controller_radar/radar_05_optimal.png':
   '图 xx　最优与预测控制族四维雷达',
 'controller_radar/radar_06_geometric.png':
   '图 xx　几何与微分平坦族四维雷达',
 'controller_radar/radar_07_learning.png':
   '图 xx　学习增强族四维雷达',
 'controller_radar/radar_08_baseline.png':
   '图 xx　工程基线族四维雷达',

 # ---- ch8 seven-scenario (6) ----
 'hover_position_error_comparison.png':
   '图 xx　悬停场景各控制器位置误差时程对比',
 'step_response_position_error_comparison.png':
   '图 xx　阶跃响应场景各控制器位置误差时程对比',
 'figure8_position_error_comparison.png':
   '图 xx　八字轨迹场景各控制器位置误差时程对比',
 'spiral_position_error_comparison.png':
   '图 xx　螺旋上升场景各控制器位置误差时程对比',
 'wind_disturbance_position_error_comparison.png':
   '图 xx　风扰场景各控制器位置误差时程对比',
 'parameter_mismatch_position_error_comparison.png':
   '图 xx　参数失配场景各控制器位置误差时程对比',

 # ---- ch8 sensitivity (3) ----
 '灵敏度分析/wind_disturbance_sensitivity.png':
   '图 xx　位置误差对风扰强度的灵敏度曲线',
 '灵敏度分析/parameter_mismatch_sensitivity.png':
   '图 xx　位置误差对质量与惯量失配幅度的灵敏度曲线',
 '灵敏度分析/motor_efficiency_sensitivity.png':
   '图 xx　位置误差对电机效率衰减的灵敏度曲线',

 # ---- ch8 formation (3) ----
 '三机编队/formation_trajectory_xy.png':
   '图 xx　三机编队水平面轨迹',
 '三机编队/formation_error.png':
   '图 xx　三机编队队形保持误差时程',
 '三机编队/inter_uav_distance.png':
   '图 xx　三机编队机间距离时程',

 # ---- ch8 ECBF (3) ----
 'ECBF安全/ecbf_pair_distance.png':
   '图 xx　ECBF 介入下的机间距离与安全半径',
 'ECBF安全/ecbf_applied_offset.png':
   '图 xx　ECBF 施加的参考位置修正量时程',
 'ECBF安全/tracking_error_divergence.png':
   '图 xx　ECBF 介入引起的跟踪误差偏离',

 # ---- ch9 single OpenBlocks (3) ----
 'single_uav_trajectory_xy.png':
   '图 xx　单机在 OpenBlocks 障碍地图中的水平面轨迹',
 'single_uav_altitude_tracking.png':
   '图 xx　单机 OpenBlocks 高度通道跟踪',
 'single_uav_position_error.png':
   '图 xx　单机 OpenBlocks 位置误差时程',

 # ---- ch9 three-UAV OpenBlocks (4) ----
 'three_uav_trajectory_xy.png':
   '图 xx　三机在 OpenBlocks 障碍地图中的水平面轨迹',
 'three_uav_pair_distance.png':
   '图 xx　三机 OpenBlocks 机间距离时程',
 'three_uav_tracking_error.png':
   '图 xx　三机 OpenBlocks 跟踪误差时程',
 'three_uav_clearance_bound.png':
   '图 xx　三机 OpenBlocks 最小避障间隙及其下界',
}
