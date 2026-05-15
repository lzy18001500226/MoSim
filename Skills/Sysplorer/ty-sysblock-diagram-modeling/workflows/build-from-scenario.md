# Workflow A: 从场景快速搭建

本文档定义从控制场景快速搭建 Sysblock 模型的标准化流程。

## 1. 适用场景

- 用户给出明确的控制需求（如"电机转速PI控制"）
- 用户指定了系统参数（如增益、时间常数）
- 用户要求达到特定性能指标（如上升时间、超调量）

## 2. 输入要求

### 2.1 必要输入

| 输入项 | 说明 | 示例 |
|--------|------|------|
| 被控对象 | 系统数学模型 | G(s) = 10/(0.5s+1) |
| 控制器类型 | P/PI/PID | PI |
| 给定信号 | 输入类型和幅值 | 阶跃 1000 rpm |

### 2.2 可选输入

| 输入项 | 说明 | 示例 |
|--------|------|------|
| 性能指标 | 上升时间、超调量等 | 上升时间<0.4s |
| 仿真时长 | 仿真结束时间 | 5s |
| 采样周期 | 控制周期 | 0.01s |

## 3. 执行步骤

### Step 1: 需求解析

1. 解析被控对象传递函数
   - 提取增益 K
   - 提取时间常数 T
   - 写成标准形式

2. 解析控制器类型
   - P: u = Kp * e
   - PI: u = Kp * e + Ki * ∫e dt
   - PID: u = Kp * e + Ki * ∫e dt + Kd * de/dt

3. 解析性能指标
   - 提取具体数值要求

### Step 2: 模板加载

参考 `references/component-mapping.md` 形成组件表、布局表、连线表和参数表；不得依赖 `.mo` 文本模板构建 Sysblock 拓扑。

### Step 3: 参数配置

根据具体需求调整参数：

```python
# 1. 设置给定信号
SetModelParamValue(model, "setpoint", "After", "1000")

# 2. 设置被控对象
SetModelParamValue(model, "motor", "Numerator", "[10]")
SetModelParamValue(model, "motor", "Denominator", "[0.5, 1]")

# 3. 设置控制器
SetModelParamValue(model, "Kp", "Gain", "0.1")
SetModelParamValue(model, "Ki", "Gain", "0.45")
```

### Step 4: 仿真验证

1. 执行仿真
2. 获取结果变量
3. 计算性能指标
4. 对比要求

### Step 5: 参数优化（如需要）

如果性能不满足要求：

```python
# 调整增益
SetModelParamValue(model, "Kp", "Gain", "新值")
SetModelParamValue(model, "Ki", "Gain", "新值")

# 重新仿真
SimulateModelEx(model, {...})

# 重新验证
```

## 4. 典型场景示例

### 4.1 场景: 直流电机转速 PI 控制

**输入：**
- 电机传递函数: G(s) = 10 / (0.5s + 1)
- 控制器: PI
- 给定: 1000 rpm 阶跃
- 性能: 上升时间<0.4s, 超调量<10%

**执行：**

```python
# 1. 创建模型
NewModel("DC_Motor_PI_Sysblock", "Sysblock")

# 2. 添加组件
AddComponent("SysplorerEmbeddedCoder.Sources.Step", ...)
AddComponent("SysplorerEmbeddedCoder.MathOperation.Sum", ...)
AddComponent("SysplorerEmbeddedCoder.MathOperation.Gain", "Kp", ...)
AddComponent("SysplorerEmbeddedCoder.MathOperation.Gain", "Ki", ...)
AddComponent("SysplorerEmbeddedCoder.Continuous.Integrator", ...)
AddComponent("SysplorerEmbeddedCoder.Continuous.TransferFcn", "Motor", ...)
AddComponent("SysplorerEmbeddedCoder.Utilities.Scope", ...)

# 3. 连接
ConnectPort("DC_Motor_PI_Sysblock","Setpoint.y", "Error_Sum.u1")
ConnectPort("DC_Motor_PI_Sysblock","Motor.y", "Error_Sum.u2")
ConnectPort("DC_Motor_PI_Sysblock","Error_Sum.y", "Kp.u")
ConnectPort("DC_Motor_PI_Sysblock","Error_Sum.y", "Ki.u")
ConnectPort("DC_Motor_PI_Sysblock","Ki.y", "Integrator.u1")
ConnectPort("DC_Motor_PI_Sysblock","Kp.y", "PI_Sum.u1")
ConnectPort("DC_Motor_PI_Sysblock","Integrator.y", "PI_Sum.u2")
ConnectPort("DC_Motor_PI_Sysblock","PI_Sum.y", "Motor.u")

# 4. 设置参数
SetModelParamValue("DC_Motor_PI_Sysblock", "Setpoint", "finalValue", "1000")
SetModelParamValue("DC_Motor_PI_Sysblock", "Motor", "numerator", "[10]")
SetModelParamValue("DC_Motor_PI_Sysblock", "Motor", "denominator", "[0.5, 1]")
SetModelParamValue("DC_Motor_PI_Sysblock", "Kp", "Gain", "0.1")
SetModelParamValue("DC_Motor_PI_Sysblock", "Ki", "Gain", "0.45")

# 5. 仿真
SimulateModelEx("DC_Motor_PI_Sysblock", {"stopTime": 5.0, "interval": 0.01})

# 6. 验证
# 获取 Motor.y 数据，计算性能指标
```

**输出：**
- 稳态误差: 0.02% (< 1%) ✓
- 上升时间: 0.32s (< 0.4s) ✓
- 超调量: 9.05% (< 10%) ✓
- 调节时间: 1.5s (< 1.5s) ✓

## 5. 输出重点

交付时必须包含：

1. **模型文件**: 完整的 .mo 文件
2. **仿真配置**: StopTime, Interval
3. **参数清单**: 所有设置的值
4. **性能验证**: 对比要求与实际值
5. **曲线图**: 响应曲线

## 6. 模板优先级

- 优先使用 `references/component-mapping.md` 中的组件/模板映射
- 根据具体场景调整组件和参数
- 保持模板的基础结构不变
