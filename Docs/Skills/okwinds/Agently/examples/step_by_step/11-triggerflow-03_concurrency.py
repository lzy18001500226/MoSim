import asyncio
import time

from agently import TriggerFlow, TriggerFlowRuntimeData


async def triggerflow_concurrency():
    flow = TriggerFlow(name="step-03-concurrency")

    async def echo(data: TriggerFlowRuntimeData):
        await asyncio.sleep(0.05)
        return f"echo: {data.input}"

    async def store_batch(data: TriggerFlowRuntimeData):
        await data.async_set_state("batch", data.input)

    flow.batch(
        ("a", echo),
        ("b", echo),
        ("c", echo),
    ).to(store_batch)

    execution = flow.create_execution(concurrency=2)
    started_at = time.perf_counter()
    await execution.async_start("hello")
    state = await execution.async_close()
    elapsed = time.perf_counter() - started_at
    assert set(state["batch"]) == {"a", "b", "c"}
    assert elapsed >= 0.1
    print({"batch": state["batch"], "elapsed": round(elapsed, 3)})

    flow_2 = TriggerFlow(name="step-03-for-each")

    async def double(data: TriggerFlowRuntimeData):
        await asyncio.sleep(0.01)
        return data.input * 2

    async def store_items(data: TriggerFlowRuntimeData):
        await data.async_set_state("items", data.input)

    flow_2.for_each(concurrency=2).to(double).end_for_each().to(store_items)
    execution_2 = flow_2.create_execution()
    await execution_2.async_start([1, 2, 3, 4])
    state_2 = await execution_2.async_close()
    assert state_2["items"] == [2, 4, 6, 8]
    print(state_2)


if __name__ == "__main__":
    asyncio.run(triggerflow_concurrency())

# Expected output:
# {'batch': {'a', 'b', 'c'}, 'elapsed': 0.1xx}   (all three keys present; elapsed >= 0.1 s)
# {'items': [2, 4, 6, 8]}
#
# How it works:
# Two concurrency primitives are shown:
#
# 1. batch()  — runs named sibling tasks concurrently.
#    flow.batch(("a", echo), ("b", echo), ("c", echo)) launches three independent echo handlers.
#    Each gets the same input ("hello").  create_execution(concurrency=2) caps parallelism to 2,
#    so "a"+"b" start first, "c" waits, giving elapsed >= 0.1 s (two 50 ms rounds).
#    The result dict keyed by label is forwarded as data.input to store_batch.
#
# 2. for_each()  — maps a handler over each element of a list input.
#    for_each(concurrency=2).to(double).end_for_each() distributes [1,2,3,4] item by item to
#    double, running two at a time.  Results are collected in the original order.
#
# Flow (batch demo):
# async_start("hello")
#   |
#   v
# batch (concurrency=2)
#   ├── "a": echo  ->  "echo: hello"  ┐ run in parallel
#   ├── "b": echo  ->  "echo: hello"  ┘
#   └── "c": echo  ->  "echo: hello"    (waits for a slot)
#   |
#   v  (merge: {"a":..., "b":..., "c":...})
# store_batch  ->  state["batch"] = {"a", "b", "c"}
#   |
# async_close()
#
# Flow (for_each demo):
# async_start([1, 2, 3, 4])
#   |
#   v
# for_each (concurrency=2)
#   ├── 1 -> double -> 2  ┐ parallel pair
#   ├── 2 -> double -> 4  ┘
#   ├── 3 -> double -> 6  ┐ next pair
#   └── 4 -> double -> 8  ┘
#   |
#   v  (collect in order: [2, 4, 6, 8])
# store_items  ->  state["items"] = [2, 4, 6, 8]
#   |
# async_close()
