---
title: Session Memory
description: How Session attaches to agents, records multi-turn history, bounds the context window, and imports / exports state.
keywords: Agently, session, activate_session, chat history, memo, context window
---

# Session Memory

> Languages: **English** · [中文](../../cn/requests/session-memory.md)

Session is Agently's multi-turn conversation container. It keeps the full conversation history (`full_context`) and the window that is actually injected into the next request (`context_window`). The default strategy only bounds length; if you need summarization, long-term preferences, or more specialized pruning, register your own analysis / resize handlers.

## Enable and disable

```python
from agently import Agently

agent = Agently.create_agent()
agent.activate_session(session_id="support-demo")

agent.input("Remember this: my order id is A-100.").start()
reply = agent.input("What is my order id?").start()

agent.deactivate_session()
```

`activate_session(session_id=...)` creates or reuses the `Session` for that id and writes `runtime.session_id` into the agent settings. Use `deactivate_session()` to stop injecting session chat history into future requests.

## Chat history methods

With a session active, these agent methods proxy to the current session:

```python
agent.set_chat_history([
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hi, I'm an Agently assistant."},
])

agent.add_chat_history({"role": "user", "content": "Continue the same topic."})
agent.reset_chat_history()
```

The current session is available as `agent.activated_session`. Without an active session, these methods fall back to the ordinary agent prompt chat-history behavior.

## Default window policy

The built-in setting is:

```python
agent.set_settings("session.max_length", 12000)
```

When the approximate text length of `context_window` exceeds `session.max_length`, the default handler runs `simple_cut`: it keeps the newest messages that fit. If even the newest message is too long, it keeps the tail of that message.

This is an approximate character count over serialized messages, not exact token accounting.

## Choose what gets recorded

By default, after a request finishes, Session appends the rendered prompt text as user content and the result data as assistant content. To record only specific paths:

```python
agent.set_settings("session.input_keys", ["info.task", "input.question"])
agent.set_settings("session.reply_keys", ["answer", "score"])
```

`session.input_keys` is resolved from prompt data; `session.reply_keys` is resolved from parsed result data. Set them back to `None` for the default recording behavior.

## Custom resize / memo

The built-in Session does not automatically call a model to summarize history. `memo` is a serializable field that your resize handler can update:

```python
def analysis_handler(full_context, context_window, memo, session_settings):
    if len(context_window) > 6:
        return "keep_last_four"
    return None


def keep_last_four(full_context, context_window, memo, session_settings):
    new_memo = {
        "previous_turns": len(full_context) - 4,
        "note": "Older turns were summarized by application code.",
    }
    return None, list(context_window[-4:]), new_memo


agent.register_session_analysis_handler(analysis_handler)
agent.register_session_resize_handler("keep_last_four", keep_last_four)
```

If you want model-generated memory, call the model in your own resize handler. Session stores the returned `memo` and injects it into later requests.

## Import / export

```python
from agently.core import Session

session = agent.activated_session
json_text = session.get_json_session()
yaml_text = session.get_yaml_session()

restored = Session(settings=agent.settings)
restored.load_json_session(json_text)

agent.sessions[restored.id] = restored
agent.activate_session(session_id=restored.id)
```

Aliases also exist: `session.to_json()` / `session.to_yaml()`, and `session.load_json(...)` / `session.load_yaml(...)`.

## Boundaries

Session owns multi-turn chat history, the current context window, an optional memo field, and import / export. It does not own durable storage backends, vector databases, cross-device user profiles, or exact token budgeting. Put those in your application layer or knowledge-base layer.

## See also

- [Context Engineering](context-engineering.md) — when to use session, prompt info, or KB
- [Knowledge Base](../knowledge/knowledge-base.md) — retrieval-backed context
- [Prompt Management](prompt-management.md) — how chat history enters a request
