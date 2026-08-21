# 姿态控制器提取计划

**目标**: 从OfficialPidGraphicalCore提取内环姿态控制逻辑，创建独立的AttitudeTrackingCore Sysblock组件

---

## OfficialPid内环姿态控制链路追踪

### 输入端口（内环相关）
- `roll_mea`, `pitch_mea`, `yaw_mea`: 姿态测量（Inport）
- `roll_ref_limit`, `pitch_ref_limit`: 由外环生成的期望姿态（内部信号）
- `z_pid`: 高度PID输出（推力基准）

### 控制逻辑

#### 1. Pitch通道（line 129-156）
```
pitch_error = pitch_ref_limit - pitch_mea  (Sum, line 129)
pitch_p = pitch_error * 14.142  (Gain, line 131)
pitch_d = filtered_derivative(pitch_error) * 1.414  (Gain, line 149)
pitch_pd = pitch_p + pitch_d  (Sum, line 151)
pitch_output = saturate(pitch_pd, ±7.0)  (Saturation, line 153)
pitch_mix = pitch_output * 0.707  (Gain, line 155)
```

**滤波微分器**（line 133-148）：
- 差分：`Difference` (dt=0.01s隐含)
- 斜率放大：`* 100.0`
- 一阶滤波：`state = state_decay * prev_state + filtered_increment * current`
  - `filtered_increment = slope * 0.631839272714496`
  - `state_decay = 0.368160727285504`
  - `UnitDelay` 存储上一状态

#### 2. Roll通道（line 157-186）
```
roll_mea_corrected = roll_mea * (-1)  (符号翻转, line 157)
roll_error = roll_ref_limit - roll_mea_corrected  (Sum, line 159)
roll_p = roll_error * 14.142  (Gain, line 161)
roll_d = filtered_derivative(roll_error) * 1.414  (Gain, line 179)
roll_pd = roll_p + roll_d  (Sum, line 181)
roll_output = saturate(roll_pd, ±7.0)  (Saturation, line 183)
roll_mix = roll_output * 0.707  (Gain, line 185)
```

**微分器参数与Pitch相同**（line 163-180）

#### 3. Yaw通道（line 187-？需要补充读取）
```
yaw_error = yaw_ref - yaw_mea  (推测)
yaw控制 → yaw_mix
```

#### 4. 混合矩阵输出（line 449-533）

**Rotor 1**:
```
mixer_1_pitch = pitch_mix * pitch_gain_1
mixer_1_roll = roll_mix * roll_gain_1
mixer_1_yaw = yaw_mix * yaw_gain_1
mixer_1_first = mixer_1_yaw + mixer_1_pitch
mixer_1 = mixer_1_first + mixer_1_roll
rotor_1_sum = mixer_1 + z_pid  (加推力基准)
y = rotor_1_sum * rotor_1_sign
```

**Rotor 2**: → y1  
**Rotor 3**: → y2  
**Rotor 4**: → y3

**混合增益矩阵**（需要从代码中提取具体值）

---

## AttitudeTrackingCore设计规格

### 输入端口（7个）
1. `desired_roll_rad` (RealInput/Inport)
2. `desired_pitch_rad` (RealInput/Inport)
3. `desired_yaw_rad` (RealInput/Inport) ← 或固定为0
4. `roll_mea` (RealInput/Inport)
5. `pitch_mea` (RealInput/Inport)
6. `yaw_mea` (RealInput/Inport)
7. `collective_thrust_n` (RealInput/Inport) ← 推力基准

### 输出端口（4个）
1. `amplitude_1` (RealOutput/Outport) → rotor 1幅值指令
2. `amplitude_2` (RealOutput/Outport) → rotor 2幅值指令
3. `amplitude_3` (RealOutput/Outport) → rotor 3幅值指令
4. `amplitude_4` (RealOutput/Outport) → rotor 4幅值指令

### 内部结构

**方案A：完全复制OfficialPid内环**
- 优点：已验证的控制增益，直接可用
- 缺点：复杂度高（滤波微分器、混合矩阵）

**方案B：简化PD姿态控制**
- 姿态误差 → 简化PD → 标准X型四旋翼混合矩阵
- 优点：结构清晰，易于调试
- 缺点：需要重新调参，可能性能不如原版

**推荐**：先采用方案A（完全复制），确保功能正确后再考虑简化

---

## 实施步骤

### Phase 1: 完整读取OfficialPid姿态控制部分
- [ ] 读取yaw通道完整实现（line 187-？）
- [ ] 提取所有mixer增益参数
- [ ] 确认推力基准（z_pid）如何生成和使用

