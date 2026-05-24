# 组件映射表

本文档将自然语言需求映射为 SysplorerEmbeddedCoder 库中的具体组件。

## 1. 信号源 (Sources)

| 需求关键词 | 组件路径 | 主要参数 |
|------------|----------|----------|
| 阶跃信号 | `SysplorerEmbeddedCoder.Sources.Step` | Time, Before, After |
| 正弦波 | `SysplorerEmbeddedCoder.Sources.SineWave` | Amplitude, Frequency, Phase |
| 斜坡信号 | `SysplorerEmbeddedCoder.Sources.Ramp` | Slope, StartTime |
| 脉冲 | `SysplorerEmbeddedCoder.Sources.PulseGenerator` | Amplitude, Period, DutyCycle |
| 常数 | `SysplorerEmbeddedCoder.Sources.Constant` | Value |
| 随机数 | `SysplorerEmbeddedCoder.Sources.RandomNumber` | Minimum, Maximum |
| 时钟 | `SysplorerEmbeddedCoder.Sources.Clock` | - |

## 2. 数学运算 (MathOperation)

| 需求关键词 | 组件路径 | 主要参数 |
|------------|----------|----------|
| 增益 | `SysplorerEmbeddedCoder.MathOperation.Gain` | Gain (k) |
| 加法器 | `SysplorerEmbeddedCoder.MathOperation.Sum` | Inputs (如 "++-") |
| 乘法器 | `SysplorerEmbeddedCoder.MathOperation.Product` | Inputs |
| 绝对值 | `SysplorerEmbeddedCoder.MathOperation.Abs` | - |
| 平方根 | `SysplorerEmbeddedCoder.MathOperation.Sqrt` | - |
| 符号 | `SysplorerEmbeddedCoder.MathOperation.Sign` | - |
| 最小值 | `SysplorerEmbeddedCoder.MathOperation.Min` | - |
| 最大值 | `SysplorerEmbeddedCoder.MathOperation.Max` | - |
| 限幅 | `SysplorerEmbeddedCoder.MathOperation.Limiter` | UpperLimit, LowerLimit |
| 滞环 | `SysplorerEmbeddedCoder.MathOperation.Hysteresis` | width |
| 三角函数 | `SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction` | Operator |

## 3. 连续系统 (Continuous)

| 需求关键词 | 组件路径 | 主要参数 |
|------------|----------|----------|
| 积分器 | `SysplorerEmbeddedCoder.Continuous.Integrator` | InitCond, UpperSaturationLimit, LowerSaturationLimit |
| 微分器 | `SysplorerEmbeddedCoder.Continuous.Derivative` | - |
| 传递函数 | `SysplorerEmbeddedCoder.Continuous.TransferFcn` | Numerator, Denominator |
| 状态空间 | `SysplorerEmbeddedCoder.Continuous.StateSpace` | A, B, C, D |
| PID | `SysplorerEmbeddedCoder.Continuous.PIDController` | Kp, Ki, Td |
| 二阶系统 | `SysplorerEmbeddedCoder.Continuous.SecondOrderSystem` | wn, zeta |
| 时滞 | `SysplorerEmbeddedCoder.Continuous.TimeDelay` | DelayTime |

## 4. 离散系统 (Discrete)

| 需求关键词 | 组件路径 | 主要参数 |
|------------|----------|----------|
| 单位延迟 | `SysplorerEmbeddedCoder.Discrete.UnitDelay` | InitialCondition |
| 离散积分 | `SysplorerEmbeddedCoder.Discrete.DiscreteIntegrator` | - |
| 离散传递函数 | `SysplorerEmbeddedCoder.Discrete.DiscreteTransferFcn` | Numerator, Denominator |
| 离散状态空间 | `SysplorerEmbeddedCoder.Discrete.DiscreteStateSpace` | A, B, C, D |
| 零阶保持 | `SysplorerEmbeddedCoder.Discrete.ZeroOrderHold` | SampleTime |
| 一阶保持 | `SysplorerEmbeddedCoder.Discrete.FirstOrderHold` | SampleTime |

## 5. 逻辑与位运算 (LogicAndBitOperation)

