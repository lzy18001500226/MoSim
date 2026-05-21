import asyncio

from agently import TriggerFlow, TriggerFlowRuntimeData


async def triggerflow_when_demo():
    flow = TriggerFlow(name="step-02-when")

    async def prepare(data: TriggerFlowRuntimeData):
        await data.async_set_state("flag", "ready")
        await data.async_emit("Prepared", {"flag": "ready"})

    async def route(data: TriggerFlowRuntimeData):
        await data.async_set_state("when_payload", data.input)

    flow.to(prepare)
    flow.when("Prepared").to(route)

    execution = flow.create_execution(auto_close=False)
    await execution.async_start(None)
    state = await execution.async_close()
    assert state["when_payload"] == {"flag": "ready"}
    print("[when]", state)


async def triggerflow_if_condition_demo():
    flow = TriggerFlow(name="step-02-if-condition")

    async def score(data: TriggerFlowRuntimeData):
        return {"score": 82}

    async def store_grade(data: TriggerFlowRuntimeData):
        await data.async_set_state("grade", data.input)

    (
        flow.to(score)
        .if_condition(lambda data: data.input["score"] >= 90)
        .to(lambda _: "A")
        .elif_condition(lambda data: data.input["score"] >= 80)
        .to(lambda _: "B")
        .else_condition()
        .to(lambda _: "C")
        .end_condition()
        .to(store_grade)
    )

    execution = flow.create_execution()
    await execution.async_start(None)
    state = await execution.async_close()
    assert state["grade"] == "B"
    print("[if]", state)


async def triggerflow_match_demo():
    flow = TriggerFlow(name="step-02-match")

    async def store_result(data: TriggerFlowRuntimeData):
        await data.async_set_state("route", data.input)

    (
        flow.to(lambda _: "medium")
        .match()
        .case("low")
        .to(lambda _: "priority: low")
        .case("medium")
        .to(lambda _: "priority: medium")
        .case("high")
        .to(lambda _: "priority: high")
        .case_else()
        .to(lambda _: "priority: unknown")
        .end_match()
        .to(store_result)
    )

    execution = flow.create_execution()
    await execution.async_start(None)
    state = await execution.async_close()
    assert state["route"] == "priority: medium"
    print("[match]", state)


async def main():
    await triggerflow_when_demo()
    await triggerflow_if_condition_demo()
    await triggerflow_match_demo()


if __name__ == "__main__":
    asyncio.run(main())

# Expected output:
# [when]  {'flag': 'ready', 'when_payload': {'flag': 'ready'}}
# [if]    {'grade': 'B'}
# [match] {'route': 'priority: medium'}
#
# How it works:
# Three independent branching mechanisms are shown:
#
# 1. when()  — event-based routing.  prepare emits "Prepared"; flow.when("Prepared").to(route)
#    registers a handler that fires when that event is dispatched.  create_execution(auto_close=False)
#    is needed because the execution has no pending main-chain work after prepare runs; without it
#    the runtime would close before the event handler is picked up.
#
# 2. if_condition / elif_condition / else_condition / end_condition  — inline branching.
#    score returns {"score": 82}, so the >= 80 arm runs and passes "B" to store_grade.
#    end_condition() merges all arms back to a single continuation.
#
# 3. match / case / case_else / end_match  — value-dispatch branching.
#    The upstream lambda returns "medium", so case("medium") fires; end_match() merges.
#
# Flow (when demo):
# async_start(None)
#   |
#   v
# prepare  ->  state["flag"] = "ready"
#              async_emit("Prepared", {"flag": "ready"})
#   |                         |
#   v                         v  [event: Prepared]
# (main done)             route  ->  state["when_payload"] = {"flag": "ready"}
#   |
# async_close()
#
# Flow (if_condition demo):
# async_start(None)
#   |
#   v
# score  ->  {"score": 82}
#   |
#   [>= 90?] No  -> [>= 80?] Yes
#                        |
#                        v
#                   lambda "B"
#                        |
#                        v  (end_condition merges)
#                   store_grade  ->  state["grade"] = "B"
#   |
# async_close()
#
# Flow (match demo):
# async_start(None)
#   |
#   v
# lambda "medium"
#   |
#   [case "low"] no  [case "medium"] yes  [case "high"] no
#                            |
#                            v
#                     lambda "priority: medium"
#                            |
#                            v  (end_match merges)
#                     store_result  ->  state["route"] = "priority: medium"
#   |
# async_close()
