import asyncio

from agently import TriggerFlow, TriggerFlowRuntimeData


async def runtime_event_data_demo():
    flow = TriggerFlow(name="step-06-runtime-event-data")

    async def inspect_event(data: TriggerFlowRuntimeData):
        await data.async_set_state("seen_event", data.event)
        await data.async_emit("CustomEvent", {"from": data.event, "value": data.input})
        return data.input

    async def store_custom_event(data: TriggerFlowRuntimeData):
        await data.async_set_state(
            "custom_event",
            {
                "event": data.event,
                "type": data.trigger_type,
                "payload": data.input,
                "layer": data.layer_mark,
            },
        )

    flow.to(inspect_event)
    flow.when("CustomEvent").to(store_custom_event)

    execution = flow.create_execution(auto_close=False)
    await execution.async_start("hello")
    state = await execution.async_close()
    assert state["seen_event"] == "START"
    assert state["custom_event"]["payload"]["value"] == "hello"
    print(state)


if __name__ == "__main__":
    asyncio.run(runtime_event_data_demo())

# Expected output (keys and structure; exact trigger_type / layer_mark values are internal):
# {
#   'seen_event': 'START',
#   'custom_event': {
#     'event': 'CustomEvent',
#     'type': <trigger_type>,
#     'payload': {'from': 'START', 'value': 'hello'},
#     'layer': <layer_mark>
#   }
# }
#
# How it works:
# TriggerFlowRuntimeData carries read-only dispatch metadata on every invocation:
#   data.event        — name of the event that triggered this chunk ("START", "CustomEvent", …)
#   data.trigger_type — how the chunk was dispatched (e.g. "main", "when", "batch", …)
#   data.layer_mark   — nesting depth marker, non-zero inside sub-flows or for_each
# These are injected by the runtime, not written by user code.
# inspect_event captures data.event (== "START") then re-emits "CustomEvent"; the when()
# handler captures the same fields for that second invocation.
#
# Flow:
# async_start("hello")   [event: START]
#   |
#   v
# inspect_event  ->  state["seen_event"] = "START"
#                    async_emit("CustomEvent", {"from": "START", "value": "hello"})
#   |                                  |
#   v                                  v  [event: CustomEvent]
# (main chain done)          store_custom_event
#                            ->  state["custom_event"] = {event, type, payload, layer}
#   |
# async_close()
