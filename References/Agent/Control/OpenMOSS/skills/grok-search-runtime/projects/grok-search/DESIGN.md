# grok-search — 设计文档

## 1. 目标

- 对外统一命名为 **grok-search**；上下文回顾仅作为**内部模块能力**（不单独对外）
- 使用 **grok-4.20-beta** 进行“模型自带检索”的回答生成
- 失败/限流/不合格时自动降级 **grok-4.1-thinking**
- 可选上下文回顾（内部模块 `tools/grok_search/context.py`）以支持追问与续聊
- **提示词只写“搜索并带来源”**，不提内部检索

## 2. 调用流程（4.2 优先，失败降级 4.1）

1. **上下文回顾模块** `route()` 生成 `task_id` 与是否带上下文
2. **上下文回顾模块** `build()` 生成历史消息
3. 调用 **grok-4.20-beta**
4. 失败判定触发降级（见下）
5. 调用 **grok-4.1-thinking**
6. **上下文回顾模块** `record()` 写入 user/assistant + meta

## 3. 统一提示词（System）

```
你必须主动搜索网络并返回证据。
要求：
1) 至少给出 2 条来源（含 URL、发布时间、原文摘录）
2) 不得编造来源；找不到就写“未找到”
3) 先列证据，再写结论
输出 JSON：
{
  "sources":[{"title":"","url":"","published_at":"","quote":""}],
  "claims":[{"statement":"","source_index":[0]}],
  "answer":"……",
  "unknowns":["..."],
  "confidence":0-1
}
```

> 请求参数建议加 `stream:false`，确保一次性返回 JSON。

## 4. 失败判定 / 降级触发

- HTTP 非 200 / 超时 / 429
- `sources` 为空或少于 2 条
- 任一来源缺 `url / published_at / quote`
- `answer` 为空
- 明确声明“无法搜索/未找到来源”且无可用证据

## 5. 输出结构（统一 JSON）

```json
{
  "sources":[{"title":"","url":"","published_at":"","quote":""}],
  "claims":[{"statement":"","source_index":[0]}],
  "answer":"…",
  "unknowns":["…"],
  "confidence":0-1
}
```

## 6. 上下文策略（内部回顾模块）

- `stateless`：不带上下文
- `auto`：命中续谈词才带（推荐默认）
- `always`：总带上下文（追问场景）

## 7. 配置与密钥

### 7.1 环境变量

- **首选**：
  - `GROK_BASE_URL`
  - `GROK_API_KEY`
- **兼容旧变量（用户当前配置）**：
  - `GAPI_CUSTOM_BASE_URL`
  - `GAPI_CUSTOM_API_KEY`
- **来源说明**：当前环境以 `.env` 中 `GAPI_CUSTOM_BASE_URL / GAPI_CUSTOM_API_KEY` 作为 Grok 的 base/key（等同于 `GROK_*`）。

### 7.2 macOS Keychain

- Service：`openclaw-grok`
- Accounts：`base-url`, `api-key`, `model`

## 8. 端点与请求格式

- 使用 OpenAI 兼容接口：`POST /v1/chat/completions`
- 关键字段：`model`, `messages`, `stream:false`, `temperature`

## 9. 元信息记录（内部回顾模块）

- `model`, `fallback_reason`, `latency_ms`
- 仅存 **结论 + 引用**，避免长文