| 需求关键词 | 组件路径 | 主要参数 |
|------------|----------|----------|
| 关系运算 | `SysplorerEmbeddedCoder.LogicAndBitOperation.RelationalOperator` | Operator (>, <, >=, <=, ==, ~=) |
| 逻辑与 | `SysplorerEmbeddedCoder.LogicAndBitOperation.LogicalOperator` | Operator (and, or, not, xor) |
| 组合逻辑 | `SysplorerEmbeddedCoder.LogicAndBitOperation.CombinatorialLogic` | TruthTable |
| 触发器 | `SysplorerEmbeddedCoder.LogicAndBitOperation.SRFlipFlop` | - |
| 边沿检测 | `SysplorerEmbeddedCoder.LogicAndBitOperation.RisingEdge` | - |

## 6. 端口 (Ports)

| 需求关键词 | 组件路径 | 说明 |
|------------|----------|------|
| 输入端口 | `SysplorerEmbeddedCoder.Ports.Inport` | 模型输入 |
| 输出端口 | `SysplorerEmbeddedCoder.Ports.Outport` | 模型输出 |

## 7. 观测与输出 (Sinks)

| 需求关键词 | 组件路径 | 主要参数 |
|------------|----------|----------|
| 示波器 | `SysplorerEmbeddedCoder.Utilities.Scope` | - |
| 显示 | `SysplorerEmbeddedCoder.Utilities.Display` | - |
| 输出到工作区 | `SysplorerEmbeddedCoder.Utilities.ToWorkspace` | VariableName |
| XY 绘图 | `SysplorerEmbeddedCoder.Utilities.XYGraph` | - |

## 8. 常用控制场景组件映射

### 8.1 PI 控制器

```
误差 -> Sum ("+-") -> [Kp -> Sum ("++")] -> [Ki -> Integrator -> Sum ("++")]
                              ↓
                          被控对象
```

**组件列表：**
1. `SysplorerEmbeddedCoder.Sources.Step` - 给定信号
2. `SysplorerEmbeddedCoder.MathOperation.Sum` - 误差计算
3. `SysplorerEmbeddedCoder.MathOperation.Gain` - Kp
4. `SysplorerEmbeddedCoder.MathOperation.Gain` - Ki
5. `SysplorerEmbeddedCoder.Continuous.Integrator` - 积分环节
6. `SysplorerEmbeddedCoder.MathOperation.Sum` - PI 输出
7. `SysplorerEmbeddedCoder.Continuous.TransferFcn` - 被控对象
8. `SysplorerEmbeddedCoder.Utilities.Scope` - 观测

### 8.2 电机速度控制

```
Setpoint -> [Sum ("+-")] -> PI_Controller -> [Sum ("++")] -> Motor -> [Sum ("+-")]
                                              ↓
                                          反馈
```

**参数设置：**
- 电机传递函数: `G(s) = K / (Ts + 1)`
  - K = 10 (增益 rpm/V)
  - T = 0.5 (时间常数 s)

### 8.3 离散 PID

```
误差 -> Sum("+-") -> [Kp] -----> 
                        |        [Ki] -> DiscreteIntegrator -> 
                                  |                        |
                        [Kd] -> Derivative ->            +-> Sum("++") -> 输出
```

## 9. 组件命名规范

### 9.1 推荐命名

| 组件类型 | 推荐命名 | 示例 |
|----------|----------|------|
| 给定/参考 | setpoint, reference, ref | setpoint |
| 误差 | error, err | error_sum |
| 比例增益 | Kp, Kp_gain | Kp |
| 积分增益 | Ki, Ki_gain | Ki |
| 微分增益 | Kd, Kd_gain | Kd |
| 控制器 | controller, pid_ctrl | controller |
| 被控对象 | plant, system, motor | plant |
| 示波器 | scope, monitor | scope |

### 9.2 连接端口命名

```python
# 输出端口
src_component.y

# 单输入端口  
dst_component.u

# 多输入端口
sum_block.u1
sum_block.u2
sum_block.u3
```

## 10. 参数默认值

### 10.1 仿真参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| StopTime | 5.0 | 仿真时间 (s) |
| Interval | 0.01 | 输出间隔 (s) |
| Solver | Euler | 求解器 |
| StartTime | 0.0 | 开始时间 |

### 10.2 控制器默认值

| 控制器 | 参数 | 初始值 |
|--------|------|--------|
| P | Kp | 1.0 |
| PI | Kp, Ki | 1.0, 1.0 |
| PID | Kp, Ki, Kd | 1.0, 1.0, 0.1 |