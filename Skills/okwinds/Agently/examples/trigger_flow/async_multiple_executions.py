import asyncio

from agently import TriggerFlow

flow = TriggerFlow(name="async-multiple-executions")


async def task(data):
    await asyncio.sleep(0.01 * int(data.input))
    await data.async_set_state("output", {"input": data.input, "status": "done"})


flow.to(task)


async def run_one(value):
    execution = flow.create_execution()
    await execution.async_start(value)
    return await execution.async_close()


async def main():
    states = await asyncio.gather(*(run_one(i) for i in range(5)))
    assert [state["output"]["input"] for state in states] == [0, 1, 2, 3, 4]
    print(states)


asyncio.run(main())

# Stable expected key output from the declared run:
# outputs preserve input order [0, 1, 2, 3, 4], each with status "done".
#
# How it works:
# Five independent executions of the same flow are launched via asyncio.gather().
# Each execution is fully isolated — it has its own state dict and runs on its own
# asyncio task.  asyncio.sleep(0.01 * input) means higher-numbered inputs finish later,
# but gather() collects results in the original call order so the output list is [0..4].
#
# Flow (each of 5 concurrent executions):
# async_start(i)  [i = 0..4, all started concurrently]
#   |
#   v
# task  ->  await asyncio.sleep(0.01 * i)
#            state["output"] = {"input": i, "status": "done"}
#   |
# async_close()  ->  state snapshot
# asyncio.gather() collects 5 snapshots in input order
