---
title: Talk to Control
description: Conversational agent that takes actions on a domain object based on natural language.
keywords: Agently, case study, talk to control, actions, conversational
---

# Talk to Control

> Languages: **English** · [中文](../../cn/case-studies/talk-to-control.md)

## The problem

A user controls something — a document, a dashboard, a set of records — by typing natural-language commands. Each turn, the model:

1. Understands what the user means.
2. Picks an action from a fixed set.
3. Executes the action against the current domain object.
4. Replies with what it did and what state things are in now.

## The shape

```text
User input  →  Agent (with actions) → action call(s) → updated state → reply
                       ▲
                       │
                  Session (multi-turn history)
```

This is fundamentally a conversational agent with actions. No TriggerFlow needed unless you have multi-step processes per turn.

## Walkthrough

```python
from agently import Agently

agent = (
    Agently.create_agent()
    .role("You control a shopping cart. Use the available actions to make changes.", always=True)
    .info({"format": "After each action, briefly confirm what changed."}, always=True)
)

# A simple in-memory cart for the demo
cart = {"items": [], "total": 0.0}


@agent.action_func
def add_item(name: str, price: float, quantity: int = 1):
    """Add a product to the cart."""
    cart["items"].append({"name": name, "price": price, "quantity": quantity})
    cart["total"] += price * quantity
    return cart


@agent.action_func
def remove_item(name: str):
    """Remove a product from the cart."""
    cart["items"] = [i for i in cart["items"] if i["name"] != name]
    cart["total"] = sum(i["price"] * i["quantity"] for i in cart["items"])
    return cart


@agent.action_func
def show_cart():
    """Return the current cart state."""
    return cart


agent.use_actions([add_item, remove_item, show_cart])

# Enable a session so multi-turn context is bounded
agent.activate_session(session_id="cart-demo")

# Conversation loop
while True:
    user_text = input("> ")
    if not user_text.strip():
        break
    reply = agent.input(user_text).start()
    print(reply)
```

## Why these choices

- **`@agent.action_func` for each operation, not a single "do anything" tool** — small, well-named actions let the model pick correctly. A monolithic tool forces the model to encode parameters in JSON inside a string.
- **`role(always=True)` for behavior, `info(always=True)` for formatting** — both are stored on the agent and included in every request that agent runs, so they count toward each request's prompt.
- **`activate_session()` instead of manual chat history management** — for chat-style interactions, Session maintains full history and the current context window. Register a custom resize handler when you need summarization. See [Session Memory](../requests/session-memory.md).
- **Cart kept as module state for the demo** — in real code this would be a database, with the action functions doing reads/writes. The shape doesn't change.
- **No structured output schema** — the agent's reply is for a human. Don't force structure unless something else consumes it programmatically.

## Variations

### Stream the reply

For a UI, switch to streaming so the user sees the response as it's generated:

```python
gen = agent.input(user_text).get_generator(type="delta")
for delta in gen:
    print(delta, end="", flush=True)
```

See [Model Response](../requests/model-response.md) for streaming options.

### Add a structured side-channel

If your UI needs to know which action ran (to highlight a row, animate, etc.), read `agent.get_action_result()` after each turn:

```python
records = agent.get_action_result()
for r in records:
    notify_ui(action=r.name, args=r.input, result=r.output)
```

### Multi-step per turn

If a single user message triggers a multi-step process (lookup → confirm → apply), promote the per-turn handling to a TriggerFlow. The conversation layer still lives in the agent; the flow runs inside one turn. See [TriggerFlow Orchestration Playbook](../playbooks/triggerflow-orchestration.md).

## Cross-links

- [Action Runtime](../actions/action-runtime.md) — `@agent.action_func` and `use_actions`
- [Session Memory](../requests/session-memory.md) — `activate_session()`, windowing, custom memo
- [Async First](../start/async-first.md) — async equivalents of the loop above
