# Codex 执行检查清单

> **用途**：Codex 每完成一批控制器后，按此清单逐项检查，确保质量
> **更新频率**：每批次完成后更新进度

---

## 阶段 1：环境准备（执行前必读）

### 1.1 必读文档（按顺序）

- [ ] `CLAUDE.md` — 了解项目硬边界和禁止修改的参数
- [ ] `AGENTS.md` — 了解任务隔离规则
- [ ] `Docs/Workflows/codex_controller_integration_plan.md` — 本次任务完整方案
- [ ] `Config/control_platform/control_scheme_catalog.json` — 获取 46 个控制器清单
- [ ] `Models/MoSimQuadrotorModel/Control/Interfaces/AttitudeThrustAdapterBase.mo` — 理解 Adapter 接口
- [ ] `Models/MoSimQuadrotorModel/Control/Adapters/CascadePidAttitudeThrustAdapter.mo` — 参考标杆实现

### 1.2 环境检查

- [ ] 确认当前工作目录：`C:\Users\HP\Desktop\MoSim`
- [ ] 确认 Python 解释器：`D:/Dev/Anaconda3/python.exe`
- [ ] 确认 Sysplorer MCP 可用：`mcp__sysplorer__session_manager(action="health")`
- [ ] 确认归档路径：`E:\刘致远18001500226\MoSim_Archive`（只读，禁止写入）

---

## 阶段 2：批次规划

### 2.1 选择本批次控制器（建议 5 个/批）

**原则**：
- 优先同一 `implementation_package`（减少 package.order 切换）
- 优先同一 `output_boundary`（复用 Adapter 模板）
- 优先已有控制器核心文件的（避免 missing_core）

**示例批次 1（ClassicRobust + ATTITUDE_THRUST）**：
```python
batch_1 = [
    "fopid",
    "lqi_baseline", 
    "robust_h2",
    "robust_hinf",
    "robust_mu_synthesis"
]
```

### 2.2 预检查（每个控制器执行）

对于批次中的每个 `scheme_id`：

```python
import os
import json

catalog = json.load(open('Config/control_platform/control_scheme_catalog.json'))
scheme = [s for s in catalog['schemes'] if s['scheme_id'] == scheme_id][0]

# ✅ 检查 1：确认 execution_kind
assert scheme['execution_kind'] == 'graphical_control_core'

# ✅ 检查 2：确认 implementation_status
assert scheme['implementation_status'] == 'implemented'

# ✅ 检查 3：确认 output_boundary
output_boundary = scheme.get('output_boundary', 'ATTITUDE_THRUST')  # 默认 ATTITUDE_THRUST
print(f"{scheme_id} → {output_boundary}")

# ✅ 检查 4：确认 implementation_package
package = scheme['implementation_package']
package_path = f"Models/MoSimQuadrotorModel/Control/{package}"
assert os.path.exists(package_path), f"Package {package} not found"

# ✅ 检查 5：搜索控制器核心文件
core_candidates = glob.glob(f"{package_path}/*{PascalCase(scheme_id)}*.mo")
if not core_candidates:
    print(f"⚠️ {scheme_id}: No controller core found, may need manual search")
else:
    print(f"✅ {scheme_id}: Found core at {core_candidates[0]}")
```

**决策规则**：
- 如果 5 个预检查都通过 → 加入本批次
- 如果检查 5 失败（找不到 core） → 标记 `missing_core`，跳过或手动搜索
- 如果检查 3 失败（status != implemented） → 标记 `not_implemented`，跳过

---

## 阶段 3：单个控制器接入（重复 5 次）

### 3.1 创建 Adapter

#### Step 1：确定 Adapter 名称和路径

```python
from utils import to_pascal_case

scheme_id = "fopid"  # 示例
output_boundary = "ATTITUDE_THRUST"

adapter_name = f"{to_pascal_case(scheme_id)}{output_boundary.replace('_', '')}Adapter"
# 结果：FopidAttitudeThrustAdapter

adapter_path = f"Models/MoSimQuadrotorModel/Control/Adapters/{adapter_name}.mo"
```

