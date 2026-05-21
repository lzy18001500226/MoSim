---
title: Playbooks
description: Recipes that combine Agently capabilities to solve common AI-application problems.
keywords: Agently, playbook, recipe, orchestration, triage
---

# Playbooks

> Languages: **English** · [中文](../../cn/playbooks/overview.md)

A playbook answers a higher-level question: *I have this kind of problem — which Agently capabilities should I combine, and how?* Each playbook references the underlying layer pages but stays opinionated about a specific scenario.

If a playbook's scenario doesn't match yours, fall back to the [Capability Map](../reference/capability-map.md) to find the right layer.

## Available playbooks

| Playbook | Use when |
|---|---|
| [TriggerFlow Orchestration](triggerflow-orchestration.md) | A multi-step process needs branching, fan-out, or pause/resume — and you want a structural template |
| [Ticket Triage](ticket-triage.md) | Classify incoming items, pick a route, hand off — a common "structured input → structured output → action" shape |

## Why playbooks exist

The other sections of the docs cover one capability per page:

- A [Schema as Prompt](../requests/schema-as-prompt.md) page tells you how `output(...)` works.
- A [Lifecycle](../triggerflow/lifecycle.md) page tells you how `seal` and `close` differ.

A playbook tells you which combination of those — across requests, sessions, actions, TriggerFlow — fits a real problem. They sit one level above the layer pages.

## What a good playbook looks like

Each page below follows the same shape:

1. **Problem framing** — the scenario in plain language, with the parts that hurt naturally.
2. **Recommended structure** — a code skeleton or flow diagram showing the pieces in their right places.
3. **Variations** — common branches (small vs large traffic, sync vs async, with vs without persistence).
4. **What to skip** — capabilities that look relevant but actually aren't.
5. **Cross-links** — pointers back to the layer pages that own each piece.

## When you don't need a playbook

If your problem is "make one model call return a structured object", you don't need a playbook — you need [Quickstart](../start/quickstart.md) and [Schema as Prompt](../requests/schema-as-prompt.md). Playbooks are for cases where the answer is "combine these three things in this order".
