# 验证样例 / Verify Example

## 默认读取集

- 必读：`references/validation-rules.md`
- 按需：`references/common-errors.md`，仅在样例结果异常时读取
- 若任务转为“基于样例重建模型”，停止当前路线并切到 `workflows/build-from-scenario.md`

## 适用场景

- 用户要求运行 TY 官方样例或企业样例并验证关键结果。
- 用户要求用样例做对照、学习参数习惯或复核结果，不要求直接把样例改壳成交付模型。

## 最短闭环

1. 先确认任务是“验证样例”还是“基于样例重建模型”；若是后者，转到 `workflows/build-from-scenario.md`。
2. 样例只可用于参考拓扑、参数习惯、观测变量和排障路径，不得通过 `extends`、wrapper 或直接改名交付。
3. 按父级闭环跑完整验证，并用 `references/validation-rules.md` 解释关键变量。
4. 若结果异常，按 `references/common-errors.md` 回溯结构、参数和工况，不要直接归因于求解器。

## 输出重点

- 说明样例用途、关键变量与对照结论。
- 说明样例中哪些内容可复用，哪些内容不可直接交付。
- 说明若要迁移到用户场景，下一步需要重建或替换的部分。
