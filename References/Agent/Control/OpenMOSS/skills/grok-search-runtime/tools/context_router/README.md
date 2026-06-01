# grok-search 内部上下文回顾模块（原 context-router）

> 已并入 grok-search；主入口请使用 `projects/grok-search/scripts/grok_search.py`。

**目的**：在多轮对话、多工具/多模型并发时，自动路由上下文并持久化，避免串台与上下文过长。

> 本工具不依赖模型返回会话句柄；**上下文由服务端维护并注入**。

---

## 1. 解决什么问题
- 多轮对话：让“继续/刚才/上次”能接着聊
- 多工具并发：不同任务/不同模型不串台
- 上下文过长：自动裁剪 + 可选摘要
- 重启丢失：SQLite 持久化

---

## 2. 核心概念
- **thread_id**：会话维度（如 user/tenant/session）
- **task_id**：任务维度（同一线程内可有多个任务）
- **caller_id**：调用方标识（模型/工具/服务，可存入 meta）
- **mode**：上下文策略
  - `stateless`：不带上下文
  - `auto`：续谈词才带
  - `always`：总带
- **snapshot**：持久化上下文快照（summary + recent messages）

---

## 3. 运行流程（推荐）
1) **route()** → 决定 task_id + 是否带上下文
2) **build_context_messages()** → 组装 `summary + recent_messages`
3) 调用模型
4) **record_turn()** → 记录本轮对话
5) 可选：**prune_expired()** → 定期清理过期任务

### 3.1 最小可运行示例（CLI 全流程）
```bash
/usr/bin/python3 ~/.openclaw/workspace/skills/context-router/examples/minimal_cli_flow.py
```
> 使用临时 DB 路径，依次执行 route → build → record → get → prune。

### 3.2 测试与验收
详见 `projects/grok-search/legacy/context-router/TESTING.md`（最小 CLI flow + TTL 回归）。

---

## 4. 配置项（ContextConfig）
| 字段 | 默认值 | 说明 |
|---|---:|---|
| max_messages | 8 | 最近保留的消息条数 |
| max_context_tokens | 4000 | 上下文总 token 预算（近似估算） |
| summary_trigger_tokens | 3200 | 超过该值时触发摘要 |
| max_summary_tokens | 800 | 摘要最大长度 |
| ttl_seconds | 86400 | 过期时间（秒） |
| continuation_patterns | 内置 | 续谈词匹配（可扩展） |

---

## 5. 路由规则（auto 模式）
**优先级**：
1. 有显式 `task_id` → 直接使用
2. 无 `task_id`：
   - 命中续谈词 + 有最近任务 + 未过期 → 复用 `last_task_id`
   - 否则生成新 `task_id`

**是否带上下文**：
- `stateless` → false
- `always` → true
- `auto` → `need_context_hint` 或命中续谈词

> 续谈词默认包含：继续/刚才/上次/这个/那个/that/this/continue…

---

## 6. 上下文组装规则
- 如果有 summary：会插入一条 `system` 消息：
  `上下文摘要：...`
- 然后追加最近 messages（按历史顺序）

**消息结构**：
```json
{"role":"user|assistant|system","content":"...","ts":1700000000}
```

---

## 7. 上下文长度控制
- 超出 `max_messages` 或 `max_context_tokens` → 移除最旧消息
- 如果提供 `summarizer`，会将被移除部分压缩进 summary
- `estimate_tokens()` 为简易估算（字符/4），可替换

**建议策略**：
- 存 “结论/证据”，避免塞入完整网页或巨量日志
- 工具输出先裁剪，再写入 messages

---

## 8. 持久化（SQLite）
默认 WAL 模式，适合单机/轻量并发。

### 数据表
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

### 过期清理
```python
store.prune_expired(ttl_seconds=24*3600)
```

---

## 9. 摘要器（可选）
你可以注入一个 summarizer：
```python
def summarizer(removed_messages, existing_summary) -> str:
    # 这里可调用 grok-4.1-thinking 进行压缩
    return new_summary
```
当内容过长或有被移除消息时，会调用 summarizer。

---

## 10. API 索引
### ContextStore
- `get_context(thread_id, task_id) -> ContextSnapshot | None`
- `upsert_context(thread_id, task_id, messages, summary, meta)`
- `update_thread_state(thread_id, task_id)`
- `get_last_task(thread_id) -> (task_id, updated_at) | None`
- `prune_expired(ttl_seconds) -> int`

### ContextRouter
- `route(thread_id, user_text, task_id=None, mode='auto', need_context_hint=None) -> RouteDecision`
- `build_context_messages(snapshot) -> List[Message]`
- `record_turn(thread_id, task_id, user_text, assistant_text, meta=None)`

### 工具
- `estimate_tokens(text) -> int`

---

## 11. 使用示例
### 11.1 基础用法
```python
store = ContextStore("./data/context.db")
router = ContextRouter(store)

# 路由
decision = router.route(thread_id="user:123", user_text="继续这个问题")

# 组装消息
messages = [
  {"role": "system", "content": "你必须搜索并返回来源..."},
  *router.build_context_messages(decision.snapshot),
  {"role": "user", "content": "继续这个问题"}
]

# 模型返回后记录
router.record_turn("user:123", decision.task_id, "继续这个问题", "...模型回答...")
```

### 11.2 工具/模型并发（显式 task_id）
```python
# 任务 A
router.route(thread_id, user_text, task_id="news:20260302", mode="always")
# 任务 B
router.route(thread_id, user_text, task_id="finance:tsla", mode="always")
```

### 11.3 强制无上下文（适合检索工具）
```python
router.route(thread_id, user_text, mode="stateless")
```

### 11.4 摘要器接入
```python
router = ContextRouter(store, summarizer=my_summary_fn)
```

---

## 12. 最佳实践
- **强制 task_id**：跨工具并发时建议显式传 task_id
- **自动策略为主**：默认 auto，避免上下文滥用
- **避免大块原文**：只保留结论/证据/短摘要
- **定期清理**：设置 TTL 或定时 prune
- **落盘路径可配**：生产可切换 SQLite/Redis/Postgres

---

## 13. 限制说明
- token 估算为粗略近似（可替换）
- summarizer 未提供时不会自动生成摘要
- SQLite 适合单机；多实例建议上 Redis/Postgres

---

## 许可证
MIT（与项目无关，可按需调整）
