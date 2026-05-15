# TY 液压 / 气动建模

本文件是 `SKILL.md` 的中文阅读版。本 skill 只能作为 `ty-sysplorer-modeling-rules` 之后的领域薄补丁使用；父级 skill 负责分流、七门闸、布局时机、修复闭环和交付证据。

## 最小读取

| 需求 | 读取 |
|---|---|
| 需求分类 | `references/requirement-map.md` |
| 库/组件映射 | `references/library-selection.md`, `references/component-map.md` |
| 介质选择 | `references/media-selection.md` |
| 参数 | `references/parameter-rules.md` |
| 验证 | `references/validation-rules.md` |
| 容阻拓扑 | 使用 `TYHydraulics` / `TYHydraulicComponents`，或检查/翻译/仿真症状指向流体容阻不匹配时读取 `references/capacitor-resistive-check.md` |
| 修复 | `references/error-repair-playbook.md`，再读 `references/common-errors.md` |
| 验收 | `references/acceptance-checklist.md`, `references/output-contract.md` |
| 图解专项 | 任务包含建图或修图时读取 `references/diagram-layout-rules.md` |
| 手册查询 | 仅在精简参考不足时读取 `references/manual-index.md` |

## 专项流程

- 从场景/表格/CSV 新建模型：`workflows/build-from-scenario.md`
- 现有模型或图解修复：`workflows/repair-existing-model.md`
- 官方或企业样例验证：`workflows/verify-example.md`

## 领域增量

- 先判断任务类型：新建、修复、样例验证、结果复核或仅指导。
- 建模前先选定流体家族：液压、热液压、气动、气体介质或热支撑。
- 介质选择属于结构性决策；压力、气体或温度行为重要时，不得在介质未知或错误的情况下继续。
- 液压/气动模型需验证压力、流量、位移、阀状态、执行器方向和边界/参考完整性。
- 使用 `TYHydraulics` 或 `TYHydraulicComponents` 的液压模型，在长仿真前，以及阀、泵、管路、容腔、容积开关等拓扑修复后，纳入容阻拓扑检查。
- 热液压模型需验证温度响应、热端口和热边界假设。
- 预期动作下零流量、非物理压力、位移反向、NaN/发散、温度无响应都视为验证失败。
- 图解任务中关键实例和关键连线必须可见、可审阅；布局时机仍由父级 Gate 6 控制。

## 修复优先级

优先沿最短阻塞链排查：

`source/boundary -> library dependency -> component mapping -> parameters -> topology -> capacitor/resistive topology -> medium -> initialization -> translation -> simulation -> result variables -> diagram annotations`

修复后回到失败的父级 Step/Gate；若拓扑、参数或图解语义变化，重跑受影响父级链路。

## 交付增量

在父级交付证据基础上补充：

- 实际使用的 TY 库、模型名/路径、拓扑摘要、介质、参数假设和未确认项。
- 使用 `TYHydraulics` / `TYHydraulicComponents` 或修复路径涉及容阻问题时，说明容阻检查状态。
- 已验证变量，以及通过/失败/无参考的判断。
- 对建模或图解修复任务，说明图面可读性。
