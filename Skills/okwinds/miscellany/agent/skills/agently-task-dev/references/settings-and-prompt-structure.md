# Settings & Prompt Structure（通用：把配置/Prompt 结构化成可复用资产）

覆盖能力点（来自 `capability-inventory.md`）：
- `CAP-SETTINGS-GLOBAL` / `CAP-SETTINGS-INSTANCE`
- `CAP-DEBUG-MAPPING` / `CAP-DEFAULT-SETTINGS` / `CAP-PLUGIN-MGR`（理解层）
- `CAP-AGENT-VS-REQUEST` / `CAP-PROMPT-SLOTS` / `CAP-QUICK-METHODS` / `CAP-MAPPINGS`
- `CAP-ORDER-MATTERS`（schema 稳定性技巧）

目标：让任务开发不依赖“临场记忆”，而是按一套可回归的结构组织 settings 与 prompt。

---

## 1) Settings：全局 vs 实例（不要互相打架）

### 全局设置：作为“默认值/基线”

```py
from agently import Agently

Agently.set_settings(
  "OpenAICompatible",
  {"base_url": "https://my-server/v1", "model": "my-model", "options": {"temperature": 0.2}},
)
```

适合放在全局的内容：
- provider 连接信息（base_url/model/auth 的形态）
- 默认 options（temperature、timeout、重试策略等）
- runtime 日志等级（如 httpx_log_level）

### 实例设置：作为“局部覆盖”

```py
agent = Agently.create_agent()
agent.set_settings("OpenAICompatible", {"options": {"temperature": 0.0}})
```

适合放实例的内容：
- 某个 agent 的差异配置（例如一个 agent 专门做“严格审稿”，temperature 更低）
- embedding agent vs chat agent 的差异配置（model_type/模型名不同）

---

## 2) debug 的通用原则（可观测性，但别把日志当产品输出）

建议：
- 开发/排障阶段开启 debug（便于看到模型请求、工具调用、TriggerFlow 日志）
- 交付服务时默认关闭 debug，并用结构化事件（SSE `type/data`）输出可观测信息

不要把：
- 事件对象 repr（`path=... wildcard_path=...`）
- dict repr（`{'title': ...}`）
直接下发给用户通道（UI/SSE）。这属于“日志污染”，应留在内部日志里。

---

## 3) `_default_settings.yaml` / 插件体系（理解层，不建议在项目里频繁替换）

能力面（概念层面）：
- PromptGenerator
- ResponseParser
- ModelRequester（如 OpenAICompatible）
- ToolManager

通用建议：
- 任务开发阶段优先用默认插件与默认 settings（更可迁移、更少兼容坑）
- 只有在明确需求（例如特殊协议/特殊工具管理）时才替换插件；并为替换后的行为补回归测试

---

## 4) Agent vs Request：什么时候用哪个

通用理解：
- `Agent`：更像“具备长期配置/工具/历史”的实体（适合多轮、可复用）
- `Request`：更像“一次调用的快照”（适合一次性调用或严格隔离）

建议：
- 需要 chat_history / tools / session 的：用 agent
- 需要把一次调用完全隔离（无历史）并可并发大量请求的：用 request 或为每次请求创建新 agent（但要注意性能）

---

## 5) Prompt slots：把 prompt 当“结构”，而不是拼字符串

常见 slot（概念层面）：
- system / developer
- info（结构化上下文）
- tools / action_results（工具与工具结果）
- instruct（规则/要求）
- examples（few-shot）
- input（用户输入）
- output（结构化 schema）
- options（温度/策略）
- chat_history
- attachment（多模态）

通用建议：
- 业务上下文尽量放 `info`（结构化、可审计）
- 输出约束放 `output(schema)` + `ensure_keys`
- 工具调用过程放 `action_results`（不要混到用户输出字段）

---

## 6) mappings：`${var}` 的工程化用法

原则：
- mappings 是“注入点”，不要让 prompt 隐式依赖全局变量
- 对可变信息（requirements、constraints、retrieval_results）用 `info({...})` 提供，然后在 instruct 中引用

避免：
- 把 environment（base_url、key、proxy）写进 prompt

---

## 7) schema 的顺序会影响稳定性（`CAP-ORDER-MATTERS`）

当你用 `.output(schema)` 做结构化输出时：
- 把“高优先级/必须完成”的字段放前面（例如 `reply`、`plan`、`urls`）
- 把“可选/补充”的字段放后面（例如 `extra`、`notes`）

理由（通用经验）：
- 模型生成结构时通常按字段顺序推进；顺序合理能显著降低缺字段概率。

