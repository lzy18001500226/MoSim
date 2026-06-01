# 使用文档：上下文路由工具 & 模型调用流程（LEGACY）

> 已并入 grok-search；本文件仅作历史参考。

## 1. 目录结构

```
projects/context-router-skill/
  ├─ DESIGN.md
  └─ USAGE.md

tools/context_router/
  ├─ context_router.py
  └─ README.md

skills/context-router/
  ├─ SKILL.md
  ├─ scripts/context_router_cli.py
  └─ examples/minimal_cli_flow.py
```

---

## 2. 环境变量（不要在文档中写明 Key）

建议在 `.env` 设置：

```
GAPI_CUSTOM_BASE_URL=https://api.example.com/
GAPI_CUSTOM_API_KEY=***
CONTEXT_DB_PATH=./data/context.db
```

> 注意：子进程不会自动继承 `.env`，需要显式加载。

---

## 3. Skill/CLI 使用（推荐）

**CLI 输出为 JSON，适合工具链消费。**

**路由：**

```bash
/usr/bin/python3 ~/.openclaw/workspace/skills/context-router/scripts/context_router_cli.py route \
  --thread-id "user:123" \
  --user-text "继续这个问题" \
  --mode auto
```

**组装上下文：**

```bash
/usr/bin/python3 ~/.openclaw/workspace/skills/context-router/scripts/context_router_cli.py build \
  --thread-id "user:123" \
  --task-id "<task_id_from_route>"
```

**记录一轮：**

```bash
/usr/bin/python3 ~/.openclaw/workspace/skills/context-router/scripts/context_router_cli.py record \
  --thread-id "user:123" \
  --task-id "<task_id>" \
  --user-text "继续这个问题" \
  --assistant-text "...模型回答..."
```

**清理过期：**

```bash
/usr/bin/python3 ~/.openclaw/workspace/skills/context-router/scripts/context_router_cli.py prune --ttl-seconds 86400
```

### 3.1 最小可运行示例（CLI 全流程）

```bash
/usr/bin/python3 ~/.openclaw/workspace/skills/context-router/examples/minimal_cli_flow.py
```

> 脚本会使用临时 DB 路径，依次执行 route → build → record → get → prune，并打印每步 JSON。

### 3.2 测试与验收

详见 `projects/context-router-skill/TESTING.md`（最小 CLI flow + TTL 回归）。

---

## 4. 基础用法（Python）

```python
from tools.context_router.context_router import ContextStore, ContextRouter, ContextConfig

store = ContextStore("./data/context.db")
router = ContextRouter(store, ContextConfig(max_messages=8, max_context_tokens=4000))

# 1) 路由
decision = router.route(
    thread_id="user:123",
    user_text="继续这个问题",
    mode="auto",  # stateless / auto / always
)

# 2) 组装上下文
messages = [
    {"role": "system", "content": "你必须搜索并返回来源…"},
    *router.build_context_messages(decision.snapshot),
    {"role": "user", "content": "继续这个问题"},
]

# 3) 调模型（伪代码）
resp = call_model("grok-4.20-beta", messages)
if is_failed(resp):
    resp = call_model("grok-4.1-thinking", messages)

# 4) 记录
router.record_turn(
    thread_id="user:123",
    task_id=decision.task_id,
    user_text="继续这个问题",
    assistant_text=resp.text,
    meta={"model": resp.model},
)
```

---

## 5. 上下文策略

- `stateless`：不带上下文（适合检索工具）
- `auto`：命中续谈词才带（推荐默认）
- `always`：总带上下文

建议：默认 `auto`，模型只给建议，**最终由代码裁决**。

---

## 6. 失败降级（4.2 -> 4.1）

**触发条件建议**：

- HTTP 非 200 / 超时 / 429
- sources 为空
- 任何 source 缺 url/时间/quote

---

## 7. 建议的系统提示词模板（要求“搜索+来源”）

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
  "answer":"…",
  "unknowns":["…"],
  "confidence":0-1
}
```

---

## 8. 上下文裁剪与摘要

- 超出阈值自动裁剪最旧消息
- 可注入 summarizer（建议用 grok-4.1-thinking）

```python
def summarizer(removed_messages, existing_summary):
    return "...压缩后的摘要..."

router = ContextRouter(store, summarizer=summarizer)
```

---

## 9. 多任务并发（task_id）

```python
# 新闻任务
router.route(thread_id, user_text, task_id="news:20260302", mode="always")
# 财报任务
router.route(thread_id, user_text, task_id="finance:tsla", mode="always")
```

---

## 10. 清理过期上下文

```python
store.prune_expired(ttl_seconds=24*3600)
```

---

## 11. 注意事项

- API 不返回会话句柄；上下文必须由服务端注入
- 不要保存大段网页/日志，建议保存“结论+证据”
- 需要跨重启保存时，必须用持久化存储（SQLite/Redis/Postgres）
