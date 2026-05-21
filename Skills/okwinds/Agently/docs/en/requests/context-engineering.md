---
title: Context Engineering
description: How to put background knowledge in front of a model without bloating the prompt.
keywords: Agently, context, info, session, KB, retrieval, instruct
---

# Context Engineering

> Languages: **English** · [中文](../../cn/requests/context-engineering.md)

The model only knows what fits in its context window. Context engineering is the discipline of choosing what goes in, where it goes, and what gets omitted.

## Where context can come from

| Source | Where it lands | Lifetime |
|---|---|---|
| `role` / `system` slot | system message | persistent for the agent |
| `info` slot | system or user (impl detail) | persistent or per-request |
| `instruct` slot | user message | persistent or per-request |
| `input` slot | user message | per-request |
| Session chat history | user/assistant messages | accumulates across requests |
| Session memo | system message | persists, written by custom resize handlers |
| Knowledge base retrieval | injected by retrieval code | per-request, on demand |
| Tool / MCP results | tool messages | accumulates within one tool loop |

Use the right slot for the right job:

- **role / system** — who the model is, hard rules (tone, persona, refusal patterns).
- **info** — facts that don't change between calls (product catalog, severity levels, formatting conventions).
- **instruct** — how to do *this kind* of request (steps, ordering, output style).
- **input** — the single payload that varies per call.
- **chat history** — what the user and model said in this session.
- **memo** — application-defined compressed long-term context.
- **KB** — large knowledge that's not always relevant.

Don't put everything in `input`. Don't put per-request payload in `info`.

## When to use which

| You have … | Put it in … |
|---|---|
| The agent's persona / tone / capability rules | `role` (`always=True`) |
| A fixed enumeration the model must know about (e.g., severity codes) | `info` (`always=True`) |
| Step-by-step instructions for one kind of task | `instruct` (`always=True` if the agent does only this kind) |
| The variable payload of one call | `input` |
| The previous turns of a conversation | session chat history |
| 100k tokens of company docs | KB with retrieval, not the prompt |
| Recently retrieved facts that are relevant *this turn* | `info` for this request only |

## Keep info diffable

`info` accepts dicts and the framework renders them. This is preferable to baking JSON strings into the prompt yourself — diffs stay readable, and the framework can render to YAML / JSON / pseudo-table forms consistently.

```python
agent.info({
    "severities": ["P0", "P1", "P2", "P3"],
    "format": "Use markdown bullets, no preamble.",
}, always=True)
```

## Don't carry tool catalogs by hand

If you're using actions / tools, the framework already injects the tool catalog when the model needs to plan a tool call. Don't manually copy tool descriptions into `info`. See [Action Runtime](../actions/action-runtime.md).

## Session vs KB vs `info`

| Scenario | Best fit |
|---|---|
| "Remember the user's name across this conversation" | session chat history |
| "Remember the user's preferences across many conversations" | custom session resize / memo, or an application-level user profile |
| "Look up the right snippet from a knowledge base" | KB retrieval, then put the retrieved snippets in per-request `info` |
| "The model always needs this fixed list" | `info(always=True)` |
| "The user just sent a 500-word problem statement" | `input` |

## Compression beats truncation

When the context window starts to fill up:

- The default Session only trims the window by `session.max_length`; when you need summaries, register a custom resize handler and write the summary into session `memo`. See [Session Memory](session-memory.md).
- For one-off long inputs, summarize before the request rather than truncating mid-sentence.

## Per-request info without polluting the agent

```python
result = (
    agent
    .info({"retrieved_snippets": chunks}, always=False)  # request-only
    .input(question)
    .output({...})
    .start()
)
```

Without `always=True`, `info` is set only for this call.

## See also

- [Prompt Management](prompt-management.md) — slot semantics in detail
- [Session Memory](session-memory.md) — chat history and memo
- [Knowledge Base](../knowledge/knowledge-base.md) — retrieval-before-prompt pattern
- [Action Runtime](../actions/action-runtime.md) — tool catalogs are injected automatically
