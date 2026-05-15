# 从场景新建模型 / Build From Scenario

## 默认读取集

- 必读：`references/requirement-map.md`
- 必读：`references/component-map.md`
- 按需：`templates/scenarios/user-input-minimum-form.md`，用户输入不足、目标过宽或缺少运动维度/驱动/约束/结果变量时读取
- 按需：`references/parameter-rules.md`，仅在组件名单稳定、准备赋值前读取
- 按需：`references/validation-rules.md`，仅在 `simulate` 成功后读取
- 按需：`templates/scenarios/mechanical-system-min-loop.example.json`，仅在用户输入过 sparse 时读取

## 适用场景

- 用户要求基于 TY 商业机械库从零搭建机械系统、传动系统、接触系统、平面机构或多体模型。
- 用户已经给出目标机构、工况和关键结果，希望直接进入自动建模闭环。

## 最短闭环

1. 先抽取最小输入：机械系统类型、运动维度、目标机构、驱动方式、约束或连接关系、关注结果。
2. 若任一必须字段缺失，读取 `templates/scenarios/user-input-minimum-form.md`，只追问阻塞建模的字段；可默认假设字段必须记录来源和风险。
3. 先读取 `references/requirement-map.md` 判断任务类型，再读取 `references/component-map.md` 的“需求到 TY 子库快速分流表”收敛 TY 子库、首选建模路径和首轮最小闭环。
4. 若快速分流表无法命中，先输出分流依据和不确定点，再补齐用户输入，不得直接自由猜测组件。
5. 先搭最小可检查闭环，不预先加入非必要损耗、柔性体、接触细节和扩展工况。
6. 对最终候选组件集中查询真实参数名，再按 `references/parameter-rules.md` 的顺序赋值。
7. 按父级闭环推进；若为 3D、多体或空间机构任务，显式检查 `TYMultibody.World` 或等价世界组件。
8. 若最小闭环可运行但运动趋势、动画判断、KPI 或用户目标未达成，回到父级优化循环。

## 输出重点

- 说明采用的 TY 子库、核心组件和最小闭环结构。
- 说明用户输入最小表单中的已知字段、默认假设字段和仍缺失字段。
- 说明快速分流表命中的用户说法、推荐子库、建模路径和首轮最小闭环。
- 说明关键参数来源、已执行动作和关键变量验证结论。
- 说明仍需补充的工况、参数或扩展结构。
