# Advanced Integrations（通用：MCP / ChatSession / Attachment / TriggerFlow Blueprint / streaming 运维）

覆盖能力点（来自 `capability-inventory.md`）：
- `CAP-MCP-USE` / `CAP-MCP-PATHING`
- `CAP-CHAT-HISTORY-*` / `CAP-CHAT-SESSION-*`（含可选扩展）
- `CAP-TF-BLUEPRINT` / `CAP-TF-SIDE-BRANCH`
- `CAP-ATTACHMENT`
- `CAP-STREAM-STREAMING-PARSE` / `CAP-STREAM-CANCEL-LOGS`（运维视角）

目标：把“高级能力”的坑与可复现用法总结成通用指南，避免 skill 只覆盖基础 happy-path。

---

## 1) MCP：如何保证 path 可复现

常见坑：
- 示例里写了 `agent.use_mcp("some/path")`，但真实项目/CI 环境下路径不同，导致运行失败。

通用建议：
- **把 MCP server 放进 repo**（例如 `mcp_servers/<name>/server.py`），并在代码里使用“相对 repo 根”的路径。
- 提供一个“路径解析函数”：
  - 优先从 env 读取（允许部署时覆盖）
  - 其次用 `Path(__file__).resolve()` 推导相对路径

回归建议：
- 在离线回归测试里至少验证“路径解析正确 + 能启动/握手”（不需要真实外部依赖）。

---

## 2) Chat History vs Chat Session（扩展能力）

### Chat History（基础，多轮上下文）
- 用 `set_chat_history/add_chat_history/reset_chat_history` 管理多轮对话上下文。
- 适合：轻量多轮、业务自己管理 history。

### Chat Session（可选扩展：持久化/记录关键输入输出）
提示：
- ChatSession 通常不是默认混入的扩展；如果你需要它，应该在项目里显式启用/声明依赖。

通用策略：
- 默认用 Chat History 保持最小依赖；
- 只有当你确实需要“会话 ID + 自动记录 + 取回”时才引入 ChatSession，并补齐：
  - 数据存储位置（文件/DB）
  - 隐私边界（哪些字段允许记录）
  - 回归测试（record_input_paths/record_output_paths 的行为稳定）

---

## 3) Attachment / 多模态（VLM）

通用原则：
- `.attachment(...)` 代表“非纯文本输入”，通常会触发底层 requester 使用 richer payload（例如 `rich_content=True`）。
- 多模态模型与文本模型的能力、价格、速率不同：建议拆分为专用 agent（VLM agent）。

回归策略：
- 离线回归不追求“看懂图像”，只验证：
  - attachment 能进入请求结构
  - response 结构化输出仍可解析

---

## 4) TriggerFlow Blueprint（复用 flow 结构）

适用：
- 你要把某个复杂 flow 作为“可复用资产”复用在多个任务里；
- 或者你希望把 flow 的结构保存下来用于审计/复盘/迁移。

通用建议：
- 把 blueprint 的 save/load 作为“构建时资产”（类似 prompt YAML），不要在每次请求时反复生成。
- 复用时仍要保证 runtime_data per-execution，不要让 blueprint 变成共享状态的入口。

---

## 5) streaming_parse vs instant（运维视角）

通用理解：
- 两者都用于“结构化字段增量”，差异多体现在：
  - path 表达方式（dot/slash/wildcard）
  - parser 的容错行为

建议：
- 用同一套回归断言覆盖它们的核心契约：
  - 字段最终完成（is_complete）
  - delta 不污染（无 repr）
  - SSE 通道只下发 envelope JSON（每条 `data:` 可 `json.loads`）

---

## 6) cancel_logs（减少噪音，但不要当成正确性依赖）

现象：
- 调试时日志很多（工具、httpx、parser），影响阅读与 UI。

建议：
- 把“日志控制”当运维开关（debug on/off、log level），不要把它作为业务逻辑的一部分。
- 对外输出（UI/SSE）必须来自你定义的事件协议，而不是来自内部日志。

