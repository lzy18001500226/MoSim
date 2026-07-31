# MSR导出操作清单

## 找到的20个MSR文件（按优先级排序）

### P0 - 核心控制器（必须导出）
1. **official_pid** - ❌ MSR文件未找到
2. **px4ctrl** - ✅ 找到MSR
   - 源：`Results/control_platform/phase2_full_48_climbpath/px4ctrl/native_result_g6_20260729_053256_034264/Px4CtrlFormalRunner/Result.msr`
   - 目标：`Results/control_platform/phase2_full_48_climbpath/px4ctrl/raw/climbpath50s.csv`

### P1 - 优化/预测族（5个）
3. **explicit_gain_scheduled_mpc** - ✅ 找到MSR
   - 源：`Results/.../explicit_gain_scheduled_mpc/.../Result.msr`
   - 目标：`Results/.../explicit_gain_scheduled_mpc/raw/climbpath50s.csv`

4. **ilqr** - ✅ 找到MSR
5. **mppi** - ✅ 找到MSR
6. **robust_mpc** - ❌ MSR未找到
7. **tube_mpc** - ❌ MSR未找到

### P2 - 几何/微分平坦族（8个）
8. **dfbc_basic** - ✅ 找到MSR
9. **dfbc_high_order** - ✅ 找到MSR
10. **dfbc_high_order_body_rate** - ✅ 找到MSR
11. **dfbc_smooth_robust** - ✅ 找到MSR
12. **dfbc_smooth_robust_body_rate** - ✅ 找到MSR
13. **se_3_basic** - ✅ 找到MSR

### P3 - 非线性/自适应族（5个）
14. **adaptive_backstepping** - ✅ 找到MSR
15. **backstepping_baseline** - ✅ 找到MSR
16. **feedback_linearization** - ✅ 找到MSR
17. **passivity_based_control** - ✅ 找到MSR
18. **ndi** - ❌ MSR未找到

### P4 - 滑模族（5个）
19. **adaptive_smc** - ✅ 找到MSR
20. **integral_smc** - ✅ 找到MSR
21. **fuzzy_smc** - ❌ MSR未找到
22. **nonsingular_terminal_smc** - ❌ MSR未找到
23. **terminal_smc** - ❌ MSR未找到

### P5 - 线性/鲁棒族（4个）
24. **lqr_baseline** - ✅ 找到MSR
25. **lqi** - ✅ 找到MSR
26. **lqg** - ✅ 找到MSR
27. **h_2_state_feedback** - ❌ MSR未找到
28. **official_pid_yaw_authority_mapped** - ❌ MSR未找到

---

## 统计
- ✅ 找到MSR：20个
- ❌ MSR缺失：8个

---

## 建议方案

### 方案A：手动导出20个（最可靠）
在MWORKS Result Viewer中逐个打开MSR文件，导出CSV到对应的`raw/climbpath50s.csv`。

**优点：** 最可靠，保证数据完整性
**缺点：** 耗时（20个文件 × 3分钟 ≈ 1小时）

### 方案B：等Codex恢复后让它处理
Codex可能有自动化脚本可以调用MWORKS API批量导出。

### 方案C：先导出核心控制器（5个），生成部分图表
只导出：px4ctrl, explicit_gain_scheduled_mpc, ilqr, dfbc_basic, lqr_baseline
然后先生成这5个控制器的详细轨迹图（5×4=20张），验证流程。

---

## 我的建议

**立即行动：方案C（先导出5个核心控制器）**

1. 在Result Viewer中导出这5个控制器的CSV
2. 我立即生成这5个控制器的详细轨迹图（20张SVG）
3. 验证图表生成流程没问题后，再导出剩余15个

这样可以在1小时内完成部分工作，而不是等待全部导出。

你觉得呢？
