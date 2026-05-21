---
title: 知识库对话
description: 多轮 KB 对话，含检索与结构化回答。
keywords: Agently, 案例研究, KB, RAG, dialog, session, retrieval
---

# 知识库对话

> 语言：[English](../../en/case-studies/kb-dialog.md) · **中文**

## 问题

用户用自然语言对一个文档集（产品文档、政策、内部 wiki）提问。每轮：

1. 检索相关段落。
2. 仅用这些段落回答。
3. 引用来源。
4. 跨轮维持对话上下文。

## 形态

```text
用户问题
   │
   ▼
从 KB 检索 top-K        ◄── 经 embedding agent + 向量库
   │
   ▼
Agent.input(question).info({"sources": chunks}, always=False).output({...})
   │
   ▼
结构化回答 + 引用来源
   │
   ▼
追加到 session 历史
```

## 走读

```python
from agently import Agently

# embedding agent —— 小 / 快模型，仅向量化
embedding_agent = Agently.create_agent().set_settings("OpenAICompatible", {
    "base_url": "...",
    "api_key": "...",
    "model": "${ENV.EMBEDDING_MODEL}",
})

# 回答 agent —— 推理模型
agent = (
    Agently.create_agent()
    .role(
        "仅用提供的 sources 回答。如果 sources 没覆盖问题，明确说明。",
        always=True,
    )
)
agent.activate_session(session_id="kb-dialog")  # 多轮

from agently.integrations.chromadb import ChromaCollection
collection = ChromaCollection(collection_name="docs", embedding_agent=embedding_agent)


def ask(user_question: str):
    chunks = collection.query(user_question, top_n=5)
    return (
        agent
        .info({"sources": chunks}, always=False)
        .input(user_question)
        .output({
            "answer": (str, "直接回答", True),
            "citations": [
                {
                    "source_id": (str, "来自提供 sources 的 id", True),
                    "quote": (str, "短的逐字引用", True),
                }
            ],
            "uncertain": (bool, "sources 未完全回答时为 True", True),
        })
        .start()
    )


# 循环
while True:
    user_text = input("> ")
    if not user_text.strip():
        break
    result = ask(user_text)
    print(result["answer"])
    for c in result["citations"]:
        print(f"  [{c['source_id']}] {c['quote']}")
    if result["uncertain"]:
        print("  （sources 未完全覆盖该问题）")
```

## 为什么这么选

- **两个 agent，每个一个职责** —— embedding 与回答有不同模型需求（embedding 用便宜小模型；回答用推理模型）。不要跨职责共享 agent。
- **`info(sources, always=False)`** —— sources 每轮都变；不应在 agent 持久 prompt 里累积。`always=False` 让它单次。
- **`role(always=True)` 强制 grounding** —— 「仅用提供 sources 回答」每轮都要。不要每次重复在 `instruct`。
- **结构化输出含 `citations`** —— 引用是程序读的。放进 schema（而非让模型在散文里格式化）让它可靠可解析。
- **`uncertain: bool`** —— KB 系统中显式「我不知道」是关键。强制为必填字段（第三槽 `True`，ensure 标记）让模型不能在缝隙里偷偷幻觉。见 [Schema as Prompt](../requests/schema-as-prompt.md)。
- **session 多轮** —— 用户可问跟进（「下版本呢？」「显示限制」）不必重复上下文。`activate_session()` 启用 session windowing。

## 变体

### 按用户过滤检索

KB 多 tenant / 多用户时，查询时限定：

```python
chunks = collection.query(user_question, top_n=5, where={"tenant_id": current_user.tenant_id})
```

### 校验引用是否在检索集中

加 `.validate(...)` 确保引用的 `source_id` 出现在检索 chunks 里：

```python
def cite_check(result, ctx):
    valid_ids = {c["id"] for c in ctx.input.get("sources", [])}
    bad = [c for c in result["citations"] if c["source_id"] not in valid_ids]
    if bad:
        return {"ok": False, "reason": "fabricated source_id", "validator_name": "citation"}
    return True
```

见 [输出控制](../requests/output-control.md)。

### 流式回答

用户交互式阅读时流 `answer`：

```python
gen = agent.info({"sources": chunks}, always=False).input(user_text).output({...}).get_generator(type="instant")
for item in gen:
    if item.path == "answer" and item.delta:
        print(item.delta, end="", flush=True)
```

## 交叉链接

- [知识库](../knowledge/knowledge-base.md) —— embedding + Chroma
- [会话记忆](../requests/session-memory.md) —— 多轮上下文
- [输出控制](../requests/output-control.md) —— 校验引用
- [Context Engineering](../requests/context-engineering.md) —— `info` 单次 vs 持久
