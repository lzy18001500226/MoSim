# Phase 5 诊断结果 PPT 视觉规格说明

## 文档用途

本文档为 Phase 5 失败控制器诊断结果的 PPT 图表提供精确的数据规格和视觉设计要求，确保图表制作准确且符合答辩需求。

---

## 第18页修订：ClimbPath 50s筛查结果

### 图1：48路控制器筛查结果热力图

**数据源**：
- 总控制器数：48个（46个恢复 + 2个未统计）
- Phase 5测试：38个
- 通过：26个（68.4%）
- 失败：12个（31.6%）
- 未测试：10个（Phase 1-3恢复但未进Phase 5）

**视觉设计**：
- 类型：横向条形图或矩阵热力图
- 颜色编码：
  - 绿色 (#6EE7B7)：26个通过
  - 黄色 (#E9A568)：12个失败但已诊断
  - 灰色 (#1E2636)：10个未参与Phase 5
- 排序：按终点误差从小到大（通过区 < 5m，失败区 >= 5m）
- 标注：每个色块显示控制器名称或数量

**数据清单**：

**通过（26个，误差 < 5m）**：
1. backstepping_attitude (0.86m)
2. ftc_pca_mid_level (1.12m)
3. cascade_pid (1.30m)
4. dfbc_high_order_attitude (1.39m)
5. super_twisting_smc (1.44m)
6. lqr_baseline (1.48m)
7. linear_mpc (1.49m)
8. trained_neural_residual_v2 (1.51m)
9. incremental_nonlinear_dynamic_inversion (1.55m)
10. attitude_thrust (1.58m)
11. px4ctrl (1.67m)
12. rotor_command (1.76m)
13. wrench (1.80m)
14. body_rate_thrust (1.82m)
15. ftc_ca_low_level (1.91m)
16. linear_quadratic_tracking (2.12m)
17. ftc_indi_high_level (2.13m)
18. explicit_mpc (2.18m)
19. ftc_inversion_matrix (2.20m)
20. pid_baseline (2.44m)
21. explicit_min_max_mpc (2.45m)
22. backstepping_inner_outer (2.47m)
23. geometric_attitude (2.75m)
24. robust_tube_mpc (3.22m)
25. se3_control (3.54m)
26. geometric_se3 (4.76m)

**失败（12个，误差 >= 5m）**：
1. dfbc_smooth_robust_attitude (5.30m) - 设计参数不匹配
2. trained_neural_residual (6.93m) - 架构不完整
3. rl_gain_scheduler (7.33m) - 架构不完整
4. explicit_gain_scheduled_mpc (7.45m) - 适配器不完整
5. tube_mpc (7.68m) - 适配器不完整
6. official_pid (8.90m) - 参数传递问题
7. adaptive_smc (11.08m) - 适配器不完整
8. fixed_awff_pid (11.18m) - 模板不兼容
9. gain_scheduled_pid (11.53m) - 适配器架构缺陷
10. fopid (14.12m) - 参考轨迹配置错误
11. fuzzy_pid (14.51m) - 适配器架构缺陷
12. mrac (14.99m) - 自适应律发散

### 图2：失败原因分类饼图

**数据源**：12个失败控制器分类统计

**分类数据**：
1. **适配器架构问题**：5个（41.7%）
   - GraphicalScalarRotorPreview缺陷：2个（gain_scheduled_pid, fuzzy_pid）
   - GraphicalAccelerationRotorPreview不完整：3个（explicit_gain_scheduled_mpc, tube_mpc, adaptive_smc）

2. **控制器内部问题**：4个（33.3%）
   - 自适应律发散：1个（mrac）
   - 设计参数不匹配：1个（dfbc_smooth_robust_attitude）
   - 架构不完整：2个（trained_neural_residual, rl_gain_scheduler）

3. **配置/参数问题**：3个（25.0%）
   - 参考轨迹配置错误：1个（fopid）
   - 参数传递问题：1个（official_pid）
   - 遗留模板不兼容：1个（fixed_awff_pid）

**视觉设计**：
- 类型：饼图或环形图
- 颜色编码：
  - 橙色 (#E9A568)：适配器架构问题（5个，41.7%）
  - 红色 (#FF6B6B)：控制器内部问题（4个，33.3%）
  - 黄色 (#FFD93D)：配置/参数问题（3个，25.0%）
- 标注：每个扇区显示类别名称、数量、百分比
- 图例：列出各类别的代表控制器

---

## 可选页A：Phase 5诊断方法论流程图

### 流程图结构

**第一层：输入**
```
失败控制器（12个）
终点误差 >= 5.0m
```

**第二层：架构验证**
```
读取 *GraphicalRunner.mo 文件
├─ 检查 output_adapter 类型
│  ├─ GraphicalAttitudeThrustRotorPreview ✅
│  ├─ GraphicalScalarRotorPreview ❌
│  └─ GraphicalAccelerationRotorPreview ⚠️
├─ 检查连接方式
│  └─ connect(core.*, output_adapter.*)
└─ 检查参数配置
   └─ scenario_mode, z_ref, 增益参数
```

**第三层：实际仿真验证（选择性）**
```
运行 Sysplorer 仿真
├─ fopid: 实测 8.35m
│  └─ 发现 z_ref=5.2m（应为15.0m）
└─ mrac: 实测 1907.51m
   └─ 发现自适应律发散，电机饱和
```

**第四层：根本原因分类**
```
8大类失败原因
├─ 适配器架构缺陷（2个）
├─ 适配器架构不完整（3个）
├─ 自适应律发散（1个）
├─ 设计参数不匹配（1个）
├─ 架构不完整（2个）
├─ 参考轨迹配置问题（1个）
├─ 参数传递/配置问题（1个）
└─ 遗留模板不兼容（1个）
```

**第五层：可修复性评估**
```
3个等级
├─ 短期无法修复（6个）：适配器/模板架构问题
├─ 需要较大改动（4个）：重新设计/调参
└─ 可能通过调参修复（2个）：配置问题
```

**视觉设计**：
- 类型：自上而下的流程图
- 颜色编码：
  - 蓝色框：正常流程节点
  - 绿色框：验证通过
  - 橙色框：问题识别
  - 红色框：严重缺陷
- 箭头：实线表示必经流程，虚线表示选择性步骤

---

## 可选页B：典型失败案例三栏对比

### 案例1：fopid（左栏）

**基本信息**：
- 控制器类型：Fractional-Order PID
- 排名：10/12（误差第10差）
- 报告误差：14.12m
- 实测误差：8.35m

**架构验证**：
```
✅ 正确架构
MoSimQuadrotorModel.Control.ClassicRobust.Fopid.FopidCore
↓
GraphicalAttitudeThrustRotorPreview
(roll_ref, pitch_ref, yaw_ref, collective_thrust)
```

**诊断发现**：
- 终点位置：[0.013, -0.092, 13.551] m
- 参考位置：[0.0, 0.0, 5.2] m ❌（应为 [0, 0, 15] m）
- 水平误差：0.093m（优秀）
- 垂直误差：8.449m（由于z_ref错误）

**根本原因**：
参考轨迹配置错误，z_ref=5.2m 而非 15.0m

**修复预期**：
修正轨迹配置后，预期误差 ~1.45m（通过阈值）

**可视化建议**：
- 顶部：绿色勾号标记架构正确
- 中部：对比图显示 z_ref=5.2m vs z=15m 目标
- 底部：绿色标记"可修复"

### 案例2：mrac（中栏）

**基本信息**：
- 控制器类型：Model Reference Adaptive Control
- 排名：12/12（误差最大）
- 报告误差：14.99m
- 实测误差：1907.51m（严重发散）

**架构验证**：
```
✅ 正确架构
MoSimQuadrotorModel.Control.Adaptive.Mrac.MracCore
↓
GraphicalAttitudeThrustRotorPreview
(roll_ref, pitch_ref, yaw_ref, collective_thrust)
```

**诊断发现**：
- 终点位置：[-379.867, 1812.492, -442.365] m
- 参考位置：[0.0, 0.0, 15.0] m
- 所有电机饱和：110 rad/s（ESC限制）
- 误差发散：从 t=10s 开始快速增长

**根本原因**：
自适应律参数设置不当，导致增益发散

**修复难度**：
需要重新调整自适应律参数或重新设计

**可视化建议**：
- 顶部：绿色勾号标记架构正确
- 中部：红色警告图显示误差1907m，电机饱和110 rad/s
- 底部：橙色标记"需重新设计"

### 案例3：gain_scheduled_pid（右栏）

**基本信息**：
- 控制器类型：Gain-Scheduled PID
- 排名：9/12（误差第9差）
- 报告误差：11.53m

**架构验证**：
```
❌ 错误架构
MoSimQuadrotorModel.Control.ClassicRobust.GainScheduledPid.GainScheduledPidCore
↓
GraphicalScalarRotorPreview
(normalized_thrust → 4个相同转速)
```

**诊断发现**：
- 适配器设计缺陷：
  ```modelica
  rotor_1_speed = rotor_2_speed = rotor_3_speed = rotor_4_speed
  = normalized_thrust * (max_speed - min_speed) + min_speed
  ```
- 物理限制：4个电机恒定相同转速→无法产生姿态力矩
- 必然结果：飞行器翻滚失控

**根本原因**：
适配器架构根本性缺陷，无法控制姿态

**修复可能性**：
无法修复，需要更换为 GraphicalAttitudeThrustRotorPreview

**可视化建议**：
- 顶部：红色叉号标记架构错误
- 中部：示意图显示4个电机转速相同→无姿态控制力矩
- 底部：红色标记"根本性缺陷"

---

## 关键数字卡片设计

### 卡片1：实际控制器核心成功率

```
┌─────────────────────────────┐
│                             │
│          78.8%              │
│                             │
│   (26通过 / 33有效)          │
│                             │
│ 排除5个适配器架构问题后的    │
│ 控制器核心实际成功率         │
│                             │
└─────────────────────────────┘
```

**数据说明**：
- 分子：26个通过的控制器
- 分母：33个有效控制器（38 - 5个适配器问题）
- 计算：26 / 33 = 0.788 = 78.8%

### 卡片2：失败控制器诊断完成度

```
┌─────────────────────────────┐
│                             │
│         12 / 12             │
│                             │
│   失败控制器诊断完成         │
│                             │
│ 9份详细报告 + 1份结构化数据  │
│ 2个实际仿真验证              │
│                             │
└─────────────────────────────┘
```

### 卡片3：适配器问题占比

```
┌─────────────────────────────┐
│                             │
│         41.7%               │
│                             │
│   (5 / 12 失败控制器)        │
│                             │
│ 失败原因归属于适配器架构问题 │
│ 非控制器核心算法问题         │
│                             │
└─────────────────────────────┘
```

---

## 详细数据表格规格

### 表1：12个失败控制器详细信息表

| 排名 | 控制器名称 | 误差(m) | 失败原因类别 | 根本原因 | 可修复性 |
|------|-----------|--------|------------|---------|---------|
| 1 | dfbc_smooth_robust_attitude | 5.30 | 设计参数不匹配 | 设计假设±8 m/s²，平台限制±3.0 m/s² | 需重新设计 |
| 2 | trained_neural_residual | 6.93 | 架构不完整 | 神经网络权重未加载或参数不匹配 | 需补全实现 |
| 3 | rl_gain_scheduler | 7.33 | 架构不完整 | 强化学习策略未正确配置 | 需补全实现 |
| 4 | explicit_gain_scheduled_mpc | 7.45 | 适配器架构不完整 | collective_thrust=0, k=1无单位转换 | 需重新设计适配器 |
| 5 | tube_mpc | 7.68 | 适配器架构不完整 | collective_thrust=0, k=1无单位转换 | 需重新设计适配器 |
| 6 | official_pid | 8.90 | 参数传递/配置问题 | scenario_mode或参数传递问题 | 可能可修复 |
| 7 | adaptive_smc | 11.08 | 适配器架构不完整 | collective_thrust=0, k=1无单位转换 | 需重新设计适配器 |
| 8 | fixed_awff_pid | 11.18 | 遗留模板不兼容 | 使用QuadChassis+ClimbPath遗留架构 | 需重新适配 |
| 9 | gain_scheduled_pid | 11.53 | 适配器架构缺陷 | 4个电机转速恒定相同，无法控制姿态 | 根本性缺陷 |
| 10 | fopid | 14.12 | 参考轨迹配置问题 | z_ref=5.2m(应为15.0m) | 可能可修复 |
| 11 | fuzzy_pid | 14.51 | 适配器架构缺陷 | 4个电机转速恒定相同，无法控制姿态 | 根本性缺陷 |
| 12 | mrac | 14.99 | 自适应律发散 | 自适应增益设置不当，电机饱和 | 需调参或重新设计 |

### 表2：失败原因分类统计表

| 失败原因类别 | 控制器数 | 占比 | 代表案例 |
|-------------|---------|------|---------|
| 适配器架构不完整 | 3 | 25.0% | explicit_gain_scheduled_mpc, tube_mpc, adaptive_smc |
| 适配器架构缺陷 | 2 | 16.7% | gain_scheduled_pid, fuzzy_pid |
| 架构不完整 | 2 | 16.7% | trained_neural_residual, rl_gain_scheduler |
| 设计参数不匹配 | 1 | 8.3% | dfbc_smooth_robust_attitude |
| 参数传递/配置问题 | 1 | 8.3% | official_pid |
| 遗留模板不兼容 | 1 | 8.3% | fixed_awff_pid |
| 参考轨迹配置问题 | 1 | 8.3% | fopid |
| 自适应律发散 | 1 | 8.3% | mrac |

### 表3：可修复性评估表

| 可修复性分组 | 控制器数 | 占比 | 控制器列表 |
|-------------|---------|------|-----------|
| 短期无法修复（适配器/模板架构问题） | 6 | 50.0% | gain_scheduled_pid, fuzzy_pid, explicit_gain_scheduled_mpc, tube_mpc, adaptive_smc, fixed_awff_pid |
| 需要较大改动（重新设计/调参） | 4 | 33.3% | dfbc_smooth_robust_attitude, mrac, trained_neural_residual, rl_gain_scheduler |
| 可能通过调参修复（配置问题） | 2 | 16.7% | official_pid, fopid |

---

## PPT配色方案

### 主色调
- 背景：深色系（#0A0D12, #0F131C）
- 文字：浅色系（#E5E7EB, #F9FAFB）
- 强调：品牌色（#38BDF8 蓝色，#6EE7B7 绿色）

### 状态指示色
- 通过：#6EE7B7（绿色）
- 失败但已诊断：#E9A568（琥珀色）
- 未测试：#1E2636（深灰）
- 可修复：#FFD93D（黄色）
- 根本性缺陷：#FF6B6B（红色）

### 图表配色
- 适配器问题：#E9A568（橙色）
- 控制器问题：#FF6B6B（红色）
- 配置问题：#FFD93D（黄色）
- 正确架构：#6EE7B7（绿色）
- 错误架构：#FF6B6B（红色）

---

**文档完成 (2026-08-19)**
