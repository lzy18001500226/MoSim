---
title: Runtime Intervention
description: Adding supplemental context to an open TriggerFlow execution without pausing or mutating the graph.
keywords: Agently, TriggerFlow, runtime intervention, intervention_point, human context
---

# Runtime Intervention

> Languages: **English** · [中文](../../cn/triggerflow/runtime-intervention.md)

Runtime intervention lets outside code add supplemental context to an open execution. TriggerFlow records that context immediately, then makes it visible to chunks at a safe boundary.

Use runtime intervention when a user adds a note, correction, attachment summary, or other context while the workflow is already running. Use [Pause and Resume](pause-and-resume.md) when the workflow must stop and wait for a required external answer.

## Modes

Intervention is disabled unless you opt in or the flow declares an explicit intervention point:

```python
execution = flow.create_execution(
    auto_close=False,
)
```

With `intervention_mode="planned"`, only explicit intervention points insert pending context:

```python
(
    flow
    .to(extract_terms)
    .intervention_point(name="before_risk", target="before_risk")
    .to(risk_assessment)
)
```

When a flow declares `intervention_point(...)`, `create_execution(...)` infers planned mode if `intervention_mode` is omitted. Pass `intervention_mode=None` only when you deliberately want to disable intervention for that execution.

With `intervention_mode="auto"`, TriggerFlow checks pending interventions before chunk dispatch. Targeted interventions insert before the first matching operator id, name, kind, group id, or group kind. Untargeted interventions insert at the next chunk boundary. A flow that declares `intervention_point(...)` cannot run in auto mode.

## Add Context

```python
await execution.async_intervene(
    {"text": "Attachment A is the latest price table."},
    author="reviewer",
    target="before_risk",
)
```

`intervene(...)` records a pending ledger item. It does not emit an event, does not pause the graph, and does not rewrite `data.input` or `data.value`.

## Read And Consume

Chunks read inserted interventions from `data.interventions` or `data.get_interventions(...)`:

```python
async def risk_assessment(data: TriggerFlowRuntimeData):
    supplements = data.get_interventions(status="inserted", target="before_risk")
    result = await assess_with_model(
        {
            "terms": data.input,
            "supplements": [item["payload"] for item in supplements],
        }
    )
    for item in supplements:
        await data.async_mark_intervention_consumed(
            item["id"],
            status="applied",
        )
    return result
```

Reading is not consumption. Use `mark_intervention_consumed(...)` to write a per-consumer audit entry with status `"applied"` or `"ignored"`. Runtime data defaults `consumer` to the current chunk name; execution-level calls still require an explicit consumer.

## Close And Persistence

Still-pending interventions become `"expired"` during `close()`. The ledger remains readable through `execution.result.get_interventions(...)` and is also included in the close snapshot under `"$interventions"`.

`execution.save()` / `execution.load()` preserve the intervention mode, ledger, version counter, insertion metadata, expiration state, and consumer metadata. Runtime policy callables are not serialized; restored auto-mode executions use the builtin policy unless a new callable is supplied.

## Runtime Stream

Intervention lifecycle changes are emitted as fail-open runtime stream items:

```python
{
    "type": "intervention",
    "action": "append",  # append | insert | expire | consume | reject
    "execution_id": execution.id,
    "intervention": {...},
}
```

Older stream consumers can ignore the unknown `type`. Observation events use `triggerflow.intervention_received`, `triggerflow.intervention_inserted`, `triggerflow.intervention_expired`, `triggerflow.intervention_consumed`, and `triggerflow.intervention_rejected`.

## See also

- `examples/step_by_step/11-triggerflow-21_document_review_runtime_intervention.py` — planned-mode document-review scenario
- `examples/step_by_step/11-triggerflow-22_ticket_triage_auto_intervention.py` — auto-mode ticket-triage scenario
- [Pause and Resume](pause-and-resume.md) — required waits and graph resume
- [Events and Streams](events-and-streams.md) — stream consumption
- [Execution Result](execution-result.md) — result-side intervention readers
