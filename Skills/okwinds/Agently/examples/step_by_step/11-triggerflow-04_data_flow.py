import asyncio

from agently import TriggerFlow, TriggerFlowRuntimeData


async def triggerflow_state_flow():
    flow = TriggerFlow(name="step-04-state-flow")

    async def prepare_user(data: TriggerFlowRuntimeData):
        await data.async_set_state("user", {"id": "u-001", "role": "admin"})
        return data.input

    async def prepare_env(data: TriggerFlowRuntimeData):
        await data.async_set_state("env", {"name": "prod"})
        return data.input

    async def summarize(data: TriggerFlowRuntimeData):
        await data.async_set_state(
            "summary",
            {
                "input": data.input,
                "user": data.get_state("user"),
                "env": data.get_state("env"),
            },
        )

    flow.to(prepare_user).to(prepare_env).to(summarize)

    execution = flow.create_execution()
    await execution.async_start("deploy")
    state = await execution.async_close()
    assert state["summary"]["user"]["id"] == "u-001"
    print(state["summary"])


if __name__ == "__main__":
    asyncio.run(triggerflow_state_flow())

# Expected output:
# {'input': 'deploy', 'user': {'id': 'u-001', 'role': 'admin'}, 'env': {'name': 'prod'}}
#
# How it works:
# State is a flat dict shared across the entire execution.  Any chunk can read values
# written by earlier chunks via data.get_state("key").  prepare_user and prepare_env
# each write one key, then summarize reads both and assembles a combined snapshot.
# This pattern avoids threading intermediate results through return values when multiple
# upstream chunks each contribute one piece of context.
#
# Flow:
# async_start("deploy")
#   |
#   v
# prepare_user  ->  state["user"] = {"id": "u-001", "role": "admin"}  (returns data.input)
#   |
#   v
# prepare_env   ->  state["env"]  = {"name": "prod"}                  (returns data.input)
#   |
#   v
# summarize     ->  reads state["user"] + state["env"] via data.get_state()
#                   state["summary"] = {"input": "deploy", "user": {...}, "env": {...}}
#   |
# async_close() ->  prints state["summary"]
