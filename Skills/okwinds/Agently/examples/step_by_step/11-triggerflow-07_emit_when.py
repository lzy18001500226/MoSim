import asyncio

from agently import TriggerFlow, TriggerFlowRuntimeData


async def emit_when_demo():
    flow = TriggerFlow(name="step-07-emit-when")

    async def planner(data: TriggerFlowRuntimeData):
        await data.async_emit("Plan.Read", {"task": "read"})
        await data.async_emit("Plan.Write", {"task": "write"})

    async def reader(data: TriggerFlowRuntimeData):
        await data.async_set_state("read_result", f"read: {data.input['task']}")

    async def writer(data: TriggerFlowRuntimeData):
        await data.async_set_state("write_result", f"write: {data.input['task']}")

    async def summarize(data: TriggerFlowRuntimeData):
        await data.async_set_state(
            "summary",
            {
                "read": data.get_state("read_result"),
                "write": data.get_state("write_result"),
            },
        )

    flow.to(planner).to(summarize)
    flow.when("Plan.Read").to(reader)
    flow.when("Plan.Write").to(writer)

    execution = flow.create_execution(auto_close=False)
    await execution.async_start("go")
    state = await execution.async_close()
    assert state["read_result"] == "read: read"
    assert state["write_result"] == "write: write"
    print(state)


if __name__ == "__main__":
    asyncio.run(emit_when_demo())

# Expected output:
# {'read_result': 'read: read', 'write_result': 'write: write',
#  'summary': {'read': 'read: read', 'write': 'write: write'}}
#
# How it works:
# planner emits two different events in one handler call, each dispatching an independent
# when() branch concurrently.  The main chain (planner -> summarize) runs sequentially, but
# summarize calls data.get_state() so it sees writes made by reader and writer even though
# those branches run concurrently alongside it — all three share the same execution state.
# create_execution(auto_close=False) is required because the execution must stay open until
# both when() branches have written their state keys before async_close() is called.
#
# Flow:
# async_start("go")
#   |
#   v
# planner  ->  async_emit("Plan.Read",  {"task": "read"})
#              async_emit("Plan.Write", {"task": "write"})
#   |                  |                        |
#   v                  v  [Plan.Read]           v  [Plan.Write]
# summarize         reader                   writer
# (waits for     ->  state["read_result"]  ->  state["write_result"]
#  branches)         = "read: read"            = "write: write"
#   |
#   v
# state["summary"] = {"read": "read: read", "write": "write: write"}
#   |
# async_close()
