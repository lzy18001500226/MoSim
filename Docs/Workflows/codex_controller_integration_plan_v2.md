# Codex 控制器接入方案（修订版 v2.0）

> **重大发现**：经过全面清点，41 个 graphical_control_core 控制器的 Adapter + GraphicalRunner 已全部存在。
> **任务性质变更**：从"创建"改为"验证 + 补全 FormalRunner"。
> **风险评估**：大幅降低，主要为验证任务，破坏性操作极少。

---

## 一、实际状态清点（2026-08-18）

### 1.1 控制器总数（权威来源：catalog.json）

```
总计：46 个 implemented scheme
├── graphical_control_core: 41 个
│   └── 所有控制器都有独立的控制器核心，通过 Adapter 连接到执行器
│
└── full_profile_whole_aircraft: 5 个（Sysblock 整机模板）
    └── 完整闭环系统，不经过 Adapter 层
```

### 1.2 Adapter 覆盖率

**状态**：✅ **41/41 (100%)** — 所有控制器已有对应 Adapter

**位置**：`Models/MoSimQuadrotorModel/Control/Adapters/`

**命名规范**：`{ControllerName}{OutputBoundary}Adapter`

**特例（7 个）**：
- `official_pid` → `OfficialPIDGraphicalRotorAdapter`（ROTOR_COMMAND）
- `lqi_baseline` → `LqiAttitudeThrustAdapter`（省略 Baseline）
- `hinf_hover_wrench` → `HinfHoverWrenchAdapter`（WRENCH，省略边界后缀）
- `dfbc_high_order_bodyrate` → `DfbcHighOrderBodyRateAdapter`
- `dfbc_smooth_robust_bodyrate` → `DfbcSmoothRobustBodyRateAdapter`
- 其余 36 个控制器遵循标准命名

### 1.3 GraphicalRunner 覆盖率

**状态**：✅ **41/41 (100%)** — 所有控制器已有标准运行器

**位置**：`Models/MoSimQuadrotorModel/Experiment/{Package}/`

**命名规范**：`{ControllerName}GraphicalRunner`

**Package 映射**（catalog → 实际目录）：

| catalog package | 实际 Experiment 子目录 | 控制器数量 |
|----------------|----------------------|-----------|
| PidFamily | `PidFamily/` | 5 |
| ClassicRobust | `LinearRobustStateFeedback/` + `NonlinearAdaptive/` | 13 (6+7) |
| SlidingMode | `SlidingMode/` | 7 |
| GeometricFlatness | `GeometricFlatness/` | 6 |
| Optimization | `OptimizationPredictive/` | 8 |
| Learning | `Learning/` | 2 |

### 1.4 FormalRunner 覆盖率

**状态**：⚠️ **36/41 (87.8%)** — 5 个控制器缺少 FormalRunner

**位置**：`Models/MoSimQuadrotorModel/Experiment/Runners/Formal/`

**缺失的 5 个**：
1. `dfbc_high_order_attitude` → `DfbcHighOrderAttitudeFormalRunner`
2. `dfbc_smooth_robust_attitude` → `DfbcSmoothRobustAttitudeFormalRunner`
3. `lqi_baseline` → `LqiBaselineFormalRunner`
4. `nmpc_outer` → `NmpcOuterFormalRunner`
5. `smc_boundary_layer` → `SmcBoundaryLayerFormalRunner`

---

## 二、Codex 任务重新定义

### 2.1 原计划 vs 实际需求

| 原计划任务 | 实际状态 | 新任务 |
|-----------|---------|--------|
| 创建 41 个 Adapter | ✅ 已全部存在 | ~~不需要~~ |
| 创建 41 个 Runner | ✅ GraphicalRunner 已全部存在 | ~~不需要~~ |
| 注册 package.order | ✅ 已注册 | ~~不需要~~ |
| 验证编译 | ❓ 未验证 | **P1：批量 CheckModel** |
| 补全 FormalRunner | ⚠️ 缺 5 个 | **P2：创建 5 个 FormalRunner** |
| 拆解整机模板 | ❌ 未开始 | **P3：拆解 5 个模板** |

### 2.2 新的优先级排序