#### Step 2：选择 Base 类

```python
base_class_map = {
    "ATTITUDE_THRUST": "MoSimQuadrotorModel.Control.Interfaces.AttitudeThrustAdapterBase",
    "BODY_RATE_THRUST": "MoSimQuadrotorModel.Control.Interfaces.BodyRateThrustAdapterBase",
    "ROTOR_COMMAND": "MoSimQuadrotorModel.Control.Interfaces.RotorCommandAdapterBase",
    "WRENCH": "MoSimQuadrotorModel.Control.Interfaces.WrenchAdapterBase"
}

base_class = base_class_map[output_boundary]
```

#### Step 3：编写 Adapter 文件

**模板**（基于 `CascadePidAttitudeThrustAdapter.mo`）：

```modelica
within MoSimQuadrotorModel.Control.Adapters;
model {adapter_name}
  "{scheme_id} controller adapter for {output_boundary} interface"
  extends {base_class};
  
  // 实例化控制器核心
  MoSimQuadrotorModel.Control.{package}.{CoreClassName} controller_core;
  
equation
  // 输入映射（从 Base 的 sensed_state / reference_trajectory 到 controller_core 的输入）
  // TODO: 根据 controller_core 的具体接口填写
  
  // 输出映射（从 controller_core 的输出到 Base 的 control_output）
  // TODO: 根据 output_boundary 填写
  
  annotation(__MWORKS(hide = false, version = "26.3.0"));
end {adapter_name};
```

**关键点**：
- **输入映射**：必须连接 `sensed_state` 和 `reference_trajectory` 到 `controller_core` 的输入端口
- **输出映射**：必须连接 `controller_core` 的输出到 `control_output`（具体格式取决于 `output_boundary`）

**参考标杆**：
```bash
# 读取标杆实现
cat Models/MoSimQuadrotorModel/Control/Adapters/CascadePidAttitudeThrustAdapter.mo
```

#### Step 4：检查清单

- [ ] 文件路径正确：`Control/Adapters/{adapter_name}.mo`
- [ ] `within` 声明：`within MoSimQuadrotorModel.Control.Adapters;`
- [ ] `extends` 正确的 Base 类
- [ ] 实例化了 `controller_core`
- [ ] 输入映射完整（没有未连接的输入端口）
- [ ] 输出映射完整（`control_output` 所有字段都有值）
- [ ] 有 `annotation(__MWORKS(...))`

### 3.2 注册 Adapter 到 package.order

```python
package_order_path = "Models/MoSimQuadrotorModel/Control/Adapters/package.order"

# 读取现有条目
with open(package_order_path, 'r') as f:
    entries = [line.strip() for line in f if line.strip()]

# 添加新 Adapter（保持字母顺序）
entries.append(adapter_name)
entries.sort()

# 写回
with open(package_order_path, 'w') as f:
    for entry in entries:
        f.write(entry + '\n')
```

**检查清单**：
- [ ] `package.order` 包含新的 `adapter_name`
- [ ] 条目按字母顺序排列
- [ ] 文件末尾有空行

### 3.3 创建 Runner

#### Step 1：确定 Runner 名称和路径

```python
runner_name = f"{to_pascal_case(scheme_id)}FormalRunner"
# 结果：FopidFormalRunner

runner_path = f"Models/MoSimQuadrotorModel/Experiment/{package}/{runner_name}.mo"
```

#### Step 2：选择 Runner Base 类

```python
runner_base_map = {
    "ATTITUDE_THRUST": "MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase",
    "BODY_RATE_THRUST": "MoSimQuadrotorModel.Experiment.Runners.Base.FormalBodyRateThrustRunnerBase",
    "ROTOR_COMMAND": "MoSimQuadrotorModel.Experiment.Runners.Base.FormalRotorCommandRunnerBase",
    "WRENCH": "MoSimQuadrotorModel.Experiment.Runners.Base.FormalWrenchRunnerBase"
}

runner_base = runner_base_map[output_boundary]
```

#### Step 3：编写 Runner 文件

**模板**：

