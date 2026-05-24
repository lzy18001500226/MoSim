---
title: 知识库
description: Embedding、检索，以及把检索结果挂进请求。
keywords: Agently, 知识库, KB, retrieval, embeddings, Chroma
---

# 知识库

> 语言：[English](../../en/knowledge/knowledge-base.md) · **中文**

Agently 术语里知识库是：向量库 + 把文本变向量的 embedding agent + 返回相关 chunk 的查询路径。Agently 内置 Chroma 适配器作为参考实现；它的包路径仍是 `agently.integrations.chromadb`。

## 何时用 KB

| 你想 … | KB？ |
|---|---|
| 总在 prompt 里带一小份固定事实 | 不 —— 用 `info(always=True)`（见 [Context Engineering](../requests/context-engineering.md)） |
| 每问从大语料检索相关片段 | 是 |
| 跨 flow execution 缓存结构化数据 | 不 —— 用 `runtime_resources` 或外部存储 |
| 记住对话历史 | 不 —— 那是 [Session](../requests/session-memory.md) |

## 参考栈

```text
文档 → embedding agent → Chroma 集合
                            │
                       （向量索引）
                            │
问题 → embedding agent → 相似度搜索 → 前 K 片段
                                          │
                                          ▼
                                 agent.info(retrieved=...)
                                          │
                                          ▼
                                        请求
```

## 最小用法

```python
from agently import Agently
from agently.integrations.chromadb import ChromaCollection

embedding_agent = Agently.create_agent().set_settings("OpenAICompatible", {
    "base_url": "...",
    "api_key": "...",
    "model": "${ENV.EMBEDDING_MODEL}",
})

collection = ChromaCollection(collection_name="docs", embedding_agent=embedding_agent)

# 索引
collection.add([
    {"id": "doc-1", "document": "Agently 有三个协议层模型插件……"},
    {"id": "doc-2", "document": "TriggerFlow lifecycle 三态……"},
])

# 查询
chunks = collection.query("有几个模型插件？", top_n=3)

# 用进请求
agent = Agently.create_agent()
result = (
    agent
    .info({"retrieved": chunks}, always=False)
    .input("用检索到的上下文回答。")
    .start()
)
```

这组 API 对应 `agently.integrations.chromadb.ChromaCollection`，仓库中的 `examples/chromadb/` 也使用同一套数据形态。

## 模式

### 单次请求检索（最常见）

只检索本问相关，挂在单次请求：

```python
chunks = collection.query(user_question, top_n=5)
agent.info({"retrieved": chunks}, always=False).input(user_question).start()
```

`always=False` 保证检索片段不进 agent 持久 prompt —— 仅本次。

### 检索集过滤

多数向量库支持按 metadata 过滤。用它限定 user / tenant / 文档类型：

```python
chunks = collection.query(
    user_question,
    top_n=5,
    where={"tenant_id": current_user.tenant_id},
)
```

### 后置 ingest

agent 输出应当成为未来上下文（如自更新 KB）时，请求后加一步把回答 ingest 回集合：

```python
result = agent.input(user_question).start()
collection.add([{
    "id": new_id(),
    "document": result["answer"],
    "metadata": {"source": "agent_answer"},
}])
```

慎用 —— 不审核就自动 ingest 模型输出是 KB 自我污染的方式。

### TriggerFlow 内

检索步骤就是另一个 chunk：

```python
async def retrieve(data):
    chunks = collection.query(data.input, top_n=5)
    return {"question": data.input, "chunks": chunks}

async def answer(data):
    payload = data.input
    return await agent.info({"retrieved": payload["chunks"]}, always=False).input(payload["question"]).async_start()

flow.to(retrieve).to(answer)
```

如果是 live client，作为 runtime resource 注入：

```python
execution = flow.create_execution(runtime_resources={"collection": collection})

async def retrieve(data):
    coll = data.require_resource("collection")
    return {"question": data.input, "chunks": coll.query(data.input, top_n=5)}
```

## 不在范围

- 完整向量数据库。Chroma 是参考；Agently 不打包一个。
- 存储 / 持久化策略。自带 Chroma 后端（文件、Postgres、hosted Chroma Cloud）。
- 重排序。需要时在 `query()` 与请求之间加。
- embedding 模型选型。按你领域选 —— embedding agent 就是配了 embedding 模型的 Agently agent。

## 另见

- [Context Engineering](../requests/context-engineering.md) —— 何时该用 KB
- [会话记忆](../requests/session-memory.md) —— 不同问题用不同工具
- [TriggerFlow State 与 Resources](../triggerflow/state-and-resources.md) —— flow 中 live Chroma client 该放哪
