---
title: Ticket Triage Playbook
description: Classify incoming items, route to the right handler, hand off — a structured-input → structured-output → action template.
keywords: Agently, playbook, triage, classification, routing
---

# Ticket Triage Playbook

> Languages: **English** · [中文](../../cn/playbooks/ticket-triage.md)

## When to use this playbook

You receive a stream of items (tickets, emails, alerts, requests). For each, you need to:

1. Classify it into a small set of categories.
2. Pick a downstream handler based on the classification.
3. Run the handler (call an API, call a model, escalate to a human).
4. Record the outcome.

The model is doing the classification (and possibly some of the handling). You want stable categories, predictable retries, and an audit trail of what was decided.

## Recommended structure

This is small enough that you can decide between two shapes:

- **Single request** if the categories are simple and the handler doesn't need flow control.
- **TriggerFlow** if you need branching with multiple steps per branch, parallel handling, or pause/resume.

### Single-request shape

```python
from agently import Agently

agent = Agently.create_agent()

result = (
    agent
    .info({
        "categories": ["billing", "technical", "spam", "other"],
        "format": "Reply only with the schema below.",
    }, always=True)
    .input(ticket_text)
    .output({
        "category": (str, "One of billing/technical/spam/other", True),
        "severity": (str, "low/med/high", True),
        "summary": (str, "One-line summary", True),
    })
    .validate(ensure_known_category)
    .start()
)

route_to_handler(result["category"], result)
```

`info(always=True)` keeps the category list visible to the model on every call without bloating per-request prompts. `.validate(...)` enforces that `category` is one of the allowed strings — see [Output Control](../requests/output-control.md).

The Python `route_to_handler(...)` is plain code: a dict of category → function.

### TriggerFlow shape

When per-category handling has its own steps:

```python
def build_flow():
    flow = TriggerFlow(name="triage")

    async def classify(data: TriggerFlowRuntimeData):
        return await classifier.input(data.input).output({
            "category": (str, "...", True),
            "severity": (str, "...", True),
            "summary": (str, "...", True),
        }).async_start()

    async def handle_billing(data):
        # multi-step billing flow ...
        await data.async_set_state("outcome", {"path": "billing", "ok": True})

    async def handle_technical(data):
        # multi-step technical flow ...
        await data.async_set_state("outcome", {"path": "technical", "ok": True})

    async def handle_spam(data):
        await data.async_set_state("outcome", {"path": "spam", "ok": True})

    async def handle_other(data):
        await data.async_set_state("outcome", {"path": "other", "ok": True})

    (
        flow.to(classify)
        .match_on(lambda d: d.input["category"])  # or use match() + cases on the category value
            .case("billing").to(handle_billing)
            .case("technical").to(handle_technical)
            .case("spam").to(handle_spam)
            .case_else().to(handle_other)
        .end_match()
    )

    return flow
```

Each per-category handler can grow into its own sub-flow if it gets complicated — see [Sub-Flow](../triggerflow/sub-flow.md).

## Variations

### High volume — batch in parallel

When tickets arrive in batches, fan out and process in parallel:

```python
flow.for_each(concurrency=8).to(triage_one_ticket).end_for_each().to(persist_results)
```

Set `concurrency` to whatever your model rate limit and downstream APIs can sustain.

### Need human approval for some categories

For high-stakes categories (refunds, account closures), pause the flow and wait for a human:

```python
async def maybe_request_approval(data):
    if data.input["category"] == "refund" and data.input["amount"] > 1000:
        return await data.async_pause_for(
            type="approval",
            payload={"ticket_id": data.input["id"], "amount": data.input["amount"]},
            resume_to="next",
        )
    return data.input
```

The execution must be created with `auto_close=False` (see [Pause and Resume](../triggerflow/pause-and-resume.md)).

### Audit trail

Push each decision to runtime stream so an external logger can record it:

```python
async def classify(data):
    result = await classifier.input(data.input).output({...}).async_start()
    await data.async_put_into_stream({"event": "classified", "result": result})
    return result
```

Consume from `execution.get_async_runtime_stream(...)` outside the flow.

## What to skip

- Don't add a TriggerFlow if your handlers are one-step each. Just route in plain Python — the single-request shape above is enough.
- Don't try to make the model do the routing logic ("now respond with what to do"). Get a clean structured answer (`category`, `severity`, `summary`), then let your code route. Models are good at classifying; orchestration logic belongs in your code.
- Don't put the classifier model name in `flow_data`. Use `runtime_resources` (or pin the agent at module level).

## Cross-links

- [Output Control](../requests/output-control.md) — `.validate(...)` for category enforcement
- [Schema as Prompt](../requests/schema-as-prompt.md) — `(type, "...", True)` for the classification fields
- [TriggerFlow Patterns](../triggerflow/patterns.md) — `match` and `case`
- [Sub-Flow](../triggerflow/sub-flow.md) — when per-category handling grows
