import asyncio

from agently import TriggerFlow

flow = TriggerFlow(name="quick-named-chunk")


@flow.chunk("normalize-input")
async def normalize(data):
    return str(data.input).strip().lower()


async def store(data):
    await data.async_set_state("normalized", data.input)


flow.to(normalize).to(store)


async def main():
    execution = flow.create_execution()
    await execution.async_start("  Agently  ")
    state = await execution.async_close()
    assert state["normalized"] == "agently"
    print(state["normalized"])


asyncio.run(main())

# Stable expected key output from the declared run:
# state["normalized"] == "agently".
#
# How it works:
# @flow.chunk("normalize-input") is a decorator shorthand that both defines the async
# handler and registers it with an explicit name in the flow's chunk registry.
# The name is used in blueprints and Mermaid diagrams instead of the function's
# __name__.  The rest of the chain (flow.to(normalize).to(store)) is identical to
# registering without a decorator.
#
# Flow:
# async_start("  Agently  ")
#   |
#   v
# normalize  ("normalize-input")  ->  "agently"   (strip + lower)
#   |
#   v
# store  ->  state["normalized"] = "agently"
#   |
# async_close()  ->  "agently"
