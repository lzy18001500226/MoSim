# 修复已有模型 / Repair Existing Model

## 默认读取集

- 必读：`references/common-errors.md`
- 按需：`references/parameter-rules.md`，仅在确认是参数问题且组件名单稳定后读取
- 按需：`references/validation-rules.md`，仅在修复后 `simulate` 成功、准备解释结果时读取
- 默认不要先读全部 reference，只围绕当前失败阶段定位问题

## 适用场景

- 已有 TY 机械模型出现 `check`、`translate`、`simulate` 或结果异常问题。
- 用户需要修复连线、参数、初值、约束或组件选择问题。

## 最短闭环

1. 先识别失败阶段，再读取 `references/common-errors.md` 选择对应排查顺序。
2. 保持 TY 库边界不变，优先做最小修复，不大范围重写无关结构。
3. 结构问题先回到 `check`；翻译问题先查状态选择、初值和约束；仿真问题先查初值、约束和参数数量级。
4. 仅在确认是参数问题时，重新通过 Sysplorer 参数查询接口核对真实参数名。
5. 修复后从最早失败阶段重新推进到 `result verify`，不得停在中间阶段。

## 输出重点

- 说明故障阶段、根因判断和最小修复动作。
- 说明修复后重新执行成功的阶段。
- 说明仍未闭环的问题和下一步建议。
