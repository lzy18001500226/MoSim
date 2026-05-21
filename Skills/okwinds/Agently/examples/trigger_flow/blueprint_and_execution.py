import asyncio

from agently import TriggerFlow, TriggerFlowBlueprint

blueprint = TriggerFlowBlueprint(name="blueprint-event-demo")


async def on_ping(data):
    await data.async_set_state("last_ping", data.input)


blueprint.add_event_handler("PING", on_ping)
flow = TriggerFlow(blueprint=blueprint, name="blueprint-execution-demo")


async def run_one(value):
    execution = flow.create_execution(auto_close=False)
    execution.emit_nowait("PING", value)
    return await execution.async_close()


async def main():
    first, second = await asyncio.gather(run_one("one"), run_one("two"))
    assert first["last_ping"] == "one"
    assert second["last_ping"] == "two"
    print({"first": first["last_ping"], "second": second["last_ping"]})


asyncio.run(main())

# Stable expected key output from the declared run:
# first execution keeps last_ping "one" and second execution keeps last_ping "two".
#
# How it works:
# TriggerFlowBlueprint defines a reusable event handler graph without being tied to
# a specific flow instance.  TriggerFlow(blueprint=...) instantiates a flow from it.
# Each create_execution() call produces an isolated execution with its own state —
# "one" and "two" stay in separate state dicts even though they run concurrently.
#
# Flow (two concurrent executions):
# Execution A: emit_nowait("PING", "one")  ->  on_ping  ->  state["last_ping"] = "one"
# Execution B: emit_nowait("PING", "two")  ->  on_ping  ->  state["last_ping"] = "two"
# asyncio.gather() runs both; first.last_ping=="one", second.last_ping=="two"
