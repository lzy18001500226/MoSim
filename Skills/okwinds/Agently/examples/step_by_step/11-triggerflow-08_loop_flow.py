import asyncio

from agently import TriggerFlow, TriggerFlowRuntimeData


async def loop_flow_demo():
    flow = TriggerFlow(name="step-08-loop-flow")

    async def start_loop(data: TriggerFlowRuntimeData):
        await data.async_set_state("values", [], emit=False)
        data.emit_nowait("Loop", 0)

    async def loop_step(data: TriggerFlowRuntimeData):
        values = data.get_state("values", []) or []
        values.append(data.input)
        await data.async_set_state("values", values, emit=False)
        if data.input < 3:
            data.emit_nowait("Loop", data.input + 1)
        else:
            await data.async_set_state("done", {"last": data.input, "count": len(values)})

    flow.to(start_loop)
    flow.when("Loop").to(loop_step)

    execution = flow.create_execution(auto_close=False)
    await execution.async_start("start")
    state = await execution.async_close()
    assert state["values"] == [0, 1, 2, 3]
    print(state["done"])


if __name__ == "__main__":
    asyncio.run(loop_flow_demo())

# Expected output:
# {'last': 3, 'count': 4}          (state["values"] == [0, 1, 2, 3])
#
# How it works:
# emit_nowait("Loop", value) fires an event synchronously without yielding, so the "Loop"
# handler is queued immediately.  loop_step reads state["values"], appends the current count,
# and re-emits "Loop" with count+1 — until count reaches 3, at which point it stops and
# writes state["done"].
# async_set_state(..., emit=False) suppresses the built-in auto-emit that would otherwise
# dispatch a state-change event for every write, which would double-trigger the "Loop" handler.
# create_execution(auto_close=False) keeps the execution open until all Loop iterations finish.
#
# Flow:
# async_start("start")
#   |
#   v
# start_loop  ->  state["values"] = []
#                 emit_nowait("Loop", 0)
#   |                        |
#   v                        v  [Loop, input=0]
# (main done)           loop_step  ->  values=[0], emit_nowait("Loop", 1)
#                            |
#                            v  [Loop, input=1]
#                       loop_step  ->  values=[0,1], emit_nowait("Loop", 2)
#                            |
#                            v  [Loop, input=2]
#                       loop_step  ->  values=[0,1,2], emit_nowait("Loop", 3)
#                            |
#                            v  [Loop, input=3]
#                       loop_step  ->  values=[0,1,2,3], input>=3: stop
#                                      state["done"] = {"last": 3, "count": 4}
#   |
# async_close()  ->  prints state["done"]
