import asyncio
from typing import Any, cast

from agently import TriggerFlow

flow = TriggerFlow(name="runtime-stream-demo")


async def stream_steps(data):
    await data.async_put_into_stream({"stage": "start", "input": data.input})
    await data.async_put_into_stream({"stage": "finish", "input": data.input})
    await data.async_set_state("done", True)


flow.to(stream_steps)


async def main():
    execution = flow.create_execution(auto_close=False)
    await execution.async_start("Agently")
    close_task = asyncio.create_task(execution.async_close())
    items = [item async for item in execution.get_async_runtime_stream(timeout=None)]
    await close_task
    assert [cast(dict[str, Any], item)["stage"] for item in items] == [
        "start",
        "finish",
    ]
    assert execution.result.get_state("done") is True
    print({"items": items, "meta": execution.result.get_meta()})


asyncio.run(main())

# Stable expected key output from the declared run:
# runtime stream emits stages ["start", "finish"] and execution result state has done=True.
#
# How it works:
# stream_steps puts two dicts into the execution's stream channel via
# async_put_into_stream.  get_async_runtime_stream(timeout=None) is an async generator
# that yields items as they arrive and exits when the execution closes.
# async_close() must run concurrently (via asyncio.create_task) so the generator is
# not blocked waiting for close.
#
# Flow:
# async_start("Agently")
#   |
#   v
# stream_steps  ->  async_put_into_stream({"stage":"start",...})
#                   async_put_into_stream({"stage":"finish",...})
#                   state["done"] = True
#   |
# asyncio.create_task(async_close())                <- concurrent
# [async for item in get_async_runtime_stream()]    ->  [{"stage":"start",...}, {"stage":"finish",...}]
#   |
# await close_task  ->  asserts state["done"] is True
