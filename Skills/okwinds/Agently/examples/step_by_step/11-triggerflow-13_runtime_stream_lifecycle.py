import asyncio

from agently import TriggerFlow, TriggerFlowRuntimeData


async def triggerflow_runtime_stream_close_demo():
    flow = TriggerFlow(name="step-13-runtime-stream-close")

    async def stream_steps(data: TriggerFlowRuntimeData):
        await data.async_put_into_stream("step-1")
        await data.async_put_into_stream("step-2")
        await data.async_set_state("done", True)

    flow.to(stream_steps)

    execution = flow.create_execution(auto_close=False)
    await execution.async_start("start")
    close_task = asyncio.create_task(execution.async_close())
    events = [event async for event in execution.get_async_runtime_stream(timeout=None)]
    state = await close_task
    assert events == ["step-1", "step-2"]
    assert state["done"] is True
    print({"events": events, "state": state})


if __name__ == "__main__":
    asyncio.run(triggerflow_runtime_stream_close_demo())

# Expected output:
# {'events': ['step-1', 'step-2'], 'state': {'done': True}}
#
# How it works:
# This example focuses on the ordering guarantee between stream consumption and close.
# async_close() is launched as a concurrent task so the stream generator is not blocked.
# The async-for loop drives stream consumption; when the execution closes the generator
# exits and the await close_task call returns the final state snapshot.
# Stream items are always delivered before the close snapshot is taken — the state dict
# in the printout reflects all async_set_state() calls that occurred during streaming.
#
# Compare with 11-triggerflow-10: that example prints the stream events together with
# execution metadata; this one isolates the ordering guarantee (events list + state in
# one dict) to make the lifecycle boundary explicit.
#
# Flow:
# async_start("start")
#   |
#   v
# stream_steps  ->  async_put_into_stream("step-1")
#                   async_put_into_stream("step-2")
#                   state["done"] = True
#   |
# asyncio.create_task(async_close())   ← concurrent
#   |
# [async for event in get_async_runtime_stream()]  ->  ['step-1', 'step-2']
#   |
# state = await close_task  ->  {'done': True}