**P0（已完成）**：
- ✅ 清理 19 个遗留 Adapter（已归档）
- ✅ 清点模型库现状（本次调查）

**P1（高优先级，验证任务）**：
1. **批量 CheckModel 验证**（预计 20-30 分钟）
   - 对 41 个 Adapter 执行 CheckModel
   - 对 41 个 GraphicalRunner 执行 CheckModel
   - 对 36 个现有 FormalRunner 执行 CheckModel
   - 生成验证报告，记录所有失败项

2. **检查 package.order 一致性**
   - 验证所有 Adapter 都在 `Control/Adapters/package.order` 中注册
   - 验证所有 GraphicalRunner 都在各自 Package 的 package.order 中注册

**P2（中优先级，补全任务）**：
3. **补全 5 个 FormalRunner**（预计 30-60 分钟）
   - 参考已有 36 个 FormalRunner 的模板
   - 为 5 个缺失控制器创建 FormalRunner
   - 注册到 `Experiment/Runners/Formal/package.order`
   - 执行 CheckModel 验证

**P3（低优先级，拆解任务）**：
4. **拆解 5 个 Sysblock 整机模板**（预计 2-4 小时）
   - 提取 Sysblock 控制器核心
   - 创建标准 Adapter 和 FormalRunner
   - 保留原始模板作为参考
   - 更新 catalog.json

---

## 三、P1 任务详细方案：批量验证

### 3.1 验证脚本 1：Adapter CheckModel

```python
import json

catalog = json.load(open('Config/control_platform/control_scheme_catalog.json'))
graphical_schemes = [s for s in catalog['schemes'] 
                     if s['execution_kind'] == 'graphical_control_core'
                     and s['implementation_status'] == 'implemented']

# Adapter 名称映射（处理 7 个特例）
adapter_map = {
    'official_pid': 'OfficialPIDGraphicalRotorAdapter',
    'lqi_baseline': 'LqiAttitudeThrustAdapter',
    'hinf_hover_wrench': 'HinfHoverWrenchAdapter',
    'dfbc_high_order_bodyrate': 'DfbcHighOrderBodyRateAdapter',
    'dfbc_smooth_robust_bodyrate': 'DfbcSmoothRobustBodyRateAdapter'
}

def to_pascal_case(s):
    return ''.join(w.capitalize() for w in s.split('_'))

failed_adapters = []
passed_adapters = []

for scheme in graphical_schemes:
    scheme_id = scheme['scheme_id']
    
    # 获取 Adapter 名称
    if scheme_id in adapter_map:
        adapter_name = adapter_map[scheme_id]
    else:
        output_boundary = scheme.get('output_boundary', 'ATTITUDE_THRUST')
        boundary_part = ''.join(w.capitalize() for w in output_boundary.split('_'))
        adapter_name = f"{to_pascal_case(scheme_id)}{boundary_part}Adapter"
    
    # CheckModel
    print(f"Checking {adapter_name}...")
    result = mcp__sysplorer__check_model(
        model_name=f"MoSimQuadrotorModel.Control.Adapters.{adapter_name}"
    )
    
    if result.get('ok'):
        passed_adapters.append(scheme_id)
        print(f"  ✓ OK")
    else:
        failed_adapters.append({
            'scheme_id': scheme_id,
            'adapter': adapter_name,
            'error': result.get('error', 'Unknown error')
        })
        print(f"  ✗ FAILED: {result.get('error')}")

print(f"\nAdapter CheckModel Results:")
print(f"  Passed: {len(passed_adapters)}/41")
print(f"  Failed: {len(failed_adapters)}/41")

if failed_adapters:
    print("\nFailed adapters:")
    for f in failed_adapters:
        print(f"  - {f['scheme_id']}: {f['error'][:80]}")
```

### 3.2 验证脚本 2：GraphicalRunner CheckModel

