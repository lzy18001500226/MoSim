# Sysplorer Skills 

> 版本：1.1.0 | 更新日期：2026-05-11

---

## 概述

Sysplorer Skills 是面向不同建模领域和工程场景的专用技能集合。每个 Skill 封装了特定领域的**建模规则**、**组件选型经验**、**典型工作流程**和**排障知识**，为 AI 客户端提供结构化的领域专家指导。

---

## Skill 分类一览

Sysplorer Skills 按建模领域分为 **4 大类**，共包含 **10 个 Skill**：

### 一、总规则与流程类（2 个）

| Skill 名称 | 中文名称 | 短描述 |
|------------|----------|--------|
| `ty-sysplorer-modeling-rules` | Sysplorer 建模总规则 | 范式分流、七门闸、工作路径、MCP 工具边界与布局闭环，所有建模任务的强制前置规则 |
| `modelica-library-workflow` | Modelica 模型库开发流程 | 按标准流程规划、搭建、规范化、评审与交付 Modelica 模型库 |

### 二、物理模型建模与调试类（4 个）

| Skill 名称 | 中文名称 | 短描述 |
|------------|----------|--------|
| `ty-mechanical-modeling` | TY 机械系统建模 | 使用 TY 商业库进行机械系统（1D/2D/3D 多体、传动、柔性体、接触）建模 |
| `ty-hydraulic-pneumatic-modeling` | TY 液压气动建模 | 使用 TY 内置库进行液压、热液压、气动系统建模与验证 |
| `ty-nps-library-modeling` | NPS 电气系统建模 | 使用 NPSLibrary 进行电力系统、电力电子、电机驱动与潮流建模 |
| `ty-thermofluid-modeling` | TY 热流体系统建模 | 使用 TY 热流体、换热、空气处理与通风库进行建模、修复与验证 |

### 三、Sysblock 框图模型建模与调试类（3 个）

| Skill 名称 | 中文名称 | 短描述 |
|------------|----------|--------|
| `ty-sysblock-diagram-modeling` | Sysblock 框图建模 | 使用 SysplorerEmbeddedCoder 进行嵌入式控制系统框图建模 |
| `ty-sysblock-signal-modeling` | Sysblock 信号与通信建模 | Sysblock 信号处理、通信链路建模（滤波、频谱、BER、QPSK/QAM 等） |
| `ty-sysblock-svdpi-codegen` | Sysblock SV-DPI 代码生成 | 为已有 Sysblock codegen 目录生成和校验 SV-DPI 包装 |

### 四、参数设计与优化类（1 个）

| Skill 名称 | 中文名称 | 短描述 |
|------------|----------|--------|
| `ty-design-opt-mpe-modeling` | DesignOptMpe 参数设计与优化 | 通过 DesignOptMpe 进行参数设计、MPE 参数估计、优化与标定 |

---

## 各 Skill 详细说明

### 1. ty-sysplorer-modeling-rules — Sysplorer 建模总规则

- **版本**：1.0.0
- **触发场景**：任何新建/搭建/修复/仿真模型任务
- **定位**：所有 modeling skills 的**强制前置规则**，负责范式分流、七门闸流程管控、工作路径约定、MCP 工具使用边界和布局闭环
- **核心规则**：
  - Modelica 物理模型：直接写 `.mo` 文本，禁止用 API 构建
  - Sysblock 框图模型：仅用官方 API（`run_script`/ModelingPy）构建，禁止编辑 `.mo` 文本
  - 混合模型：Sysblock 部分走 API，物理顶层走文本 `.mo`
  - 工作路径仅使用 Agent CWD 或 `GetDirectory()`，禁止使用 MCP 服务端路径
  - `check_model` 后、翻译/长仿真前必须完成图解语义与 `smart_layout`
- **严禁操作**：`ClearAll`、`ChangeDirectory`、Sysblock 中 `SetModelText`

### 2. modelica-library-workflow — Modelica 模型库开发流程

- **版本**：1.0.0
- **触发场景**：模型库包结构规范化、示例/测试、图形修复、中文本地化、评审或交付准备
- **定位**：`ty-sysplorer-modeling-rules` 的流程附加技能
- **核心工作流**：需求映射 → 模板/包设计 → 构建/扩展/规范化 → 图形修复/本地化 → 评审交付
- **特色**：
  - 按需读取引用文件（需求映射、模板包方案、跨域包策略、验收清单等）
  - 六种专用工作流（从模板构建、扩展现有库、评审、规范化、中文化、修复图形标注）
  - `package.mo` 与 `package.order` 同步维护
  - 示例（Examples）与测试（Tests）分离

### 3. ty-mechanical-modeling — TY 机械系统建模

- **版本**：1.0.0
- **触发词**：`TYDriveline`、`TYFlexBody`、`TYContact`、`TYMechanics`、`TYMultibody`、`TYDriveline3D`、`TYMechanics2D`
- **定位**：`ty-sysplorer-modeling-rules` 的领域附加技能
- **核心约束**：仅允许 TY 开头机械库组件
- **维度识别**：1D / 2D / 3D 驱动库选择；多体模型需 `TYMultibody.World`
- **工作流**：任务识别 → 组件映射 → 参数规则 → 最小可验回路 → 验证闭环
- **修复优先链**：TY 库边界 → world/reference → 结构连接 → 参数 → 初始化/约束 → 求解器 → 结果解读
- **交付要求**：子库边界、组件来源、验证变量、动画状态（多体模型）

