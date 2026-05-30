from agently import TriggerFlow, TriggerFlowRuntimeData


async def init(data: TriggerFlowRuntimeData):
    await data.async_set_state("initial_number", data.input)
    return data.input


def make_multiplier(multiplier: int):
    async def multiply(data: TriggerFlowRuntimeData):
        return data.input * multiplier

    return multiply


async def summarize(data: TriggerFlowRuntimeData):
    await data.async_set_state(
        "response",
        {
            "group_1": data.input["first"],
            "group_2": data.input["second"] + data.input["third"],
            "initial_number": data.get_state("initial_number"),
        },
    )


def dump_flow():
    flow = TriggerFlow(name="rest-api-triggerflow-demo")
    (
        flow.to(init)
        .batch(
            ("first", make_multiplier(1)),
            ("second", make_multiplier(2)),
            ("third", make_multiplier(3)),
        )
        .to(summarize)
    )
    return flow


async def run_flow(value: int):
    execution = dump_flow().create_execution()
    await execution.async_start(value)
    await execution.async_close()
    result = execution.result
    return result.get_state("response")

# Stable expected key output from the declared run:
# run_flow(3) returns {"group_1": 3, "group_2": 15, "initial_number": 3}.
#
# How it works:
# - dump_flow() builds a TriggerFlow with an init chunk, a three-way batch, and a summarize chunk.
# - run_flow(value) starts and closes one execution, then returns response from execution state.
# - This module is imported by restful_api_server/server.py for HTTP exposure.
#
# ASCII flow:
# start/input
#   |
#   v
# TriggerFlow chunks / branches
#   |
#   v
# async_close() -> close snapshot / runtime stream assertions
