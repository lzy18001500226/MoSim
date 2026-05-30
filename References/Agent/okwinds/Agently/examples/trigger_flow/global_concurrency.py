import asyncio
import time

from agently import TriggerFlow

flow = TriggerFlow(name="global-concurrency-demo")


async def handle(data):
    await asyncio.sleep(0.05)
    return data.input


async def store_batch(data):
    await data.async_set_state("batch", data.input)


flow.batch(
    ("a", handle),
    ("b", handle),
    ("c", handle),
    ("d", handle),
).to(store_batch)


async def main():
    execution = flow.create_execution(concurrency=2)
    started_at = time.perf_counter()
    await execution.async_start("demo")
    state = await execution.async_close()
    elapsed = time.perf_counter() - started_at
    assert set(state["batch"]) == {"a", "b", "c", "d"}
    assert elapsed >= 0.1
    print({"batch": state["batch"], "elapsed": round(elapsed, 3)})


asyncio.run(main())

# Stable expected key output from the declared run:
# state["batch"] has keys a, b, c, d and each value is "demo".
#
# How it works:
# create_execution(concurrency=2) sets the execution-level global concurrency cap.
# The batch has four handlers but only two run at a time; four handlers at 50ms each
# need two rounds, so elapsed >= 0.1 s.  This is the same parameter as in step-by-step
# 11-triggerflow-03, but here the concurrency is set on the execution rather than inside
# the batch() call to show that both produce the same throttling effect.
#
# Flow:
# async_start("demo")
#   |
#   v
# batch (global concurrency=2 from execution)
#   ├── "a": handle  ->  "demo"  ┐ round 1 (parallel)
#   ├── "b": handle  ->  "demo"  ┘
#   ├── "c": handle  ->  "demo"  ┐ round 2 (parallel, after round 1 finishes)
#   └── "d": handle  ->  "demo"  ┘   elapsed >= 0.1 s
#   |
# store_batch  ->  state["batch"] = {"a":"demo", "b":"demo", "c":"demo", "d":"demo"}
#   |
# async_close()
