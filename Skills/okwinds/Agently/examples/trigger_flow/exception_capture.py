import asyncio

from agently import TriggerFlow

flow = TriggerFlow(name="exception-capture-demo")


async def fail(data):
    await data.async_set_state("started", True)
    raise RuntimeError("demo failure")


flow.to(fail)


async def main():
    execution = flow.create_execution()
    try:
        await execution.async_start("demo")
    except RuntimeError as error:
        await execution.async_set_state("error", str(error), emit=False)
    state = await execution.async_close()
    assert state["started"] is True
    assert state["error"] == "demo failure"
    print(state)


asyncio.run(main())

# Stable expected key output from the declared run:
# state["started"] is True and state["error"] == "demo failure" after the chunk exception is captured.
#
# How it works:
# fail() raises RuntimeError after writing state["started"]=True.  The caller wraps
# async_start() in a try/except and writes state["error"] via execution.async_set_state()
# (the external form of the same API).  async_close() then returns the complete snapshot
# including both keys set before and after the exception.
#
# Flow:
# async_start("demo")
#   |
#   v
# fail  ->  state["started"] = True
#            raise RuntimeError("demo failure")   <- caught by caller
#   |
# [except RuntimeError]
# execution.async_set_state("error", "demo failure")
#   |
# async_close()  ->  {"started": True, "error": "demo failure"}
