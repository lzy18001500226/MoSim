---
title: PRD → Test Cases
description: Long structured input + per-section streaming + ensure-marked required fields for a comprehensive test case generator.
keywords: Agently, case study, PRD, test cases, structured output, streaming
---

# PRD → Test Cases

> Languages: **English** · [中文](../../cn/case-studies/prd-testcases.md)

## The problem

Given a multi-page Product Requirements Document, produce a comprehensive set of test cases:

- functional cases per requirement
- edge cases per requirement
- non-functional cases (perf, security, accessibility) where relevant
- traceability back to the requirement

The output must be complete (no skipped requirements) and stable in shape (a downstream tracking system ingests it).

## The shape

```text
PRD text → list_requirements → per_requirement_cases (for_each) → consolidate
```

A TriggerFlow makes sense here because the second step is a fan-out over an unbounded number of requirements.

## Walkthrough

```python
from agently import Agently, TriggerFlow, TriggerFlowRuntimeData

agent = Agently.create_agent()


async def list_requirements(data):
    prd_text = data.input
    result = await agent.input(prd_text).output({
        "requirements": [
            {
                "id": (str, "Stable id like REQ-001", True),
                "title": (str, "Short title", True),
                "text": (str, "Verbatim or close paraphrase", True),
            }
        ],
    }).async_start()
    await data.async_set_state("requirements", result["requirements"])
    return result["requirements"]


async def cases_for_one(data):
    req = data.input
    return await agent.info({"requirement": req}, always=False).input(
        "Produce test cases covering functional, edge, and non-functional aspects."
    ).output({
        "requirement_id": (str, "Matches REQ id", True),
        "functional": [
            {
                "id": (str, "stable id", True),
                "title": (str, "case title", True),
                "steps": [(str, "step", True)],
                "expected": (str, "expected result", True),
            }
        ],
        "edge": [
            {
                "id": (str, "stable id", True),
                "title": (str, "case title", True),
                "steps": [(str, "step", True)],
                "expected": (str, "expected result", True),
            }
        ],
        "non_functional": [
            {
                "id": (str, "stable id", True),
                "kind": (str, "perf/security/accessibility/...", True),
                "title": (str, "case title", True),
                "rationale": (str, "why this matters for this requirement", True),
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

## Why these choices

- **Two-step model use** — a single mega-prompt tends to skip requirements or invent them. Splitting into `list_requirements` (the model focuses purely on extraction) and `cases_for_one` (focuses on cases for one given requirement) gives much more reliable coverage.
- **Aggressive `ensure` flags** — every leaf the downstream system depends on is marked `True` (the third slot). The framework retries when fields are missing. See [Schema as Prompt](../requests/schema-as-prompt.md).
- **`for_each(concurrency=3)`** — bounded parallelism. Higher gets you rate-limited; lower drags out the runtime. Pick based on your provider's quota.
- **`info(requirement, always=False)`** — each chunk handler injects only the requirement it's working on. The model isn't confused by other requirements.
- **`flow.async_start(...)`** — self-closing, no pause. Hidden sugar is appropriate.

## Variations

### Stream per-section progress

If a UI displays partial results as they're generated, push each requirement's cases into the runtime stream:

```python
async def cases_for_one(data):
    req = data.input
    response = agent.info({"requirement": req}, always=False).input("...").output({...}).get_response()
    async for item in response.get_async_generator(type="instant"):
        if item.is_complete:
            await data.async_put_into_stream({"req_id": req["id"], "path": item.path, "value": item.value})
    return await response.async_get_data()
```

The consumer of `execution.get_async_runtime_stream(...)` sees per-requirement, per-field progress. See [Events and Streams](../triggerflow/events-and-streams.md).

### Validate against the requirement set

If `consolidate` notices that some requirements are missing from the case map, add a `.validate(...)` to fail-and-retry instead of silently shipping incomplete output:

```python
def all_requirements_covered(result, ctx):
    expected_ids = {r["id"] for r in ctx.input}  # the requirements list
    got_ids = {tc["requirement_id"] for tc in result.get("items", [])}
    missing = expected_ids - got_ids
    if missing:
        return {"ok": False, "reason": f"missing: {sorted(missing)}", "validator_name": "coverage"}
    return True
```

This works at the per-chunk level — applying it across the consolidate output requires comparing against the upstream requirements list, easiest to do in plain Python after `consolidate`.

### Save and resume on long PRDs

For very long PRDs (50+ requirements), the run can be long enough to want checkpointing. Switch to `flow.create_execution(auto_close=False)`, save after `list_requirements`, and resume to pick up the for_each. See [Persistence and Blueprint](../triggerflow/persistence-and-blueprint.md).

## Cross-links

- [Patterns](../triggerflow/patterns.md) — `for_each` with `concurrency`
- [Output Control](../requests/output-control.md) — `.validate(...)` for coverage checks
- [Schema as Prompt](../requests/schema-as-prompt.md) — `ensure` flags on every required field
