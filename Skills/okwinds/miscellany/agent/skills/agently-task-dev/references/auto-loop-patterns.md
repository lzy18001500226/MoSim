# Auto Loop Patterns（通用：plan → tool → plan → final）

目标：提供一个可复用的“多步循环编排”骨架，用于 research agent / coding agent / 复杂任务自动化。

来源：
- `agently-exmaples/step_by_step/12-auto_loop.py`
- TriggerFlow 示例：`agently-exmaples/step_by_step/11-triggerflow-*`

---

## 1) 核心抽象：`next_action` 的统一协议

建议把“下一步动作”抽象为结构化 schema（而不是 free-form text），最小形态：

```json
{
  "type": "tool" | "final",
  "reply": "if final",
  "tool_using": { "tool_name": "...", "purpose": "...", "kwargs": { ... } }
}
```

原则：
- `type="tool"` 时，`tool_using` 必须存在；`reply` 可为空字符串。
- `type="final"` 时，`reply` 必须存在；`tool_using` 为 null/缺省。

---

## 2) 终止条件（必须，防无限循环）

通用 guardrails：
- `max_steps`：达到上限直接 `final`（并解释为何终止）。
- `done_plans`：记录每次 tool 的 purpose/result；当同一失败反复出现，强制转 `final` 或换策略。
- 明确退出信号：CLI 模式支持 `exit`；服务模式支持超时/取消。

---

## 3) 工具注册与“分阶段启用”

推荐的通用范式：
1) Stage 1：只允许 `search` 类工具 → 产出候选 URL
2) Stage 2：并发 `browse` → 拉内容
3) Stage 3：禁用工具 → 基于 sources 生成总结/结论

好处：
- 工具调用更可控
- 输出更可回归（减少模型“乱用工具”）

---

## 4) 状态管理：runtime_data vs 进程级缓存

通用规则：
- per-request 状态：放 `runtime_data`（question/step/memo/done_plans 等）
- 跨请求复用资源（KB/连接池/索引）：放进程级缓存（模块级变量/外层闭包），避免每回合重建

---

## 5) UI/日志：把过程事件化（而不是 print）

当你需要把 auto loop 变成 Web/SSE 服务：
- 用 `status`、`item_start/item_delta/item_final` 事件输出过程
- 避免把 Python 对象 `repr` 直接下发给客户端
- SSE 适配层要做 envelope 收敛（只允许 JSON）

参考：
- `references/streaming-ux-playbook.md`
- `references/testing-strategy.md`（SSE 回归护栏）

---

## 6) 回归测试建议（不过拟合）

离线 stub 下只验“链路正确/协议正确/可终止”：
- 在 `max_steps` 下可稳定终止
- 若产生 `tool` 动作：`tool_name` 必须属于允许列表
- 若产生 `final` 动作：`reply` 非空
- 若有 SSE：每条 `data:` 必须可 `json.loads`

