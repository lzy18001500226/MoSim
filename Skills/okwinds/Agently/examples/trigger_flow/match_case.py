import asyncio

from agently import TriggerFlow

flow = TriggerFlow(name="match-case-demo")


async def choose_priority(data):
    return data.input.get("priority", "unknown")


async def store_result(data):
    await data.async_set_state("result", data.input)


(
    flow.to(choose_priority)
    .match()
    .case("low")
    .to(lambda _: "queue")
    .case("high")
    .to(lambda _: "run-now")
    .case_else()
    .to(lambda _: "review")
    .end_match()
    .to(store_result)
)


async def main():
    execution = flow.create_execution()
    await execution.async_start({"priority": "high"})
    state = await execution.async_close()
    assert state["result"] == "run-now"
    print(state["result"])


asyncio.run(main())

# Stable expected key output from the declared run:
# state["result"] == "run-now" for priority "high".
#
# How it works:
# choose_priority extracts the "priority" key from input and returns its value as a
# string.  match/case dispatches based on that string: case("high") matches and the
# lambda returns "run-now".  end_match() merges all arms back to a single continuation.
#
# Flow:
# async_start({"priority": "high"})
#   |
#   v
# choose_priority  ->  "high"
#   |
#   [case "low"] no   [case "high"] yes   [case_else] skip
#                            |
#                            v
#                     lambda _  ->  "run-now"
#                            |
#                            v  (end_match merges)
#                     store_result  ->  state["result"] = "run-now"
#   |
# async_close()
