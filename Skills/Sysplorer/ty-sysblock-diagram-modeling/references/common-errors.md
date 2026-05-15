# 常见错误与修复

本文档汇总 Sysblock 建模过程中的常见错误及修复方案。

## 1. 模型创建错误

### 1.1 "模型没有打开"

**错误信息：**
```
Error: 模型 'ModelName' 没有打开
```

**原因：**
- 在调用 `AddComponent` 或`SetModelParamValue`前未先打开模型

**修复方案：**
```python
# 先打开模型
ModelingPy.OpenModel("ModelName")
# 再进行其他操作
ModelingPy.AddComponent("ModelName", model_text)
```

### 1.2 "模型已存在"

**错误信息：**
```
Error: 模型 'ModelName' 已存在
```

**原因：**
- 尝试创建已存在的同名模型

**修复方案：**
```python
# 选项1: 删除旧模型
ModelingPy.EraseClasses("ModelName")

# 选项2: 使用不同名称
ModelingPy.NewModel("NewModelName", "Sysblock")
```

## 2. 组件错误

### 2.1 "组件类型不存在"

**错误信息：**
```
Error: 组件类型 'SysplorerEmbeddedCoder.XXX.YYY' 不存在
```

**可能原因：**
1. 组件路径错误
2. 子包名称错误
3. 组件未在库中

**修复方案：**
```python
# 检查正确的组件路径
# 错误：SysplorerEmbeddedCoder.Math.Gain  
# 正确：SysplorerEmbeddedCoder.MathOperation.Gain
```

### 2.2 "组件名称重复"

**错误信息：**
```
Error: 模型中已存在名为 'XXX' 的组件
```

**修复方案：**
```python
# 使用唯一名称
ModelingPy.AddComponent(type, model, "new_name", x, y)
```

### 2.3 参数名称错误

**错误信息：**
```
Error: 参数 'XXX' 不存在
```

**修复方案：**
```python
# 检查正确的参数名称
# Step 组件参数：Time, Before, After (不是 stepTime, initialValue, finalValue)
# Gain 组件参数：Gain (不是 k)
# Sum 组件参数：Inputs (不是 inputs 或 sign)
```

## 3. 连接错误

### 3.1 "端口不存在"

**错误信息：**
```
Error: port 'XXX' not found
```

**常见原因与修复：**

| 错误写法 | 正确写法 |
|----------|----------|
| `step.out` | `step.y` |
| `gain.output` | `gain.y` |
| `integrator.in` | `integrator.u1` |
| `sum.input1` | `sum.u1` |

### 3.2 "Algebraic Loop" (代数环)

**错误信息：**
```
Warning: Algebraic loop detected
```

**原因：**
- 存在直接反馈，没有延迟

**修复方案：**
```python
# 在反馈路径中添加 UnitDelay
ModelingPy.AddComponent(
    "SysplorerEmbeddedCoder.Discrete.UnitDelay", 
    model_name, 
    "delay", 
    x, y
)
ModelingPy.ConnectPort(model_name, "feedback.y", "delay.u1")
ModelingPy.ConnectPort(model_name, "delay.y", "error_sum.u2")
```

## 4. 仿真错误

### 4.1 "模型检查失败"

**错误信息：**
```
Error: 模型检查失败
```

**排查步骤：**
1. 运行 check_model 获取详细错误
2. 检查模型文本语法
3. 检查所有组件是否正确声明
4. 检查 connect 语句

### 4.2 "仿真超时"

**可能原因：**
1. 仿真时间设置过长
2. 模型存在不稳定环节
3. 求解器不收敛

**修复方案：**
```python
# 减少仿真时间
ModelingPy.SimulateModelEx("ModelName", {"stopTime": 1.0})

# 或更换求解器
ModelingPy.SetModelExperiment("ModelName", {
    "Algorithm": "RungaKutta"
})
```

### 4.3 "积分饱和"

**原因：**
- 积分器输出超出限制

**修复方案：**
```python
# 设置积分器限幅
ModelingPy.SetModelParamValue(model, "integrator", "LimitOutput", "true")
ModelingPy.SetModelParamValue(model, "integrator", "UpperSaturationLimit", "100")
ModelingPy.SetModelParamValue(model, "integrator", "LowerSaturationLimit", "0")
```

## 5. 代码生成错误

### 5.1 "模块暂不支持代码生成"

**错误信息：**
```
Error: "DC_Motor_PI_Sysblock.Integrator" 模块暂不支持嵌入式代码生成
Error: "DC_Motor_PI_Sysblock.Motor" 模块暂不支持嵌入式代码生成
```

**原因：**
- Integrator、TransferFcn 等连续组件不支持代码生成

**说明：**
- 这是 Sysblock 组件的限制

### 5.2 "数据类型不匹配"

**错误信息：**
```
Error: 数据类型不匹配
```

**修复方案：**
- 确保输入输出端口数据类型一致
- 使用 Gain 组件进行类型转换

## 6. 结果获取错误

### 6.1 "变量不存在"

**错误信息：**
```
Error: 变量 'XXX' 不存在
```

**修复方案：**
```python
# 先获取变量列表
ModelingPy.GetResultVariables()

# 确认变量名格式
# 正确格式: "component.y"
# 例如: "motor.y", "scope.u1"
```

### 6.2 "结果为空"

**可能原因：**
1. 仿真未成功
2. 变量未连接到输出

**排查步骤：**
1. 检查仿真是否成功
2. 检查 Scope 或 Display 是否连接
3. 检查仿真时间是否足够

## 7. 错误排查顺序

遇到错误时，按以下顺序排查：

```
1. 检查模型是否打开
   └─> OpenModel()

2. 检查组件类型路径是否正确
   └─> 使用完整的 SysplorerEmbeddedCoder.xxx.Component 路径

3. 检查端口名称是否正确
   └─> .y (输出), .u (输入), .u1/.u2 (多输入)

4. 检查参数名称是否正确
   └-> 参考 component-mapping.md

5. 检查连接是否形成闭环
   └-> 检查每条 connect 语句

6. 检查模型检查结果
   └-> check_model()

7. 检查仿真配置
   └-> StopTime, Interval, Solver
```

## 8. 错误日志获取

```python
# 获取上一个命令的错误信息
error = ModelingPy.GetLastErrors()
print(error)

# 获取当前模型的信息
info = ModelingPy.GetModelInfo("ModelName")
print(info)
```