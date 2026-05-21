import asyncio

from agently import TriggerFlow

flow = TriggerFlow(name="nowait-loop-demo")


async def start_loop(data):
    await data.async_set_state("values", [], emit=False)
    data.emit_nowait("TICK", 1)


async def on_tick(data):
    values = data.get_state("values", []) or []
    values.append(data.input)
    await data.async_set_state("values", values, emit=False)
    if data.input < 3:
        data.emit_nowait("TICK", data.input + 1)
    else:
        await data.async_set_state("summary", {"count": len(values), "last": values[-1]})


flow.to(start_loop)
flow.when("TICK").to(on_tick)


async def main():
    execution = flow.create_execution(auto_close=False)
    await execution.async_start(None)
    state = await execution.async_close()
    assert state["values"] == [1, 2, 3]
    assert state["summary"] == {"count": 3, "last": 3}
    print(state["summary"])


asyncio.run(main())

# Stable expected key output from the declared run:
# state["values"] == [1, 2, 3] and state["summary"] == {"count": 3, "last": 3}.
#
# How it works:
# start_loop fires "TICK" with value 1 via emit_nowait.  on_tick appends the value and
# re-emits "TICK" with value+1 until value >= 3, at which point it writes state["summary"].
# async_set_state(..., emit=False) suppresses the built-in auto-emit that would otherwise
# double-fire the "TICK" handler on every state write.
#
# Flow:
# async_start(None)
#   |
#   v
# start_loop  ->  state["values"] = [],  emit_nowait("TICK", 1)
#   |                          |
#   v                          v  [TICK, 1]
# (main done)            on_tick  ->  values=[1],  emit_nowait("TICK", 2)
#                              |
#                              v  [TICK, 2]
#                        on_tick  ->  values=[1,2],  emit_nowait("TICK", 3)
#                              |
#                              v  [TICK, 3]
#                        on_tick  ->  values=[1,2,3],  input>=3: stop
#                                     state["summary"] = {"count":3, "last":3}
