# 压力测试场景（Skill TDD）

> 用途：把“技能文档是否真的能让 Coding Agent 正确使用 Agently”变成可回归的测试用例。
>
> 说明：这些不是单元测试，而是 **压力场景（pressure scenarios）**。每个场景都故意叠加时间/约束/不完整信息等压力，观察没有 skill 时的常见失误（RED），再用 skill 修复（GREEN），最后不断堵漏洞（REFACTOR）。

---

## 评估通用标准（所有场景都适用）

1) 能力覆盖：回答/实现必须显式使用 Agently 的关键能力（见 `references/capability-inventory.md`）。
2) 可运行性：给出可执行的运行步骤（包含 env/依赖/入口文件）。
3) 可观测性：包含 streaming/runtimestream 的事件格式说明或示例输出。
4) 风险控制：避免顶层执行副作用（`import` 就跑）、避免无限循环、解释代理/网络依赖（proxy、API key）。

---

## 场景 A：多步工具调用 + 结构化输出 + 流式 UI（时间压力 + 网络约束）

**用户请求（压力输入）**
- “用 Agently 做一个多步任务：先 Search 找 3 个链接，再 Browse 抓正文，最后结构化总结（带 sources）。要能实时流式输出：用户能看到 answer token，同时 UI 还能拿到结构化字段的事件。现在就要，别写太复杂。”

**压力组合**
- 时间压力：要求快速可交付
- 网络/环境约束：Search 可能需要 proxy；Browse 可能失败
- 输出约束：既要 `delta`（用户体验）又要 `instant`（结构化事件）

**必须体现的能力点（最低要求）**
- `Agently.set_settings` / `agent.set_settings`（OpenAICompatible）
- `.output(schema)` + `ensure_keys`
- `Search` + `Browse` 组合（可以多阶段 Search→选择→并发 Browse→总结）
- streaming：`delta` + `instant`（或 `specific`）

**通过标准（PASS）**
- 给出一个最小可运行 demo（脚本或模块）
- 明确说明 env（proxy/keys）与失败退化策略（Search/Browse 失败如何处理）
- 给出 streaming 事件示例（至少说明每个 event 代表什么）

---

## 场景 B：TriggerFlow 编排 Auto Loop（复杂度压力 + 正确性压力）

**用户请求（压力输入）**
- “用 Agently 的 TriggerFlow 做一个 Auto Loop：plan → tool → plan → reply → memo → loop。每轮最多 5 步，避免死循环。要把过程写进 runtime stream（status/thinking/plan/tool/reply/memo），并提供一版交互 CLI（stdin 输入）。”

**压力组合**
- 复杂度压力：需要工作流、状态、循环、限步、memo
- 正确性压力：容易死循环、事件乱序、runtime_data 使用错误
- 可观测性压力：必须把过程事件化（runtime stream）

**必须体现的能力点（最低要求）**
- TriggerFlow：`to/when/emit/collect/runtime_data`
- runtime stream：`put_into_stream` + `stop_stream`
- streaming parse：对结构化 planning 的 `instant` 解析（按 `wildcard_path` 触发）
- step 上限与失败退化策略（工具失败→final）

**通过标准（PASS）**
- 给出清晰的 flow 拓扑（步骤图或条列都可）
- 明确哪些数据放 `runtime_data`，哪些放 chat_history/memo
- 提供可运行入口（CLI）

---

## 场景 C：把 TriggerFlow/Auto Loop 暴露成 SSE/WS 服务（交付压力 + 约束压力）

**用户请求（压力输入）**
- “把上面的 Auto Loop 变成一个 FastAPI 服务：`GET /sse?question=...` 返回 SSE，`WS /ws` 支持双工，`POST /ask` 返回一次性 reply。事件格式统一 `{\"type\": \"...\", \"data\": ...}`。要给 Dockerfile 和本地启动命令。”

**压力组合**
- 交付压力：必须有服务入口、接口定义、运行命令
- 约束压力：事件格式固定；需要可回归验证
- 工程压力：依赖管理、env 注入、SSE flush、WS 循环

**必须体现的能力点（最低要求）**
- FastAPI：SSE（StreamingResponse）+ WebSocket + POST
- TriggerFlow runtime stream 与服务端推送桥接
- config：`DEEPSEEK_API_KEY` / `SEARCH_PROXY` 之类 env（或等价）
- 事件封装：统一 `_emit(type, data)`，并处理异常事件

**通过标准（PASS）**
- 代码结构清晰（app/main.py, routes.py, flow.py, config.py, schemas.py）
- 文档包含本地运行与 Docker 运行
- SSE/WS 返回事件符合约定（type/data）

