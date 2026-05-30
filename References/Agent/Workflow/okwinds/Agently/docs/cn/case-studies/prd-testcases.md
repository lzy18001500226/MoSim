---
title: PRD → 测试用例
description: 长结构化输入 + 分段流式 + ensure 标记必填字段，给一个完整测试用例生成器。
keywords: Agently, 案例研究, PRD, 测试用例, 结构化输出, 流式
---

# PRD → 测试用例

> 语言：[English](../../en/case-studies/prd-testcases.md) · **中文**

## 问题

给一份多页 PRD，产出完整测试用例集：

- 每个需求的功能用例
- 每个需求的边界用例
- 相关时的非功能用例（性能、安全、可达性）
- 追溯到需求

输出必须完整（没有跳过的需求）且形态稳定（下游跟踪系统消费）。

## 形态

```text
PRD 文本 → list_requirements → per_requirement_cases (for_each) → consolidate
```

TriggerFlow 在这里有意义因为第二步是对未知数量需求的 fan-out。

## 走读

```python
from agently import Agently, TriggerFlow, TriggerFlowRuntimeData

agent = Agently.create_agent()


async def list_requirements(data):
    prd_text = data.input
    result = await agent.input(prd_text).output({
        "requirements": [
            {
                "id": (str, "稳定 id 如 REQ-001", True),
                "title": (str, "短标题", True),
                "text": (str, "逐字或近义复述", True),
            }
        ],
    }).async_start()
    await data.async_set_state("requirements", result["requirements"])
    return result["requirements"]


async def cases_for_one(data):
    req = data.input
    return await agent.info({"requirement": req}, always=False).input(
        "产出覆盖功能、边界、非功能方面的测试用例。"
    ).output({
        "requirement_id": (str, "匹配 REQ id", True),
        "functional": [
            {
                "id": (str, "稳定 id", True),
                "title": (str, "用例标题", True),
                "steps": [(str, "步骤", True)],
                "expected": (str, "预期结果", True),
            }
        ],
        "edge": [
            {
                "id": (str, "稳定 id", True),
                "title": (str, "用例标题", True),
                "steps": [(str, "步骤", True)],
                "expected": (str, "预期结果", True),
            }
        ],
        "non_functional": [
            {
                "id": (str, "稳定 id", True),
                "kind": (str, "perf/security/accessibility/...", True),
                "title": (str, "用例标题", True),
                "rationale": (str, "为何对该需求重要", True),
            }
        ],
    }).async_start()


async def consolidate(data):
    by_req = {item["requirement_id"]: item for item in data.input}
    await data.async_set_state("test_cases", by_req)


flow = TriggerFlow(name="prd-to-cases")
(
    flow.to(list_requirements)
    .for_each(concurrency=3)
        .to(cases_for_one)
    .end_for_each()
    .to(consolidate)
)


async def run(prd_text):
    return await flow.async_start(prd_text)
```

## 为什么这么选

- **两步模型用法** —— 单个超级 prompt 容易跳过需求或编造。拆为 `list_requirements`（模型纯做提取）与 `cases_for_one`（针对一个需求做用例）覆盖率更可靠。
- **激进的 `ensure` 标记** —— 下游依赖的每个叶子第三槽 `True`。框架在缺字段时重试。见 [Schema as Prompt](../requests/schema-as-prompt.md)。
- **`for_each(concurrency=3)`** —— 受限并发。更高被限速；更低拖长运行。按你的 provider 配额选。
- **`info(requirement, always=False)`** —— 每个 chunk handler 只注入它在处理的需求。模型不被其他需求干扰。
- **`flow.async_start(...)`** —— 自闭合，无 pause。隐式糖合适。

## 变体

### 流分段进度

UI 边生成边显示时，把每需求的用例推到 runtime stream：

```python
async def cases_for_one(data):
    req = data.input
    response = agent.info({"requirement": req}, always=False).input("...").output({...}).get_response()
    async for item in response.get_async_generator(type="instant"):
        if item.is_complete:
            await data.async_put_into_stream({"req_id": req["id"], "path": item.path, "value": item.value})
    return await response.async_get_data()
```

`execution.get_async_runtime_stream(...)` 消费者看到按需求按字段的进度。见 [事件与流](../triggerflow/events-and-streams.md)。

### 校验需求覆盖

`consolidate` 注意到部分需求未在用例 map 里时，用 `.validate(...)` 失败重试，而非悄悄出不完整：

```python
def all_requirements_covered(result, ctx):
    expected_ids = {r["id"] for r in ctx.input}  # 需求列表
    got_ids = {tc["requirement_id"] for tc in result.get("items", [])}
    missing = expected_ids - got_ids
    if missing:
        return {"ok": False, "reason": f"missing: {sorted(missing)}", "validator_name": "coverage"}
    return True
```

它在 chunk 级工作 —— 跨 consolidate 输出时与上游需求列表对比，最容易在 `consolidate` 后用普通 Python 做。

### 长 PRD 的保存恢复

很长的 PRD（50+ 需求）运行可能足够长，值得 checkpoint。换 `flow.create_execution(auto_close=False)`，`list_requirements` 后保存，恢复继续 for_each。见 [持久化与 Blueprint](../triggerflow/persistence-and-blueprint.md)。

## 交叉链接

- [模式](../triggerflow/patterns.md) —— `for_each` 与 `concurrency`
- [输出控制](../requests/output-control.md) —— `.validate(...)` 覆盖检查
- [Schema as Prompt](../requests/schema-as-prompt.md) —— 每个必填字段的 `ensure` 标记