```modelica
within MoSimQuadrotorModel.Experiment.{package};
model {runner_name}
  "Formal runner for {scheme_id} controller"
  extends {runner_base}(
    redeclare MoSimQuadrotorModel.Control.Adapters.{adapter_name} formal_adapter
  );
  annotation(__MWORKS(hide = false, version = "26.3.0"));
end {runner_name};
```

**关键点**：
- 必须有 `redeclare` 语句
- `redeclare` 的 Adapter 路径必须正确

#### Step 4：检查清单

- [ ] 文件路径正确：`Experiment/{package}/{runner_name}.mo`
- [ ] `within` 声明：`within MoSimQuadrotorModel.Experiment.{package};`
- [ ] `extends` 正确的 Runner Base 类
- [ ] `redeclare` 了正确的 Adapter
- [ ] 有 `annotation(__MWORKS(...))`

### 3.4 注册 Runner 到 package.order

```python
package_order_path = f"Models/MoSimQuadrotorModel/Experiment/{package}/package.order"

# 读取现有条目
with open(package_order_path, 'r') as f:
    entries = [line.strip() for line in f if line.strip()]

# 添加新 Runner（保持字母顺序）
entries.append(runner_name)
entries.sort()

# 写回
with open(package_order_path, 'w') as f:
    for entry in entries:
        f.write(entry + '\n')
```

**检查清单**：
- [ ] `package.order` 包含新的 `runner_name`
- [ ] 条目按字母顺序排列
- [ ] 文件末尾有空行

### 3.5 验证：Sysplorer CheckModel

**关键步骤**：分三步验证，逐步定位问题

#### Step 1：验证 Adapter

```python
from mcp__sysplorer import check_model

result = check_model(
    model_name=f"MoSimQuadrotorModel.Control.Adapters.{adapter_name}"
)

assert result['ok'] == True, f"Adapter CheckModel failed: {result.get('error')}"
```

**常见错误**：
- `Class XXX not found` → 检查 `controller_core` 的路径
- `Type mismatch` → 检查输入输出连接的类型
- `Missing component` → 检查是否实例化了 `controller_core`

#### Step 2：验证 Runner（不连接 Plant）

```python
result = check_model(
    model_name=f"MoSimQuadrotorModel.Experiment.{package}.{runner_name}"
)

assert result['ok'] == True, f"Runner CheckModel failed: {result.get('error')}"
```

**常见错误**：
- `Missing redeclare` → 检查 Runner 的 `redeclare` 语句
- `Base class not found` → 检查 Runner Base 类路径
- `Adapter not found` → 检查 Adapter 路径拼写

#### Step 3：验证 Runner（完整仿真，可选）

```python
# 可选：运行一个短时仿真验证完整闭环
result = simulate_model(
    model_name=f"MoSimQuadrotorModel.Experiment.{package}.{runner_name}",
    stop_time=5.0  # 只跑 5 秒
)

# 检查是否成功
assert result['ok'] == True
```

**检查清单**：
- [ ] Adapter CheckModel 通过
- [ ] Runner CheckModel 通过
- [ ] （可选）短时仿真无报错

---

## 阶段 4：批次完成后的检查

### 4.1 文件完整性检查

对于本批次的每个控制器：

```python
batch_controllers = ["fopid", "lqi_baseline", "robust_h2", "robust_hinf", "robust_mu_synthesis"]

for scheme_id in batch_controllers:
    # 检查 Adapter 文件存在
    adapter_path = f"Models/MoSimQuadrotorModel/Control/Adapters/{adapter_name}.mo"
    assert os.path.exists(adapter_path), f"{scheme_id}: Adapter file missing"
    
    # 检查 Runner 文件存在
    runner_path = f"Models/MoSimQuadrotorModel/Experiment/{package}/{runner_name}.mo"
    assert os.path.exists(runner_path), f"{scheme_id}: Runner file missing"
    
    # 检查 Adapter 在 package.order 中
    adapter_order = open("Models/MoSimQuadrotorModel/Control/Adapters/package.order").read()
    assert adapter_name in adapter_order, f"{scheme_id}: Adapter not in package.order"
    
    # 检查 Runner 在 package.order 中
    runner_order = open(f"Models/MoSimQuadrotorModel/Experiment/{package}/package.order").read()
    assert runner_name in runner_order, f"{scheme_id}: Runner not in package.order"
    
    print(f"✅ {scheme_id}: All files present and registered")
```

