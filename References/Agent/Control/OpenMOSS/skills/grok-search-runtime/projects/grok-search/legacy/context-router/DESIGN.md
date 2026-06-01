# 上下文路由与技能化设计文档（LEGACY）

> 已并入 grok-search；本文件仅作历史参考。

## 1. 背景与目标

多轮对话 + 多工具/多模型并发场景下，必须解决：

- **上下文串台**（不同任务互相污染）
- **上下文过长**（成本飙升/幻觉增加）
- **跨重启丢失**（会话体验不稳定）
- **模型调用方式不统一**（4.2 优先、失败降级 4.1 等策略难以复用）

目标：

1. 提供**可持久化的上下文路由能力**（thread + task）。
2. 提供**可控的上下文裁剪策略**（消息上限 + token 预算 + 可选摘要）。
3. 封装成**OpenClaw skill**，方便模型/工具调用。
4. 与 **grok-4.20-beta / grok-4.1-thinking** 的调用策略可复用。

非目标：

- 不实现完整检索系统（仅提供“要求模型搜索”的提示词模板）。
- 不强绑定特定数据库（SQLite 默认，允许替换）。

---

## 2. 总体架构

```
┌──────────────────────────────────────────┐
│  上层编排（Agent / Tool Router）         │
│  - 选择模型（4.2 优先、失败降级 4.1）     │
│  - 决定是否携带上下文（auto/stateless）  │
└──────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│ Context Router Skill                      │
│ - route() 生成 task_id + 是否带上下文     │
│ - build_context_messages() 组装消息       │
│ - record_turn() 持久化一轮对话            │
│ - prune_expired() 清理过期上下文          │
└──────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│ Context Store (SQLite 默认)               │
│ - contexts / thread_state                 │
└──────────────────────────────────────────┘
```

---

## 3. 关键设计点

### 3.1 路由键

- **thread_id**：会话维度（用户/群组/会话）
- **task_id**：任务维度（同一会话内可并行多个任务）
- **caller_id**：调用方标识（模型/工具名，保存在 meta 中）

### 3.2 上下文策略

- `stateless`：不带上下文
- `auto`：命中续谈词 / need_context_hint 时带
- `always`：总带

### 3.3 续谈判定

默认关键词：继续/刚才/上次/这个/那个/that/this/continue…
可通过 `ContextConfig.continuation_patterns` 扩展。

### 3.4 上下文裁剪

- **max_messages**：保留最近 N 条
- **max_context_tokens**：总 token 预算
- **summary_trigger_tokens**：超过阈值触发摘要
- **summarizer**：可选，用模型压缩旧消息

### 3.5 持久化

默认 SQLite：

```
contexts(
  thread_id,
  task_id,
  messages_json,
  summary,
  meta_json,
  created_at,
  updated_at
)
thread_state(
  thread_id,
  last_task_id,
  updated_at
)
```

### 3.6 模型调用策略

- **默认 4.20-beta**
- **错误/超额/超时/不合格** → 自动降级 4.1-thinking
- “不合格”判定：sources 为空或无 URL/时间/quote

---

## 4. Skill 设计（拟）

### 4.1 方法清单

- `context.route(thread_id, user_text, task_id?, mode?, need_context_hint?)`
- `context.build(snapshot)`
- `context.record(thread_id, task_id, user_text, assistant_text, meta?)`
- `context.get(thread_id, task_id)`
- `context.prune(ttl_seconds)`

### 4.2 返回结构

```json
{
  "thread_id": "...",
  "task_id": "...",
  "include_context": true,
  "reason": "reuse_last_task",
  "snapshot": {
    "summary": "...",
    "messages": [...]
  }
}
```

---

## 5. 安全与治理

- 不保存原始敏感信息（建议仅保存“结论/证据/摘要”）
- 设置 TTL 清理过期上下文
- API Key 不落文档明文（通过 env 管理）

---

## 6. 配置与环境变量（建议）

- `GAPI_CUSTOM_BASE_URL`：API Base URL
- `GAPI_CUSTOM_API_KEY`：API Key
- `CONTEXT_DB_PATH`：SQLite 路径（默认 ./data/context.db）

---

## 7. 可扩展方向

- Redis/Postgres 存储适配
- 更精确的 tokenizer
- 多模型摘要器路由（4.1 thinking 用于压缩）
- 细粒度审计日志

---

## 8. 里程碑

1. 现有 router + SQLite（已实现）
2. Skill 封装（下一步）
3. 文档与示例（下一步）
