---
title: Knowledge Base Dialog
description: Multi-turn dialog over a knowledge base with retrieval and structured answers.
keywords: Agently, case study, KB, RAG, dialog, session, retrieval
---

# Knowledge Base Dialog

> Languages: **English** · [中文](../../cn/case-studies/kb-dialog.md)

## The problem

A user asks questions in natural language about a document collection (product docs, policies, internal wiki). Each turn:

1. Retrieve the relevant passages.
2. Answer using only those passages.
3. Cite sources.
4. Maintain conversation context across turns.

## The shape

```text
User question
   │
   ▼
Retrieve top-K from KB        ◄── via embedding agent + vector store
   │
   ▼
Agent.input(question).info({"sources": chunks}, always=False).output({...})
   │
   ▼
Structured answer + cited sources
   │
   ▼
Append to session history
```

## Walkthrough

```python
from agently import Agently

# Embedding agent — small / fast model, just for vectorization
embedding_agent = Agently.create_agent().set_settings("OpenAICompatible", {
    "base_url": "...",
    "api_key": "...",
    "model": "${ENV.EMBEDDING_MODEL}",
})

# Answering agent — reasoning model
agent = (
    Agently.create_agent()
    .role(
        "Answer using ONLY the provided sources. If the sources do not "
        "contain the answer, say so explicitly.",
        always=True,
    )
)
agent.activate_session(session_id="kb-dialog")  # multi-turn

from agently.integrations.chromadb import ChromaCollection
collection = ChromaCollection(collection_name="docs", embedding_agent=embedding_agent)


def ask(user_question: str):
    chunks = collection.query(user_question, top_n=5)
    return (
        agent
        .info({"sources": chunks}, always=False)
        .input(user_question)
        .output({
            "answer": (str, "Direct answer", True),
            "citations": [
                {
                    "source_id": (str, "Source id from the provided sources", True),
                    "quote": (str, "Short verbatim quote", True),
                }
            ],
            "uncertain": (bool, "True if the sources do not fully answer the question", True),
        })
        .start()
    )


# Loop
while True:
    user_text = input("> ")
    if not user_text.strip():
        break
    result = ask(user_text)
    print(result["answer"])
    for c in result["citations"]:
        print(f"  [{c['source_id']}] {c['quote']}")
    if result["uncertain"]:
        print("  (the sources do not fully cover this question)")
```

## Why these choices

- **Two agents, one role each** — embedding and answering have different model needs (cheap small model for embeddings; reasoning model for answers). Don't share an agent across roles.
- **`info(sources, always=False)`** — sources change every turn; they shouldn't accumulate in the agent's persistent prompt. `always=False` makes them per-call.
- **`role(always=True)` enforces grounding** — the "answer using only the provided sources" instruction is part of every turn. Don't repeat it in `instruct` per call.
- **Structured output with `citations`** — citations are programmatic. Putting them in the schema (rather than asking the model to format them in prose) makes them reliably parseable.
- **`uncertain: bool`** — explicit "I don't know" is critical for KB systems. Forcing it as a required field (`True` in the third slot, ensure flag) means the model can't quietly hallucinate around gaps. See [Schema as Prompt](../requests/schema-as-prompt.md).
- **Session for multi-turn** — the user can ask follow-ups ("what about the next version?", "show me the limits") without repeating context. `activate_session()` enables session windowing.

## Variations

### Filter retrieval per user

If your KB has multiple tenants or users, scope retrieval at query time:

```python
chunks = collection.query(user_question, top_n=5, where={"tenant_id": current_user.tenant_id})
```

### Validate citations against the retrieved set

Add `.validate(...)` to make sure cited `source_id`s actually appear in the retrieved chunks:

```python
def cite_check(result, ctx):
    valid_ids = {c["id"] for c in ctx.input.get("sources", [])}
    bad = [c for c in result["citations"] if c["source_id"] not in valid_ids]
    if bad:
        return {"ok": False, "reason": "fabricated source_id", "validator_name": "citation"}
    return True
```

See [Output Control](../requests/output-control.md).

### Stream the answer

If the user is reading interactively, stream the `answer` field:

```python
gen = agent.info({"sources": chunks}, always=False).input(user_text).output({...}).get_generator(type="instant")
for item in gen:
    if item.path == "answer" and item.delta:
        print(item.delta, end="", flush=True)
```

## Cross-links

- [Knowledge Base](../knowledge/knowledge-base.md) — embedding + Chroma
- [Session Memory](../requests/session-memory.md) — multi-turn context
- [Output Control](../requests/output-control.md) — validating citations
- [Context Engineering](../requests/context-engineering.md) — `info` per-call vs persistent