### 4.2 更新进度报告

```python
# 读取现有报告
progress_file = "Docs/Cache/controller_integration_progress.md"

# 添加本批次完成的控制器
completed_count = len(batch_controllers)
total_count = 41

# 更新报告（追加到"已完成"表格）
with open(progress_file, 'a') as f:
    for scheme_id in batch_controllers:
        f.write(f"| {scheme_id} | ✅ | ✅ | ✅ | Batch X completed |\n")
    
print(f"Progress updated: {completed_count} controllers completed (Total: {completed_count}/41)")
```

### 4.3 生成批次总结

```markdown
## 批次 X 总结（YYYY-MM-DD）

**完成数量**：5/41

**本批次控制器**：
- fopid (ClassicRobust, ATTITUDE_THRUST)
- lqi_baseline (ClassicRobust, ATTITUDE_THRUST)
- robust_h2 (ClassicRobust, ATTITUDE_THRUST)
- robust_hinf (ClassicRobust, ATTITUDE_THRUST)
- robust_mu_synthesis (ClassicRobust, ATTITUDE_THRUST)

**验证结果**：
- ✅ 所有 Adapter CheckModel 通过
- ✅ 所有 Runner CheckModel 通过
- ✅ 所有文件已注册到 package.order

**下一批次计划**：
- [ ] optimal_h2, pid_lqr_hybrid, robust_servo_lqr, state_observer_lqr, adaptive_lqr (ClassicRobust)
```

---

## 阶段 5：整体验证（所有批次完成后）

### 5.1 完整性统计

```python
import json

catalog = json.load(open('Config/control_platform/control_scheme_catalog.json'))
graphical_schemes = [s for s in catalog['schemes'] 
                     if s['execution_kind'] == 'graphical_control_core'
                     and s['implementation_status'] == 'implemented']

total = len(graphical_schemes)
completed = 0

for scheme in graphical_schemes:
    scheme_id = scheme['scheme_id']
    # 检查是否有 Adapter 和 Runner
    adapter_exists = check_adapter_exists(scheme_id)
    runner_exists = check_runner_exists(scheme_id)
    
    if adapter_exists and runner_exists:
        completed += 1

print(f"✅ Completed: {completed}/{total} ({completed/total*100:.1f}%)")
```

### 5.2 分类统计

```python
by_package = {}
by_boundary = {}

for scheme in graphical_schemes:
    pkg = scheme['implementation_package']
    boundary = scheme.get('output_boundary', 'ATTITUDE_THRUST')
    
    by_package[pkg] = by_package.get(pkg, 0) + 1
    by_boundary[boundary] = by_boundary.get(boundary, 0) + 1

print("\n按 Package 分布：")
for pkg, count in sorted(by_package.items()):
    print(f"  {pkg}: {count}")

print("\n按 Output Boundary 分布：")
for boundary, count in sorted(by_boundary.items()):
    print(f"  {boundary}: {count}")
```

### 5.3 用户验证准备

生成一个用户可直接运行的验证脚本：

```python
# 文件：Scripts/verify_all_controllers.py

import subprocess
import json

catalog = json.load(open('Config/control_platform/control_scheme_catalog.json'))
graphical_schemes = [s for s in catalog['schemes'] 
                     if s['execution_kind'] == 'graphical_control_core'
                     and s['implementation_status'] == 'implemented']

failed = []

for scheme in graphical_schemes[:5]:  # 先验证前 5 个
    scheme_id = scheme['scheme_id']
    package = scheme['implementation_package']
    runner_name = to_pascal_case(scheme_id) + "FormalRunner"
    
    print(f"Checking {scheme_id}...")
    
    # CheckModel
    result = check_model(f"MoSimQuadrotorModel.Experiment.{package}.{runner_name}")
    
    if not result['ok']:
        failed.append((scheme_id, result['error']))
        print(f"  ❌ FAILED: {result['error']}")
    else:
        print(f"  ✅ OK")

if failed:
    print(f"\n❌ {len(failed)} controllers failed:")
    for scheme_id, error in failed:
        print(f"  - {scheme_id}: {error}")
else:
    print(f"\n✅ All {len(graphical_schemes[:5])} controllers verified successfully!")
```