```python
# Package 映射
package_map = {
    'PidFamily': 'PidFamily',
    'SlidingMode': 'SlidingMode',
    'GeometricFlatness': 'GeometricFlatness',
    'Optimization': 'OptimizationPredictive',
    'Learning': 'Learning',
    'ClassicRobust': None  # 需要额外处理
}

# ClassicRobust 分包规则
classic_robust_map = {
    'LinearRobustStateFeedback': [
        'h2_state_feedback', 'hinf_hover_wrench', 'lqg',
        'lqi_baseline', 'lqr_baseline', 'pole_placement_luenberger'
    ],
    'NonlinearAdaptive': [
        'adaptive_backstepping', 'backstepping_baseline',
        'feedback_linearization', 'mrac', 'ndi',
        'passivity_based_control'
    ]
}

failed_runners = []
passed_runners = []

for scheme in graphical_schemes:
    scheme_id = scheme['scheme_id']
    catalog_package = scheme['implementation_package']
    
    # 确定实际 Package
    if catalog_package == 'ClassicRobust':
        if scheme_id in classic_robust_map['LinearRobustStateFeedback']:
            actual_package = 'LinearRobustStateFeedback'
        elif scheme_id in classic_robust_map['NonlinearAdaptive']:
            actual_package = 'NonlinearAdaptive'
        else:
            print(f"Warning: {scheme_id} not in ClassicRobust map")
            continue
    else:
        actual_package = package_map.get(catalog_package, catalog_package)
    
    runner_name = to_pascal_case(scheme_id) + 'GraphicalRunner'
    
    # CheckModel
    print(f"Checking {runner_name}...")
    result = mcp__sysplorer__check_model(
        model_name=f"MoSimQuadrotorModel.Experiment.{actual_package}.{runner_name}"
    )
    
    if result.get('ok'):
        passed_runners.append(scheme_id)
        print(f"  ✓ OK")
    else:
        failed_runners.append({
            'scheme_id': scheme_id,
            'runner': runner_name,
            'package': actual_package,
            'error': result.get('error', 'Unknown error')
        })
        print(f"  ✗ FAILED: {result.get('error')}")

print(f"\nGraphicalRunner CheckModel Results:")
print(f"  Passed: {len(passed_runners)}/41")
print(f"  Failed: {len(failed_runners)}/41")
```

---

## 四、P2 任务详细方案：补全 5 个 FormalRunner

### 4.1 FormalRunner 模板（参考已有实现）

```modelica
within MoSimQuadrotorModel.Experiment.Runners.Formal;
model {ControllerName}FormalRunner
  "{scheme_id} formal runner for standardized testing"
  extends MoSimQuadrotorModel.Experiment.Runners.Base.Formal{OutputBoundary}RunnerBase(
    redeclare MoSimQuadrotorModel.Control.Adapters.{AdapterName} formal_adapter
  );
  annotation(__MWORKS(hide = false, version = "26.3.0"));
end {ControllerName}FormalRunner;
```

### 4.2 需要创建的 5 个 FormalRunner

#### 1. DfbcHighOrderAttitudeFormalRunner

```modelica
within MoSimQuadrotorModel.Experiment.Runners.Formal;
model DfbcHighOrderAttitudeFormalRunner
  "dfbc_high_order_attitude formal runner for standardized testing"
  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare MoSimQuadrotorModel.Control.Adapters.DfbcHighOrderAttitudeThrustAdapter formal_adapter
  );
  annotation(__MWORKS(hide = false, version = "26.3.0"));
end DfbcHighOrderAttitudeFormalRunner;
```

#### 2. DfbcSmoothRobustAttitudeFormalRunner

```modelica
within MoSimQuadrotorModel.Experiment.Runners.Formal;
model DfbcSmoothRobustAttitudeFormalRunner
  "dfbc_smooth_robust_attitude formal runner for standardized testing"
  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare MoSimQuadrotorModel.Control.Adapters.DfbcSmoothRobustAttitudeThrustAdapter formal_adapter
  );
  annotation(__MWORKS(hide = false, version = "26.3.0"));
end DfbcSmoothRobustAttitudeFormalRunner;
```

#### 3. LqiBaselineFormalRunner

```modelica
within MoSimQuadrotorModel.Experiment.Runners.Formal;
model LqiBaselineFormalRunner
  "lqi_baseline formal runner for standardized testing"
  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare MoSimQuadrotorModel.Control.Adapters.LqiAttitudeThrustAdapter formal_adapter
  );
  annotation(__MWORKS(hide = false, version = "26.3.0"));
end LqiBaselineFormalRunner;
```

