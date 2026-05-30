# Observability

建议按这个顺序读：

1. [概览](overview.md)：区分 Event Center、TriggerFlow runtime stream、DevTools 与 coding-agent 指引。
2. [Event Center](event-center.md)：框架级 observation event（观测事件）和兼容规则。
3. [DevTools](devtools.md)：ObservationBridge、EvaluationBridge 与 InteractiveWrapper。

observation event 只观察发生了什么。TriggerFlow 的 `emit` / `when` 改变 flow 控制流，TriggerFlow runtime stream 把 live 数据推给消费者。
