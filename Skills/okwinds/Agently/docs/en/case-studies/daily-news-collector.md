---
title: Daily News Collector
description: TriggerFlow + tools + structured output for a scheduled news pipeline.
keywords: Agently, case study, news, TriggerFlow, schedule
---

# Daily News Collector

> Languages: **English** · [中文](../../cn/case-studies/daily-news-collector.md)

## The problem

Every morning, collect a curated list of items from a few feeds, group them by topic, score each for relevance, and produce a single structured digest.

## The shape

```text
Schedule (cron / external)
   │
   ▼
TriggerFlow execution
   ├── pull_feeds         (parallel via for_each)
   ├── normalize          (clean and dedupe)
   ├── classify           (model: assign topic + score)
   ├── filter_low_score
   ├── group_by_topic
   └── render_digest      (model: produce the human-friendly output)
```

## Walkthrough

```python
from agently import Agently, TriggerFlow, TriggerFlowRuntimeData

agent = Agently.create_agent()


async def pull_feed(data):
    feed_url = data.input
    items = await fetch_feed(feed_url)
    return [{"feed": feed_url, **item} for item in items]


async def normalize(data):
    items = data.input
    seen = set()
    unique = []
    for item in items:
        key = (item.get("title"), item.get("link"))
        if key not in seen:
            seen.add(key)
            unique.append(item)
    await data.async_set_state("normalized", unique)
    return unique


async def classify_one(data):
    item = data.input
    result = await agent.input(item["title"] + "\n\n" + item.get("summary", "")).output({
        "topic": (str, "ai|infra|product|other", True),
        "score": (float, "0.0–1.0 relevance", True),
    }).async_start()
    return {**item, **result}


async def filter_and_group(data):
    items = [i for i in data.input if i["score"] >= 0.5]
    grouped = {}
    for item in items:
        grouped.setdefault(item["topic"], []).append(item)
    await data.async_set_state("grouped", grouped)
    return grouped


async def render_digest(data):
    grouped = data.input
    digest = await agent.info({"grouped": grouped}, always=False).input(
        "Render a markdown digest. Group by topic, top 5 per topic by score."
    ).async_start()
    await data.async_set_state("digest", digest)


flow = TriggerFlow(name="daily-news")
(
    flow.for_each(concurrency=4).to(pull_feed).end_for_each()  # one per feed
    .to(lambda data: [item for sub in data.input for item in sub])  # flatten
    .to(normalize)
    .for_each(concurrency=8).to(classify_one).end_for_each()
    .to(filter_and_group)
    .to(render_digest)
)

# external scheduler triggers this:
async def run_daily(feed_urls):
    snapshot = await flow.async_start(feed_urls)
    publish_digest(snapshot["digest"])
```

## Why these choices

- **TriggerFlow over a script** — branching on classification (filter low scores) and parallel fan-out (`for_each(concurrency=4)`) are first-class in TriggerFlow. Doing this in plain async needs careful scaffolding; in a flow it's two operators.
- **`flow.async_start(...)` not `create_execution`** — this flow is self-closing, no human input, no external `emit`. The hidden execution sugar is fine. See [Lifecycle](../triggerflow/lifecycle.md).
- **State writes for `normalized`, `grouped`, `digest`** — all three are useful for debugging when something goes wrong. They land in the close snapshot and you can inspect them after the fact.
- **One agent at module level** — the same agent is reused across hundreds of classify calls. Don't recreate per call.
- **`info(grouped, always=False)` in `render_digest`** — the grouped data is large and only relevant to this call. `always=False` keeps it out of the agent's persistent prompt.

## Trade-offs

- The classifier reuses the same agent for all topics. If one topic needs a different model, inject a `runtime_resources` map and use `data.require_resource("classifier_for_<topic>")`.
- No retry policy beyond what `.start()` provides per request. If a feed fetch fails, the whole flow fails. Add a `try/except` around `pull_feed` if partial output is acceptable.
- No persistence — the flow is short enough that survival across restarts isn't worth the complexity. Add `save()` if a single run is long enough to be interrupted.

## Cross-links

- [Patterns](../triggerflow/patterns.md) — `for_each` and concurrency
- [Model Integration](../triggerflow/model-integration.md) — calling agents inside chunks
- [Schema as Prompt](../requests/schema-as-prompt.md) — the `topic` / `score` schema