#### 4. NmpcOuterFormalRunner

```modelica
within MoSimQuadrotorModel.Experiment.Runners.Formal;
model NmpcOuterFormalRunner
  "nmpc_outer formal runner for standardized testing"
  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare MoSimQuadrotorModel.Control.Adapters.NmpcOuterAttitudeThrustAdapter formal_adapter
  );
  annotation(__MWORKS(hide = false, version = "26.3.0"));
end NmpcOuterFormalRunner;
```

#### 5. SmcBoundaryLayerFormalRunner

```modelica
within MoSimQuadrotorModel.Experiment.Runners.Formal;
model SmcBoundaryLayerFormalRunner
  "smc_boundary_layer formal runner for standardized testing"
  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare MoSimQuadrotorModel.Control.Adapters.SmcBoundaryLayerAttitudeThrustAdapter formal_adapter
  );
  annotation(__MWORKS(hide = false, version = "26.3.0"));
end SmcBoundaryLayerFormalRunner;
```

### 4.3 注册到 package.order

读取 `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/package.order`，按字母顺序插入 5 个新条目。

---

## 五、执行约束（与原方案一致）

### 5.1 硬约束（违反则失败）

1. **禁止修改已标定参数**（CLAUDE.md 第4节）
2. **禁止 git 操作**
3. **Adapter/Runner 必须继承正确的 Base 类**
4. **文件必须在 package.order 中注册**

### 5.2 Sysplorer 环境要求

- 确认 Sysplorer MCP 可用：`mcp__sysplorer__session_manager(action="health")`
- 工作目录：`C:\Users\HP\Desktop\MoSim`
- Python 解释器：`D:/Dev/Anaconda3/python.exe`

---

## 六、成功标准（修订版）

### 6.1 P1 完成标准（验证任务）

- [ ] 41 个 Adapter 全部通过 CheckModel（或记录失败原因）
- [ ] 41 个 GraphicalRunner 全部通过 CheckModel（或记录失败原因）
- [ ] 36 个现有 FormalRunner 通过 CheckModel（或记录失败原因）
- [ ] 生成验证报告：`Docs/Cache/controller_checkmodel_report.md`

### 6.2 P2 完成标准（补全任务）

- [ ] 5 个新 FormalRunner 文件创建完成
- [ ] 5 个新 FormalRunner 在 package.order 中注册
- [ ] 5 个新 FormalRunner 通过 CheckModel
- [ ] FormalRunner 覆盖率：41/41 (100%)

### 6.3 P3 完成标准（拆解任务）

- [ ] 5 个 Sysblock 控制器核心提取完成
- [ ] 5 个对应的 Adapter 和 FormalRunner 创建完成
- [ ] catalog.json 更新（新增 5 个 scheme_id）
- [ ] 原始整机模板保留作为参考

---

## 七、风险评估（大幅降低）

### 7.1 原计划风险

- ❌ 创建 41 个 Adapter（命名可能不一致）
- ❌ 创建 41 个 Runner（可能破坏 package.order）
- ❌ 可能引入大量编译错误

### 7.2 新方案风险

- ✅ P1 任务为只读验证，无破坏性
- ⚠️ P2 任务仅创建 5 个文件，有现成模板
- ⚠️ P3 任务需要提取控制器核心，风险可控

---

## 八、Codex 执行清单更新

**原清单**：`Docs/Workflows/codex_execution_checklist.md`  
**需要更新**：将"阶段 3：单个控制器接入"改为"阶段 3：FormalRunner 补全"

**新的执行流程**：
1. 阶段 1：环境准备（不变）
2. 阶段 2：批次规划（改为"验证批次规划"）
3. 阶段 3：批量验证（CheckModel）
4. 阶段 4：补全 5 个 FormalRunner
5. 阶段 5：整机模板拆解（不变）
6. 阶段 6：最终验证（不变）

---

**方案版本**：v2.0（重大修订）  
**创建日期**：2026-08-18  
**修订原因**：发现 Adapter + GraphicalRunner 已全覆盖，任务性质从"创建"改为"验证+补全"  
**作者**：Claude Code  
**审核者**：待用户确认