---

## 阶段 6：整机模板拆解（P2 优先级）

### 6.1 拆解前检查

- [ ] 已完成 41 个 graphical_control_core 的接入
- [ ] 用户已验证至少 5 个 Runner 能正常仿真
- [ ] 用户确认可以开始拆解整机模板

### 6.2 拆解流程（以 `fixed_awff_pid` 为例）

#### Step 1：读取原始整机模板

```python
template_path = "Models/MoSimQuadrotorModel/Experiment/Templates/Official/Example1AWFFSysblockClosedLoop.mo"

# 提取关键信息：
# 1. 控制器实例：AWFF_FullControllerEquation_Sysblock controller3_2;
# 2. 输入连接：x_error, y_error, z_error, ...
# 3. 输出连接：controller3_2.y, y1, y2, y3 → motor delta
```

#### Step 2：创建控制器核心

```modelica
within MoSimQuadrotorModel.Control.PidFamily;
model AwffSysblockCore
  "AWFF Sysblock controller core (extracted from whole-aircraft template)"
  
  // 标准化输入接口
  Modelica.Blocks.Interfaces.RealInput x_error;
  Modelica.Blocks.Interfaces.RealInput y_error;
  Modelica.Blocks.Interfaces.RealInput z_error;
  // ... 其他输入
  
  // 标准化输出接口（ROTOR_COMMAND）
  Modelica.Blocks.Interfaces.RealOutput motor_delta[4];
  
  // 内部 Sysblock 控制器（复用原模板的实例）
  AWFF_FullControllerEquation_Sysblock controller;
  
equation
  // 输入映射
  connect(x_error, controller.x_error);
  // ...
  
  // 输出映射
  motor_delta[1] = controller.y;
  motor_delta[2] = controller.y1;
  motor_delta[3] = controller.y2;
  motor_delta[4] = controller.y3;
  
end AwffSysblockCore;
```

#### Step 3：创建 Adapter（ROTOR_COMMAND 边界）

```modelica
within MoSimQuadrotorModel.Control.Adapters;
model AwffSysblockRotorAdapter
  "Adapter for AWFF Sysblock controller (ROTOR_COMMAND boundary)"
  extends MoSimQuadrotorModel.Control.Interfaces.RotorCommandAdapterBase;
  
  MoSimQuadrotorModel.Control.PidFamily.AwffSysblockCore controller_core;
  
equation
  // 输入映射：从 Base 提供的 sensed_state/reference_trajectory 到 controller_core
  // 需要计算 error = reference - sensed
  controller_core.x_error = reference_trajectory.position[1] - sensed_state.position[1];
  controller_core.y_error = reference_trajectory.position[2] - sensed_state.position[2];
  controller_core.z_error = reference_trajectory.position[3] - sensed_state.position[3];
  // ...
  
  // 输出映射：从 controller_core 到 Base 的 control_output
  control_output = controller_core.motor_delta;
  
end AwffSysblockRotorAdapter;
```

#### Step 4：创建 Runner

```modelica
within MoSimQuadrotorModel.Experiment.SingleUav.PidFamily;
model AwffSysblockFormalRunner
  "Formal runner for AWFF Sysblock controller"
  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalRotorCommandRunnerBase(
    redeclare MoSimQuadrotorModel.Control.Adapters.AwffSysblockRotorAdapter formal_adapter
  );
end AwffSysblockFormalRunner;
```

#### Step 5：更新 catalog

```json
{
  "scheme_id": "awff_sysblock",
  "execution_kind": "graphical_control_core",
  "implementation_package": "PidFamily",
  "output_boundary": "ROTOR_COMMAND",
  "implementation_status": "implemented",
  "derived_from": "fixed_awff_pid"
}
```

