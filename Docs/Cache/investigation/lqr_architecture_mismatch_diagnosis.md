# LQR控制器架构缺陷诊断报告

**日期**: 2026-08-22
**状态**: 根本原因已确认，需要架构重构

---

## 问题现象

LqrBaselineGraphicalRunner在adapter架构修复后，跟踪误差从10,065m增加到17,554m（恶化74%），尽管信号传播已验证正常（core.enable=1.0，core.position_x接收到真实反馈）。

---

## 根本原因

**LqrBaselineCore是纯外环位置控制器，缺少内环姿态控制器**

### 证据1：LqrBaselineCore的输入输出

**输入端口（17个）**：
- position_x/y/z: 位置测量
- velocity_x/y/z: 速度测量
- reference_position_x/y/z: 位置参考
- reference_velocity_x/y/z: 速度参考
- reference_acceleration_x/y/z: 加速度前馈
- dt, enable: 控制参数

**输出端口（13个）**：
- position_error_x/y/z_out
- velocity_error_x/y/z_out
- desired_acceleration_x/y/z_out
- **desired_roll_rad_out** ← "期望"姿态
- **desired_pitch_rad_out** ← "期望"姿态
- normalized_thrust_out
- collective_thrust_n_out

**关键观察**：
1. **无姿态反馈输入**（没有roll_mea, pitch_mea, yaw_mea）
2. 输出变量名为`desired_roll/pitch_rad_out`（"期望"表明是设定值，非控制量）
3. 控制逻辑：位置误差 → PD反馈 → 期望加速度 → 转换为期望姿态

### 证据2：OfficialPid的级联架构对比

OfficialPidGraphicalCore **在单个Sysblock Core内实现完整级联控制**：

**输入端口（9个）**：
- x_ref, y_ref, z_ref: 位置参考
- x_mea, y_mea, z_mea: 位置测量
- **roll_mea, pitch_mea, yaw_mea**: **姿态测量** ← 关键差异

**输出端口（4个）**：
- y, y1, y2, y3: 四路幅值指令（直接可用于BaselineRotorMapper）

**内部控制链**：
```
外环：x_error = x_ref - x_mea
      x_pd = x_p + x_d  (PD控制)
      pitch_ref = saturate(x_pd * 0.1, ±15°)
      
      y_error = y_ref - y_mea
      y_pd = y_p + y_d
      roll_ref = saturate(y_pd * 0.1, ±15°)

内环：pitch_error = pitch_ref - pitch_mea
      roll_error = roll_ref - (-roll_mea)
      yaw_error = yaw_ref - yaw_mea
      [姿态PD控制] → y, y1, y2, y3 (幅值指令)
```

**关键差异总结**：

| 特性 | OfficialPid | LqrBaseline |
|------|-------------|-------------|
| 姿态反馈输入 | ✅ roll/pitch/yaw_mea | ❌ 无 |
| 控制结构 | 完整级联（外环+内环） | 仅外环 |
| 输出类型 | 幅值指令（y, y1, y2, y3） | 期望姿态+推力 |
| Sysblock实现 | 单Core全状态反馈 | 外环Core（需配对内环） |

---

## 当前架构问题

**现有控制链**：
```
plant → LqrSignalAdapter → LqrBaselineCore → GraphicalAttitudeThrustRotorPreview → plant
         (17信号传递)      (输出期望姿态)      (错误地当作控制输入使用)
```

**错误点**：GraphicalAttitudeThrustRotorPreview接收`desired_roll_rad_out`后，将其作为**实际控制输入**直接映射到转子指令，没有进行**姿态误差闭环控制**。

**为什么修复后误差更大**：
- 修复前：core输入全0 → 输出0 → 飞机自由下坠（10,065m误差）
- 修复后：core输入正确 → 输出正确的期望姿态 → 但**无姿态跟踪控制** → 开环响应更差（17,554m误差）

---

## 正确架构要求

### 方案A：添加独立内环姿态控制器

```
外环: plant → LqrSignalAdapter → LqrBaselineCore → desired_roll/pitch/thrust
                                  (17输入)         (期望姿态输出)
                                                        ↓
内环:          plant.attitude ──────────────→ [新增：姿态控制器] → rotor_command
                                (姿态误差闭环)      ↓
                                           BaselineRotorMapper
```

**优点**：
- 保持LqrBaselineCore不变（已有Sysblock实现）
- 模块化清晰：外环专注位置，内环专注姿态
- 可复用现有姿态控制器（如从OfficialPid提取内环部分）

**缺点**：
- 需要创建新的内环控制器Sysblock组件
- 两级控制器增加调试复杂度

### 方案B：重构LqrBaseline为全状态反馈（类OfficialPid）

将LqrBaselineCore扩展为接收姿态反馈，内部实现完整级联控制。

**优点**：
- 单Core完整实现，架构简洁
- 与OfficialPid一致的接口模式

**缺点**：
- 需要大幅修改已有Sysblock实现
- 违背LQR外环设计的原始意图（可能原设计就是分离式）

---

## 推荐方案

**采用方案A**：添加独立内环姿态控制器

**理由**：
1. LqrBaselineCore的设计意图就是纯外环（从命名"desired_roll/pitch"可见）
2. 归档库中可能有其他控制器也是相同模式（外环Core + 缺失内环）
3. 创建可复用的姿态控制器模块，可同时修复其他类似问题

**具体实施步骤**：
1. 从OfficialPidGraphicalCore提取姿态控制逻辑（pitch/roll/yaw的PD环）
2. 创建`AttitudeTrackingCore.mo`（Sysblock），输入：desired_roll/pitch/yaw + roll/pitch/yaw_mea + thrust，输出：4路幅值指令
3. 修改LqrBaselineGraphicalRunner架构：
   ```
   LqrBaselineCore → AttitudeTrackingCore → BaselineRotorMapper
                      ↑
                 plant.attitude (新增连接)
   ```
4. 测试验证跟踪误差是否<5m

---

## 影响范围评估

需要检查所有46个失败控制器，识别哪些属于"纯外环Core"架构：
- 输出变量名包含`desired_`前缀
- 无姿态反馈输入端口
- 输出不是直接的rotor_command或amplitude

**候选控制器家族**（推测）：
- LqiBaseline（可能与LqrBaseline类似）
- FeedbackLinearization（可能输出期望姿态）
- BacksteppingBaseline（可能分层设计）

---

## 下一步行动

1. 创建AttitudeTrackingCore Sysblock组件
2. 修改LqrBaselineGraphicalRunner连接
3. 运行test_lqr_adapter_fix.py验证
4. 如果成功，批量应用到其他外环控制器
