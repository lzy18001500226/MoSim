import asyncio

from agently import TriggerFlow

flow = TriggerFlow(name="when-demo")


async def prepare(data):
    await data.async_set_state("request", {"topic": data.input, "status": "prepared"})
    await data.async_emit("REQUEST_PREPARED", {"topic": data.input})


async def route_prepared(data):
    await data.async_set_state("route", {"event": data.event, "payload": data.input})


flow.to(prepare)
flow.when("REQUEST_PREPARED").to(route_prepared)


async def main():
    execution = flow.create_execution(auto_close=False)
    await execution.async_start("refund")
    state = await execution.async_close()
    assert state["request"]["status"] == "prepared"
    assert state["route"]["payload"] == {"topic": "refund"}
    print(state)


asyncio.run(main())

# Stable expected key output from the declared run:
# request.status == "prepared" and route.payload == {"topic": "refund"}.
#
# How it works:
# prepare stores state["request"] then calls async_emit("REQUEST_PREPARED", payload).
# flow.when("REQUEST_PREPARED").to(route_prepared) registers a handler that fires when
# that event is dispatched.  auto_close=False is needed because without it the runtime
# would close the execution before the event handler has a chance to run.
#
# Flow:
# async_start("refund")
#   |
#   v
# prepare  ->  state["request"] = {"topic": "refund", "status": "prepared"}
#              async_emit("REQUEST_PREPARED", {"topic": "refund"})
#   |                             |
#   v                             v  [event: REQUEST_PREPARED]
# (main done)               route_prepared
#                           ->  state["route"] = {"event": "REQUEST_PREPARED", "payload": {"topic":"refund"}}
#   |
# async_close()
