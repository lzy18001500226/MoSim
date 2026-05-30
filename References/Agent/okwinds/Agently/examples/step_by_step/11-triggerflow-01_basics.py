import asyncio

from agently import TriggerFlow, TriggerFlowRuntimeData


async def triggerflow_basics():
    flow = TriggerFlow(name="step-01-basics")

    async def greet(data: TriggerFlowRuntimeData):
        await data.async_set_state("greeting", f"Hello, {data.input}")
        return data.input

    async def finish(data: TriggerFlowRuntimeData):
        await data.async_set_state("finished", True)

    flow.to(greet).to(finish)

    execution = flow.create_execution()
    await execution.async_start("Agently")
    state = await execution.async_close()
    assert state["greeting"] == "Hello, Agently"
    print(state)


if __name__ == "__main__":
    asyncio.run(triggerflow_basics())

# Expected output:
# {'greeting': 'Hello, Agently', 'finished': True}
#
# How it works:
# flow.to(greet).to(finish) builds a two-step linear chain.
# Each chunk receives TriggerFlowRuntimeData and writes to the shared state dict
# via async_set_state().  async_close() returns the final state snapshot.
#
# Flow:
# async_start("Agently")
#   |
#   v
# greet  ->  state["greeting"] = "Hello, Agently"  (returns data.input)
#   |
#   v
# finish ->  state["finished"] = True
#   |
#   v
# async_close() -> {'greeting': 'Hello, Agently', 'finished': True}
