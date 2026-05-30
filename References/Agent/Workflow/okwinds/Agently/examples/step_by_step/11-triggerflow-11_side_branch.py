import asyncio

from agently import TriggerFlow, TriggerFlowRuntimeData


async def triggerflow_side_branch_demo():
    flow = TriggerFlow(name="step-11-side-branch")

    async def main_task(data: TriggerFlowRuntimeData):
        return f"main: {data.input}"

    async def side_task(data: TriggerFlowRuntimeData):
        await data.async_set_state("side", f"side saw {data.input}")

    async def store_main(data: TriggerFlowRuntimeData):
        await data.async_set_state("main", data.input)

    flow.to(main_task).side_branch(side_task).to(store_main)

    execution = flow.create_execution()
    await execution.async_start("hello")
    state = await execution.async_close()
    assert state["main"] == "main: hello"
    assert state["side"] == "side saw main: hello"
    print(state)


if __name__ == "__main__":
    asyncio.run(triggerflow_side_branch_demo())

# Expected output:
# {'main': 'main: hello', 'side': 'side saw main: hello'}
#
# How it works:
# side_branch(side_task) attaches a parallel observer to the output of main_task.
# side_task receives main_task's return value ("main: hello") as data.input and runs
# concurrently with the rest of the main chain.  The main chain continues to store_main
# immediately, without waiting for side_task to finish.  side_task does not produce a
# return value that feeds into the main chain — it is a fire-and-observe tap, not a fork.
# Both chunks share the same execution state, so side writes are visible in the close snapshot.
#
# Flow:
# async_start("hello")
#   |
#   v
# main_task  ->  "main: hello"
#   |                   |
#   |           [side_branch]
#   |                   v  (concurrent, does not block main chain)
#   v           side_task  ->  state["side"] = "side saw main: hello"
# store_main  ->  state["main"] = "main: hello"
#   |
# async_close()  ->  {'main': 'main: hello', 'side': 'side saw main: hello'}
