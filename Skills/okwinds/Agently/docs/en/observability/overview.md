---
title: Observability Overview
description: The boundary between Event Center observation events, TriggerFlow stream/control events, DevTools, and coding-agent guidance.
keywords: Agently, observability, Event Center, ObservationEvent, RuntimeEvent, DevTools, TriggerFlow
---

# Observability Overview

> Languages: **English** · [中文](../../cn/observability/overview.md)

Agently has several event-like surfaces. They are related, but they do different jobs.

| Surface | Owner | Purpose | Read |
|---|---|---|---|
| Observation events | Event Center | Framework-level events such as model requests, Session, Action calls, TriggerFlow lifecycle. `RuntimeEvent` remains a 4.1.x compatibility name. | [Event Center](event-center.md) |
| TriggerFlow `emit` / `when` | TriggerFlow execution | Flow-control signals inside one execution | [TriggerFlow Events and Streams](../triggerflow/events-and-streams.md) |
| TriggerFlow runtime stream | TriggerFlow execution | Live data items for UI, SSE, logs, or wrappers | [TriggerFlow Events and Streams](../triggerflow/events-and-streams.md) |
| DevTools | `agently-devtools` companion package | Visualize runs, upload observations, run evaluations, expose an interactive wrapper | [DevTools](devtools.md) |
| Coding-agent guidance | `Agently-Skills` companion repo | Give Codex, Claude Code, Cursor, and similar tools current framework guidance | [Coding Agents](../development/coding-agents.md) |

## Rule of thumb

- Use Event Center when you want to observe framework activity without changing application behavior.
- Use TriggerFlow `emit` / `when` when an event should route work inside the flow.
- Use TriggerFlow runtime stream when a chunk needs to push live output to an external consumer.
- Use DevTools when you want a ready-made observation, evaluation, or interactive UI path.

The source-backed observation event shape lives in [`agently/types/data/event.py`](../../../agently/types/data/event.py), and the event dispatcher lives in [`agently/core/EventCenter.py`](../../../agently/core/EventCenter.py). DevTools examples live under [`examples/devtools/`](../../../examples/devtools/).
