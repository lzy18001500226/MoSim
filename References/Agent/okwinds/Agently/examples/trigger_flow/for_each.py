import asyncio

from agently import TriggerFlow

flow = TriggerFlow(name="for-each-demo")


async def double(data):
    await asyncio.sleep(0.01)
    return data.input * 2


async def store_items(data):
    await data.async_set_state("items", data.input)


flow.for_each(concurrency=2).to(double).end_for_each().to(store_items)


async def main():
    execution = flow.create_execution()
    await execution.async_start([1, 2, 3])
    state = await execution.async_close()
    assert state["items"] == [2, 4, 6]
    print(state["items"])


asyncio.run(main())

# Stable expected key output from the declared run:
# state["items"] == [2, 4, 6].
#
# How it works:
# for_each(concurrency=2).to(double).end_for_each() distributes each element of the
# input list to double in parallel (up to 2 at a time) and collects results in the
# original order.  The merged list is forwarded to store_items.
#
# Flow:
# async_start([1, 2, 3])
#   |
#   v
# for_each (concurrency=2)
#   ├── 1  ->  double  ->  2  ┐ parallel
#   ├── 2  ->  double  ->  4  ┘
#   └── 3  ->  double  ->  6    (next slot)
#   |
#   v  (collect in order: [2, 4, 6])
# store_items  ->  state["items"] = [2, 4, 6]
#   |
# async_close()