#### Step 6：验证

- [ ] `AwffSysblockCore` CheckModel 通过
- [ ] `AwffSysblockRotorAdapter` CheckModel 通过
- [ ] `AwffSysblockFormalRunner` CheckModel 通过
- [ ] 短时仿真（5 秒）无报错
- [ ] 原始整机模板文件保留在 `Templates/IntegratedChains/FixedAwffPid.mo`

### 6.3 拆解检查清单

对于 5 个整机模板，每个都需要：

- [ ] 提取控制器核心到 `Control/{Package}/`
- [ ] 创建对应的 Adapter（ROTOR_COMMAND 边界）
- [ ] 创建对应的 Runner
- [ ] 更新 catalog（新增 scheme_id，标记 `derived_from`）
- [ ] CheckModel 通过
- [ ] 原始模板文件保留作为参考

---

## 阶段 7：最终交付

### 7.1 文档整理

- [ ] `controller_integration_progress.md` 包含所有 46 个控制器状态
- [ ] `control_scheme_catalog.json` 已更新（frozen_scheme_count = 46）
- [ ] `CLAUDE.md` 操作记录已更新
- [ ] 生成最终报告：`Docs/Cache/controller_integration_final_report.md`

### 7.2 用户验证清单

交付给用户前，Codex 必须确认：

- [ ] 运行 `Px4CtrlRunner`（OpenBlocks 场景）无报错
- [ ] 运行 `ThreeUavPx4CtrlFormationRunner`（三机编队）无报错
- [ ] 随机抽查 5 个新接入的 Runner，CheckModel 通过
- [ ] 所有新增文件都在 package.order 中注册
- [ ] 没有修改任何标定参数（CLAUDE.md 第4节）
- [ ] 没有执行任何 git 操作

### 7.3 交付物清单

1. **新增文件**：
   - 41 个 Adapter（`Control/Adapters/`）
   - 41 个 Runner（`Experiment/{Package}/`）
   - 5 个拆解后的控制器核心（`Control/{Package}/`，如果拆解了整机模板）
   
2. **修改文件**：
   - `Control/Adapters/package.order`
   - 6 个 `Experiment/{Package}/package.order`
   - `Config/control_platform/control_scheme_catalog.json`
   
3. **文档**：
   - `Docs/Cache/controller_integration_progress.md`
   - `Docs/Cache/controller_integration_final_report.md`
   - `CLAUDE.md`（操作记录）

---

## 附录：常用工具函数

### A.1 字符串转换

```python
def to_pascal_case(snake_str):
    """cascade_pid → CascadePid"""
    return ''.join(word.capitalize() for word in snake_str.split('_'))

def to_adapter_name(scheme_id, output_boundary):
    """cascade_pid + ATTITUDE_THRUST → CascadePidAttitudeThrustAdapter"""
    boundary_part = ''.join(word.capitalize() for word in output_boundary.split('_'))
    return f"{to_pascal_case(scheme_id)}{boundary_part}Adapter"

def to_runner_name(scheme_id):
    """cascade_pid → CascadePidFormalRunner"""
    return f"{to_pascal_case(scheme_id)}FormalRunner"
```

### A.2 文件检查

```python
def check_adapter_exists(scheme_id, output_boundary="ATTITUDE_THRUST"):
    adapter_name = to_adapter_name(scheme_id, output_boundary)
    path = f"Models/MoSimQuadrotorModel/Control/Adapters/{adapter_name}.mo"
    return os.path.exists(path)

def check_runner_exists(scheme_id, package):
    runner_name = to_runner_name(scheme_id)
    path = f"Models/MoSimQuadrotorModel/Experiment/{package}/{runner_name}.mo"
    return os.path.exists(path)
```

### A.3 CheckModel 包装

```python
def safe_check_model(model_name, timeout=30):
    """Safe wrapper for CheckModel with timeout"""
    try:
        result = check_model(model_name=model_name)
        return result
    except Exception as e:
        return {'ok': False, 'error': str(e)}
```

---

**检查清单版本**：v1.0  
**创建日期**：2026-08-18  
**最后更新**：2026-08-18
