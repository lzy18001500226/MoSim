---
title: 日常资讯收集器
description: TriggerFlow + tool + 结构化输出，给定时执行的资讯流水线。
keywords: Agently, 案例研究, news, TriggerFlow, schedule
---

# 日常资讯收集器

> 语言：[English](../../en/case-studies/daily-news-collector.md) · **中文**

## 问题

每天早上从几个 feed 收一份精选 item，按主题分组，对每条打相关性分，最后产出一份结构化 digest。

## 形态

```text
计划任务（cron / 外部）
   │
   ▼
TriggerFlow execution
   ├── pull_feeds         （for_each 并行）
   ├── normalize          （清洗去重）
   ├── classify           （模型：分配主题 + 分数）
   ├── filter_low_score
   ├── group_by_topic
   └── render_digest      （模型：产出人友好输出）
```

## 走读

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
        "score": (float, "0.0–1.0 相关性", True),
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
        "渲染一份 markdown digest。按主题分组，每主题前 5 按分数。"
    ).async_start()
    await data.async_set_state("digest", digest)


flow = TriggerFlow(name="daily-news")
(
    flow.for_each(concurrency=4).to(pull_feed).end_for_each()  # 一个 feed 一个
    .to(lambda data: [item for sub in data.input for item in sub])  # flatten
    .to(normalize)
    .for_each(concurrency=8).to(classify_one).end_for_each()
    .to(filter_and_group)
    .to(render_digest)
)

# 外部调度器触发：
async def run_daily(feed_urls):
    snapshot = await flow.async_start(feed_urls)
    publish_digest(snapshot["digest"])
```

## 为什么这么选

- **TriggerFlow 而非脚本** —— 按分类分支（过滤低分）与并行 fan-out（`for_each(concurrency=4)`）在 TriggerFlow 里是一等公民。普通 async 做这事需要小心搭脚手架；在 flow 里就两个 operator。
- **`flow.async_start(...)` 而非 `create_execution`** —— 这个 flow 自闭合，无人工输入、无外部 emit。隐式糖足够。见 [Lifecycle](../triggerflow/lifecycle.md)。
- **state 写入 `normalized`、`grouped`、`digest`** —— 三者都对故障排查有用。它们落入 close snapshot，事后可检查。
- **模块级一个 agent** —— 同一 agent 跨数百次 classify 调用复用。不要每次重建。
- **`info(grouped, always=False)` 在 `render_digest`** —— grouped 数据大且只对本次调用相关。`always=False` 保证不进 agent 持久 prompt。

## 取舍

- 分类器对所有主题用同一 agent。某个主题需要不同模型时，注入 `runtime_resources` map 并用 `data.require_resource("classifier_for_<topic>")`。
- 没有比 `.start()` 自带的更进一步的重试策略。某个 feed 抓失败整个 flow 失败。能接受部分输出时给 `pull_feed` 包 `try/except`。
- 无持久化 —— flow 短到不值得跨重启复杂度。单次运行长到可能被中断时加 `save()`。

## 交叉链接

- [模式](../triggerflow/patterns.md) —— `for_each` 与并发
- [模型集成](../triggerflow/model-integration.md) —— 在 chunk 内调 agent
- [Schema as Prompt](../requests/schema-as-prompt.md) —— `topic` / `score` schema
