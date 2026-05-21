import asyncio

from agently import TriggerFlow

flow = TriggerFlow(name="nested-for-demo")


async def make_groups(data):
    return [[f"{data.input}-a", f"{data.input}-b"], [f"{data.input}-c"]]


async def expand_group(data):
    return data.input


async def mark_item(data):
    return {"item": data.input, "ready": True}


async def store_nested(data):
    await data.async_set_state("nested", data.input)


(
    flow.to(make_groups)
    .for_each(concurrency=2)
    .to(expand_group)
    .for_each(concurrency=2)
    .to(mark_item)
    .end_for_each()
    .end_for_each()
    .to(store_nested)
)


async def main():
    execution = flow.create_execution()
    await execution.async_start("demo")
    state = await execution.async_close()
    assert state["nested"] == [
        [{"item": "demo-a", "ready": True}, {"item": "demo-b", "ready": True}],
        [{"item": "demo-c", "ready": True}],
    ]
    print(state["nested"])


asyncio.run(main())

# Stable expected key output from the declared run:
# nested groups contain demo-a, demo-b, and demo-c items, each with ready=True.
#
# How it works:
# make_groups produces a 2-D list: [["demo-a","demo-b"], ["demo-c"]].
# The outer for_each iterates over groups (2 groups); expand_group passes each group
# through unchanged.  The inner for_each iterates over the items in each group and
# applies mark_item.  end_for_each() pair nests the collection: results are
# [[{item:"demo-a",...}, {item:"demo-b",...}], [{item:"demo-c",...}]].
#
# Flow:
# async_start("demo")
#   |
#   v
# make_groups  ->  [["demo-a","demo-b"], ["demo-c"]]
#   |
#   v
# for_each (outer, concurrency=2)  -- iterates over groups
#   ├── ["demo-a","demo-b"]  ->  expand_group  ->  ["demo-a","demo-b"]
#   │     for_each (inner, concurrency=2)
#   │       ├── "demo-a"  ->  mark_item  ->  {"item":"demo-a","ready":True}
#   │       └── "demo-b"  ->  mark_item  ->  {"item":"demo-b","ready":True}
#   └── ["demo-c"]          ->  expand_group  ->  ["demo-c"]
#         for_each (inner)
#           └── "demo-c"  ->  mark_item  ->  {"item":"demo-c","ready":True}
#   |
# store_nested  ->  state["nested"] = [[{...},{...}],[{...}]]
