# MSR导出失败总结

## 问题诊断

经过多次尝试，MSR文件的自动导出失败，原因如下：

### 1. MWORKS API无法打开MSR文件
- `ModelingPy.OpenResult()` 返回 `False`
- `GetLastErrors()` 无错误信息
- 尝试的所有20个MSR文件都无法打开

### 2. MSR文件结构分析（HDF5格式）
通过直接读取HDF5文件，发现：
- **Animation Data Table**: 5001行 × 229列
- **Continuous Data Table**: 5001行 × 184列  
- **Discrete Data Table**: 21532行 × 65列
- **Variable Name Table**: 2286个变量名（用`\x00`分隔）
- **Variable Index Table**: 索引结构复杂，无法直接映射到数据列

### 3. 找到的关键变量名
通过解析Variable Name Table，确认存在以下变量：
```
x, y, z:        controller.position_mea[1-3]
x_ref等:        controller.position_ref[1-3]
vx, vy, vz:     controller.velocity_mea[1-3]
roll等:         controller.roll_mea, controller.pitch_mea, controller.yaw_mea
u1-u4:          plant.physical.wrapper.motor_command[1-4]
time:           Animation Data Table的第0列
```

### 4. 无法自动映射的原因
- Animation Index Table只映射了1个变量到数据列
- Variable Index Table的结构无法直接解析出变量→列的映射关系
- 需要MWORKS内部API才能正确解析这个索引结构

---

## 解决方案

### 方案A：手动导出（最可靠）⭐

在**MWORKS Syslab Result Viewer**中：

1. 打开MSR文件（双击或File→Open）
2. 工具栏：Export → CSV
3. 选择变量（建议导出全部，或至少包含上述关键变量）
4. 保存到：`{controller}/raw/climbpath50s.csv`

**需要导出的控制器列表**（20个MSR文件已找到）：
```
adaptive_backstepping, adaptive_smc, backstepping_baseline,
dfbc_basic, dfbc_high_order_body_rate, dfbc_high_order,
dfbc_smooth_robust_body_rate, dfbc_smooth_robust,
explicit_gain_scheduled_mpc, feedback_linearization,
ilqr, integral_smc, lqg, lqi, lqr_baseline, mppi,
passivity_based_control, px4ctrl, se_3_basic
(+ 1个待确认：可能在不同路径)
```

**缺失的8个MSR文件**：
```
fuzzy_smc, h_2_state_feedback, ndi, nonsingular_terminal_smc,
official_pid, official_pid_yaw_authority_mapped,
robust_mpc, terminal_smc
```

### 方案B：重新仿真生成CSV（如果仿真配置支持）

如果原始仿真脚本支持直接输出CSV，可以重新运行仿真。

### 方案C：等待Codex恢复

之前Codex可能有处理MSR的经验，等它恢复后可以尝试。

---

## 导出后的工作流

一旦CSV文件准备好（任何一个控制器），我立即可以：

1. **验证数据**：读取CSV，检查列名和数据完整性
2. **生成详细轨迹图**（4张SVG）：
   - 位置xyz vs time
   - 速度xyz vs time  
   - 姿态roll/pitch/yaw vs time
   - 控制输入u1-u4 vs time
3. **批量生成**：有了第一个成功案例后，批量处理所有20个控制器
4. **最终交付**：112张详细轨迹图（28控制器×4图，目前有20个MSR可用=80张图）

---

## 我的建议

**立即行动**：先手动导出1个控制器（px4ctrl）验证流程

1. 在Result Viewer中打开px4ctrl的MSR文件
2. 导出CSV到 `px4ctrl/raw/climbpath50s.csv`
3. 告诉我CSV已准备好
4. 我立即生成该控制器的4张图验证效果
5. 确认无误后，批量导出剩余19个控制器

预计时间：
- 单个导出：2-3分钟
- 20个控制器：40-60分钟（可以边导出边生图）
