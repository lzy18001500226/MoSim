---
title: Knowledge Base
description: Embeddings, retrieval, and feeding retrieved context into a request.
keywords: Agently, knowledge base, KB, retrieval, embeddings, Chroma
---

# Knowledge Base

> Languages: **English** · [中文](../../cn/knowledge/knowledge-base.md)

A knowledge base in Agently terms is: a vector store, an embedding agent that turns text into vectors, and a query path that returns relevant chunks. Agently ships a Chroma adapter as the reference implementation; its package path is still `agently.integrations.chromadb`.

## When to reach for KB

| You want to … | KB? |
|---|---|
| Always include a small fixed list of facts in the prompt | No — use `info(always=True)` (see [Context Engineering](../requests/context-engineering.md)) |
| Retrieve the relevant snippets from a large corpus per question | Yes |
| Cache structured data across executions of a flow | No — use `runtime_resources` or external storage |
| Remember conversation history | No — that's a [Session](../requests/session-memory.md) |

## Reference stack

```text
documents → embedding agent → Chroma collection
                                 │
                            (vector index)
                                 │
question → embedding agent → similarity search → top-K chunks
                                                    │
                                                    ▼
                                           agent.info(retrieved=...)
                                                    │
                                                    ▼
                                                  request
```

## Minimal usage

```python
from agently import Agently
from agently.integrations.chromadb import ChromaCollection

embedding_agent = Agently.create_agent().set_settings("OpenAICompatible", {
    "base_url": "...",
    "api_key": "...",
    "model": "${ENV.EMBEDDING_MODEL}",
})

collection = ChromaCollection(collection_name="docs", embedding_agent=embedding_agent)

# Index
collection.add([
    {"id": "doc-1", "document": "Agently has three protocol-level model plugins..."},
    {"id": "doc-2", "document": "TriggerFlow lifecycle has three states..."},
])

# Query
chunks = collection.query("how many model plugins are there?", top_n=3)

# Use in a request
agent = Agently.create_agent()
result = (
    agent
    .info({"retrieved": chunks}, always=False)
    .input("Answer using the retrieved context.")
    .start()
)
```

This API surface maps to `agently.integrations.chromadb.ChromaCollection`; the examples under `examples/chromadb/` use the same data shape.

## Patterns

### Per-request retrieval (most common)

Retrieve only what's relevant for this question, attach to a single request:

```python
chunks = collection.query(user_question, top_n=5)
agent.info({"retrieved": chunks}, always=False).input(user_question).start()
```

`always=False` keeps the retrieved snippets out of the agent's persistent prompt — they only apply for this call.

### Filter the retrieved set

Most vector stores let you filter by metadata. Use it to scope retrieval to the right user, tenant, or document type:

```python
chunks = collection.query(
    user_question,
    top_n=5,
    where={"tenant_id": current_user.tenant_id},
)
```

### After-turn ingestion

If your agent's output should become future context (e.g., a self-improving knowledge base), add a step after the request that ingests the answer back into the collection:

```python
result = agent.input(user_question).start()
collection.add([{
    "id": new_id(),
    "document": result["answer"],
    "metadata": {"source": "agent_answer"},
}])
```

Be deliberate — auto-ingesting model output without review is how knowledge bases poison themselves.

### Inside a TriggerFlow

A retrieval step is just another chunk:

```python
async def retrieve(data):
    chunks = collection.query(data.input, top_n=5)
    return {"question": data.input, "chunks": chunks}

async def answer(data):
    payload = data.input
    return await agent.info({"retrieved": payload["chunks"]}, always=False).input(payload["question"]).async_start()

flow.to(retrieve).to(answer)
```

Inject the collection as a runtime resource if it's a live client:

```python
execution = flow.create_execution(runtime_resources={"collection": collection})

async def retrieve(data):
    coll = data.require_resource("collection")
    return {"question": data.input, "chunks": coll.query(data.input, top_n=5)}
```

## Out of scope

- A full vector database. Chroma is the reference; Agently doesn't bundle one.
- Storage / persistence policies. Bring your own Chroma backend (filesystem, Postgres, hosted Chroma Cloud).
- Reranking. Add it between `query()` and the request if you need it.
- Embedding model selection. Use whatever works for your domain — the embedding agent is just an Agently agent with an embedding model configured.

## See also

- [Context Engineering](../requests/context-engineering.md) — when KB is the right tool
- [Session Memory](../requests/session-memory.md) — different problem, different tool
- [TriggerFlow State and Resources](../triggerflow/state-and-resources.md) — where to put a live Chroma client in a flow