### 4. ty-hydraulic-pneumatic-modeling — TY 液压气动建模

- **版本**：1.0.0
- **触发词**：`TYOilMedia`、`TYHydraulics`、`TYHydraulicComponents`、`TYThermalHydraulics`、`TYThermalHydraulicComponents`、`TYGasMedia`、`TYPneumatics`、`TYPneumaticComponents`、`TYThermals`
- **定位**：`ty-sysplorer-modeling-rules` 的领域附加技能
- **核心库**：
  - 液压：TYHydraulics / TYHydraulicComponents / TYThermalHydraulics / TYThermalHydraulicComponents
  - 气动：TYPneumatics / TYPneumaticComponents
  - 介质：TYOilMedia / TYGasMedia
- **特色规则**：
  - 介质选择是结构性决策，未确定介质前不得继续
  - 液压模型需执行容性-阻性拓扑检查（capacitor-resistive check）
  - 图面规则：键实例与键连线必须可见
  - 验证项：压力、流量、位移、阀状态、作动方向、边界完整性
- **修复优先链**：源/边界 → 库依赖 → 组件映射 → 参数 → 拓扑 → 容性阻性拓扑 → 介质 → 初始化 → 翻译 → 仿真 → 结果变量 → 图解标注

### 5. ty-nps-library-modeling — NPS 电气系统建模

- **版本**：1.0.0
- **触发词**：`NPSLibrary`（注意：仅 `Boost`、`Buck`、`DCDC` 等场景词不足以触发）
- **定位**：`ty-sysplorer-modeling-rules` 的领域附加技能
- **核心域**：电力电子、电机驱动、源网、故障保护、潮流
- **默认约束**：默认使用 NPSLibrary 内组件
- **建模原则**：先主功率路径再控制链路，按需添加 Ground/Reference/Powergui/Sensors
- **潮流任务**：需检查 LoadFlowBus、slack/PV/PQ 总线定义、Powergui 初始化
- **验证项**：功能正确性、趋势合理性、数值可接受性、参考/工程预期
- **修复优先链**：GUI/call_code 调用 → 接地/参考 → 连接完整性 → 接口兼容性 → Powergui/潮流 → 初始化 → 参数 → 翻译 → 仿真 → 结果解读

### 6. ty-thermofluid-modeling — TY 热流体系统建模

- **版本**：1.0.0
- **触发词**：`TYMedia`、`TYThermoFluidSys`、`TYAirTreatmentAndVentilation`
- **定位**：`ty-sysplorer-modeling-rules` 的领域附加技能
- **核心域**：热流体、换热、空气处理、通风、HVAC、环境控制
- **建模策略**：
  - 先选定介质和相态假设再定拓扑
  - 先构建最小能量/流体路径再添加控制、传感器和次级回路
  - 开环优先验证再闭环收敛
- **验证项**：压力、温度、流量、湿度、焓、换热率、压缩机功率、COP 等
- **修复优先链**：介质选择 → 边界/参考 → 拓扑 → 参数 → 离散化/阻力组织 → 初始化 → 翻译 → 仿真 → 结果解读

### 7. ty-sysblock-diagram-modeling — Sysblock 框图建模

- **版本**：1.0.0
- **触发场景**：新建 Sysblock 框图模型、修复现有模型、参数整定或仿真验证
- **定位**：`ty-sysplorer-modeling-rules` 路由到 Sysblock 路径后的领域补充
- **强制规则**：
  - 仅通过 `call_code(mode="run_script")` 官方 API 构建和编辑
  - 禁止 `SetModelText`、手写 `.mo` 文本、`connect()` 方程
  - 使用 `ConnectPort` 连线，使用全路径组件名如 `SysplorerEmbeddedCoder.xxx.ComponentName`
  - 正确使用端口后缀：`.y`、`.u`、`.u1`、`.u2`
- **覆盖组件**：信号源、数学运算、连续/离散系统、逻辑运算、观测器
- **验证项**：稳态值、上升时间、超调量、稳定时间等控制指标

### 8. ty-sysblock-signal-modeling — Sysblock 信号与通信建模

- **版本**：1.0.0
- **触发场景**：Sysblock 信号处理或通信链路建模
- **定位**：`ty-sysplorer-modeling-rules` 路由到 Sysblock 路径后的领域补充
- **核心域**：
  - 信号处理：滤波、频谱验证、多速率处理、特征提取
  - 通信链路：基带链路、BER、QPSK/QAM、同步、DSSS
- **涉及库**：TYDSPSystem、TYCommunication、TYMixedSignal、SysplorerEmbeddedCoder
- **强制规则**：
  - 先加载 `SysplorerEmbeddedCoder`
  - 先分类任务再设计（滤波/频谱/多速率/特征提取/通信链路/BER/同步/混合信号）
  - 先构建最小可运行信号链再扩展
  - 提前定义可观测性：输出变量、频谱、BER、同步状态等