### Phase 2: 创建AttitudeTrackingCore Sysblock
- [ ] 创建`Models/MoSimQuadrotorModel/Control/InnerLoop/AttitudeTrackingCore.mo`
- [ ] 创建`Models/MoSimQuadrotorModel/Control/InnerLoop/package.mo`
- [ ] 实现Sysblock组件：
  - 7个Inport声明
  - 4个Outport声明
  - 完整姿态PD控制逻辑（复制OfficialPid line 129-186 + yaw部分）
  - 混合矩阵逻辑（复制line 449-533）
  - 添加`__MWORKS(SECInstance = true)`注解

### Phase 3: 创建信号适配器
- [ ] 创建`AttitudeSignalAdapter.mo`（Modelica组件）
  - 输入：LqrBaselineCore的desired_roll/pitch_rad_out + collective_thrust_n_out
  - 输入：plant的roll/pitch/yaw_mea
  - 输出：7个信号传递给AttitudeTrackingCore
- [ ] 或直接在LqrBaselineGraphicalRunner中连接（如果端口类型兼容）

### Phase 4: 修改LqrBaselineGraphicalRunner
- [ ] 添加AttitudeTrackingCore组件声明
- [ ] 修改连接链路：
  ```
  原架构：
    LqrBaselineCore.desired_roll_rad_out → GraphicalAttitudeThrustRotorPreview.roll_ref

  新架构：
    LqrBaselineCore.desired_roll_rad_out → AttitudeTrackingCore.desired_roll_rad
    LqrBaselineCore.desired_pitch_rad_out → AttitudeTrackingCore.desired_pitch_rad
    LqrBaselineCore.collective_thrust_n_out → AttitudeTrackingCore.collective_thrust_n
    plant.attitude[1] → AttitudeTrackingCore.roll_mea
    plant.attitude[2] → AttitudeTrackingCore.pitch_mea
    plant.attitude[3] → AttitudeTrackingCore.yaw_mea
    AttitudeTrackingCore.amplitude_1/2/3/4 → BaselineRotorMapper或fault_compensator
  ```
- [ ] 移除GraphicalAttitudeThrustRotorPreview

### Phase 5: 验证测试
- [ ] CheckModel验证
- [ ] 50s ClimbPath仿真
- [ ] 检查跟踪误差是否<5m
- [ ] 对比修复前后的position_error_norm曲线

---

## 关键技术细节

### 1. 端口类型兼容性
- **LqrBaselineCore输出**: Sysblock `Outport`
- **plant.attitude**: Modelica `RealOutput[3]`
- **AttitudeTrackingCore输入**: Sysblock `Inport`

**问题**: Sysblock Inport能否直接接收Modelica RealOutput？
**答案**: 不能！需要Modelica adapter（与前面的LqrSignalAdapter同理）

**解决方案**:
```
plant.attitude[1/2/3] → AttitudeSignalAdapter (Modelica) → AttitudeTrackingCore (Sysblock)
LqrBaselineCore.desired_*_out (Sysblock Outport) → 是否需要adapter？
```

**需要确认**: Sysblock Outport能否直接连接到另一个Sysblock的Inport？
- 如果可以：LqrBaselineCore → AttitudeTrackingCore 直连
- 如果不可以：需要中间Modelica passthrough

### 2. 推力基准转换
OfficialPid的`z_pid`输出是高度PID的结果，单位可能是幅值或归一化推力。
LqrBaselineCore输出`collective_thrust_n_out`，单位是牛顿(N)。

**需要确认**:
1. OfficialPid的z_pid单位是什么？
2. collective_thrust_n如何转换为与z_pid相同的单位？
3. 混合矩阵中的推力基准加法是否需要缩放？

### 3. Yaw设定值来源
LqrBaselineGraphicalRunner当前使用`zero.y`作为yaw参考（line 108）。
AttitudeTrackingCore的yaw_ref应该：
- 方案A：接收外部输入（从LqrBaselineGraphicalRunner的zero常量）
- 方案B：内部硬编码为0

---

## 待解决问题

1. **读取OfficialPid yaw通道完整实现**
2. **提取混合矩阵增益**（需要读取mixer_*_pitch_gain等组件的k值）
3. **确认Sysblock Outport→Inport是否需要adapter**
4. **确认推力单位转换关系**
5. **决定是否需要独立的AttitudeSignalAdapter**

---

## 下一步行动

**立即执行**: 读取OfficialPidGraphicalCore line 187-250（yaw通道+混合增益）
