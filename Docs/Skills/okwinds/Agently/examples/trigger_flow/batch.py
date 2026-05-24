import asyncio

from agently import TriggerFlow

flow = TriggerFlow(name="batch-demo")


def make_handler(label):
    async def handle(data):
        await asyncio.sleep(0.01)
        return f"{label}:{data.input}"

    return handle


async def store_batch(data):
    await data.async_set_state("batch", data.input)


flow.batch(
    ("draft", make_handler("draft")),
    ("review", make_handler("review")),
    ("ship", make_handler("ship")),
    concurrency=2,
).to(store_batch)


async def main():
    execution = flow.create_execution()
    await execution.async_start("demo")
    state = await execution.async_close()
    assert state["batch"] == {
        "draft": "draft:demo",
        "review": "review:demo",
        "ship": "ship:demo",
    }
    print(state["batch"])


asyncio.run(main())

# Stable expected key output from the declared run:
# batch == {"draft": "draft:demo", "review": "review:demo", "ship": "ship:demo"}.
#
# How it works:
# flow.batch(("draft", h), ("review", h), ("ship", h), concurrency=2) runs three
# named handlers in parallel with at most 2 running simultaneously.  Each receives
# the same input ("demo") and returns a labeled string.  The results are merged into
# a dict keyed by label and forwarded to store_batch.
#
# Flow:
# async_start("demo")
#   |
#   v
# batch (concurrency=2)
#   ├── "draft":  handler  ->  "draft:demo"   ┐ parallel
#   ├── "review": handler  ->  "review:demo"  ┘
#   └── "ship":   handler  ->  "ship:demo"      (waits for slot)
#   |
#   v  (merge: {"draft":..., "review":..., "ship":...})
# store_batch  ->  state["batch"] = {"draft":"draft:demo", ...}
#   |
# async_close()
