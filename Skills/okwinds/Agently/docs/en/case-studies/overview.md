---
title: Case Studies
description: Real scenarios showing how Agently capabilities combine to solve concrete problems.
keywords: Agently, case studies, examples, KB dialog, daily news, talk to control
---

# Case Studies

> Languages: **English** · [中文](../../cn/case-studies/overview.md)

Each case study is a short walkthrough of one realistic scenario: the problem, the structure that solves it, the Agently pieces involved, and the trade-offs that drove the decisions.

These are **examples**, not prescriptions. They highlight common shapes you'll see when building real applications. If a case study mostly fits your scenario, follow it; if not, the [Capability Map](../reference/capability-map.md) and [Playbooks](../playbooks/overview.md) are better starting points.

## Available case studies

| Case study | Combines |
|---|---|
| [Daily News Collector](daily-news-collector.md) | TriggerFlow + tools + structured output + scheduled run |
| [Talk to Control](talk-to-control.md) | Conversational agent + actions on a domain object + streaming |
| [Knowledge Base Dialog](kb-dialog.md) | Embeddings + retrieval + session memory + structured answer |
| [PRD → Test Cases](prd-testcases.md) | Long-input structured output + ensure-marked required fields + per-section streaming |
| [Survey Dialog](survey-dialog.md) | Multi-turn session + dynamic prompts + branching follow-ups |

## What each case study covers

Each page is structured the same way:

1. **The problem** — what someone actually asked for.
2. **The shape** — how the pieces fit together at a glance.
3. **Walkthrough** — the relevant code with explanations.
4. **Why these choices** — the trade-offs and what the alternatives would cost.
5. **Where it lives** — pointer to the runnable example in the repository, when one exists.

## Reading order

If you're new, read [Daily News Collector](daily-news-collector.md) first — it covers the most ground in the least space. If you have a specific shape in mind (RAG, conversational with actions, long-input parsing), jump straight to the relevant case.