- **验证项**：频谱正确性、BER 达标、同步锁定、时序对齐

### 9. ty-sysblock-svdpi-codegen — Sysblock SV-DPI 代码生成

- **版本**：1.0.0
- **触发场景**：已有 codegen 目录的基础上生成/刷新/校验 SV-DPI 包装
- **触发词**：dpi.h、dpi.c、dpi_pkg.sv、dpi.sv、tb.sv、simulate.do、wave.do、motrace.json、ModelSim、Questa
- **核心闭环**：边界确认 → codegen 目录检查 → 运行生成器 → 元数据审查 → 测试点处理 → 可选仿真 → 交付
- **脚本驱动**：`scripts/render_svdpi.py`
- **边界**：仅接管已有 codegen 目录后的包装生成，不负责 Sysplorer 建模或 codegen 本体
- **生成产物**：dpi.h、dpi.c、dpi_pkg.sv、dpi.sv、tb.sv、_svdpi_metadata.json、simulate.do、wave.do

### 10. ty-design-opt-mpe-modeling — DesignOptMpe 参数设计与优化

- **版本**：1.0.0
- **触发场景**：通过 DesignOptMpe 做参数设计、MPE 参数估计、优化与标定脚本、`run_script` 实验循环
- **边界**：
  - 仅用于 DesignOptMpe 相关的参数设计/估计/优化任务
  - 不用作通用 ModelingPy API 查询（用 `get_api_document`）
  - 不用作纯 Modelica/Sysblock 建模（先走 `ty-sysplorer-modeling-rules`）
- **工具链**：`session_manager`（就绪检查）→ `call_code(mode="run_script")`（执行脚本）→ `resources_retrieval`（查 API 文档）→ `model_manager`/`check_model`/`translate_model`/`simulate_model`
- **关键规则**：
  - DesignOptMpe 不走主 `Help()` 命名空间，需在 `run_script` 中用 `import` + `ListFunctions()` / `help()` 查文档
  - 会话就绪优先；禁止 `ClearAll` / `ChangeDirectory`

---

## Skill 调用关系

```
ty-sysplorer-modeling-rules（总规则，所有建模任务的强制前置）
    ├── modelica-library-workflow（模型库开发流程附加）
    ├── ty-mechanical-modeling（机械领域附加）
    ├── ty-hydraulic-pneumatic-modeling（液压气动领域附加）
    ├── ty-nps-library-modeling（电气领域附加）
    ├── ty-thermofluid-modeling（热流体领域附加）
    ├── ty-sysblock-diagram-modeling（Sysblock 框图领域附加）
    ├── ty-sysblock-signal-modeling（Sysblock 信号领域附加）
    └── ty-sysblock-svdpi-codegen（SV-DPI 代码生成，需已有 codegen 目录）
ty-design-opt-mpe-modeling（参数设计优化，需先走 ty-sysplorer-modeling-rules 确认建模范式）
```

---

## Skill 目录结构概览

```
Skills/
├── ty-sysplorer-modeling-rules/      （总规则）
├── modelica-library-workflow/
├── ty-mechanical-modeling/
├── ty-hydraulic-pneumatic-modeling/
├── ty-nps-library-modeling/
├── ty-thermofluid-modeling/
├── ty-sysblock-diagram-modeling/
├── ty-sysblock-signal-modeling/
├── ty-sysblock-svdpi-codegen/
├── ty-design-opt-mpe-modeling/
├── Skills汇总.md                      （本文件）
└── Skill文件清单.md                   （文件规范要求）
```

每个 Skill 目录内通常包含：
- `SKILL.md` — 主定义文件
- `references/` — 参考文档
- `templates/` — 模板文件
- `scripts/` — 自动化脚本
- `workflows/` — 专用工作流定义
- `docs/` — 额外文档

---

## 安装说明

配置时需要**拷贝整个 skill 目录**，不能只拷贝 `SKILL.md`。

### OpenCode

**项目级安装**：
```
<your-project>/.opencode/skills/
```

**用户级安装**：
```
~/.config/opencode/skills/
```

### Codex

**项目级安装**：
```
your-project/.codex/skills/
```

**用户级安装**：
```
~/.codex/skills/        # Linux/macOS
%USERPROFILE%\.codex\skills\  # Windows
```

### Claude Code

**项目级安装**：
```
your-project/.claude/skills/
```

**用户级安装**：
```
~/.claude/skills/       # Linux/macOS
%USERPROFILE%\.claude\skills\  # Windows
```

---

## 建议

- 如果仅当前仓库使用，优先选择**项目级安装**
- 如果希望多个项目共用，选择**用户级安装**
- 所有建模任务必须先加载 `ty-sysplorer-modeling-rules`，该 skill 负责范式分流与流程管控


## 使用许可
本模型库版权由[Tongyuan]版权所有，未经许可，不得用于商业用途。

[Tongyuan]: <http://mohub.net/user/6/repo>

