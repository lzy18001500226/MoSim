# 测试策略（真正的“任务+测试”驱动）

> 你的定义：构建测试用例的同时构建任务；对交付任务的 **Agently 输出结果** 做可用性测试；测试通过才表示任务交付没问题。

这个 skill 按两级测试组织（让回归可稳定运行）：

---

## Level 1：离线可回归（默认必须）

目标：不依赖外网、不依赖真实 API key，仍然能验证：
- `.output(schema)` 的结构化输出可被解析并满足 `ensure_keys`
- `instant/streaming_parse` 事件流可用（路径/增量/完成标记）
- 服务化 SSE 输出格式正确（如果实现了 `/sse`）

做法：在测试里启一个 **OpenAI-compatible stub（ASGI app）**，并通过 `OpenAICompatible.client_options.transport = httpx.ASGITransport(app=stub)` 把 Agently 的请求路由到本地 stub。

优点：
- 测试稳定、速度快、可在 CI 跑
- 能回归 streaming/结构化解析链路（是 Agently 的核心价值）

---

## Level 2：真模型集成（可选）

目标：用真实模型 provider 验证“实际质量/可用性”（而不是只验证链路）。

建议：
- 通过环境变量开关启用，例如 `AGENTLY_INTEGRATION=1`
- 没有 key 时自动 skip（不要让 CI 失败）
- 重点验收：
  - 生成质量（例如 `reply` 不为空、`sources` 有效）
  - 工具调用效果（Search/Browse/MCP）
  - 真实网络错误时的降级策略是否生效

---

## 典型断言（建议写进 tests）

结构化输出（必须）：
- `result` 是 `dict`
- `ensure_keys` 覆盖的 key 都存在（例如 `sources[*].url`）
- 字段类型正确（`reply` 为 str，`sources` 为 list[dict]）

Streaming（必须）：
- `instant` 里至少出现 1 个预期字段 path（例如 `reply`/`sources[0].url`）
- `StreamingData.is_complete` 的 key 最终出现（字段完成）

SSE（可选，但推荐）：
- Response content-type 是 `text/event-stream`
- Body 中逐条出现 `data: {...}\n\n`
- JSON `type/data` 符合约定
- **回归护栏**：每条 `data:` 行都必须能 `json.loads` 成功（禁止输出 Python repr 或非 JSON）

---

## Streaming UX 回归守护（通用，强烈建议）

当你做“打字机式快速反馈”时，最容易回归的不是模型质量，而是：
1) **把事件对象/字典 repr 当成正文**（UI 先出现一坨 `{'title': ...}` 或 `path='...' wildcard_path=...`）
2) **重复生成同一段/同一项**（流式 + fallback 又跑一遍，导致两版文本）
3) **UI 重复渲染**（同一 index 既显示 delta 卡片又显示 final 卡片）

建议在离线回归里加“不过拟合”的守护断言：

- 若存在 `item_delta`/`paragraph_delta` 这类事件：
  - `delta` 必须是纯文本（str）
  - `delta` 不得包含 repr 痕迹（例如 `wildcard_path=`, `full_data=`, `path=`, `delta=`）
  - `delta` 不得以 `{` 开头且包含 `"'title':"`（Python dict repr 的典型特征）

- 若存在 `item_final`/`paragraph` 这类最终事件：
  - 必须携带稳定的 `index`（或唯一 ID）
  - 同一 `index` 的 final 不应重复出现（最多 1 次）

> 以上断言不要求“必须产生 delta”，仅在“事件存在时”校验结构与纯净性，避免测试变脆。
