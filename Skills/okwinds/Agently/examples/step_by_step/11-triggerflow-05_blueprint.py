import asyncio

from agently import TriggerFlow, TriggerFlowRuntimeData


async def upper(data: TriggerFlowRuntimeData):
    return str(data.input).upper()


async def store(data: TriggerFlowRuntimeData):
    await data.async_set_state("output", data.input)


def build_flow():
    flow = TriggerFlow(name="step-05-blueprint-source")
    flow.register_chunk_handler(upper)
    flow.register_chunk_handler(store)
    flow.to(upper).to(store)
    return flow


async def run_flow(flow: TriggerFlow, value: str):
    execution = flow.create_execution()
    await execution.async_start(value)
    return await execution.async_close()


async def triggerflow_blueprint():
    source_flow = build_flow()
    blueprint = source_flow.save_blueprint()

    restored_flow = TriggerFlow(name="step-05-blueprint-restored")
    restored_flow.register_chunk_handler(upper)
    restored_flow.register_chunk_handler(store)
    restored_flow.load_blueprint(blueprint)

    state = await run_flow(restored_flow, "agently")
    assert state["output"] == "AGENTLY"
    print(state)


if __name__ == "__main__":
    asyncio.run(triggerflow_blueprint())

# Expected output:
# {'output': 'AGENTLY'}
#
# How it works:
# save_blueprint() serializes the flow's routing graph to a plain dict (no function objects).
# load_blueprint() reconstructs the same routing on a different TriggerFlow instance.
# Because the blueprint stores handlers by name, the target flow must call
# register_chunk_handler() for each referenced function before loading — that re-links
# the name to the actual callable.
# This lets you persist, transmit, or version-control the flow topology independently
# of the Python module that defines the handler bodies.
#
# Flow:
# source_flow.to(upper).to(store)
#   |
# save_blueprint()  ->  {"nodes": [...], "edges": [...]}   (topology only, no functions)
#   |
# restored_flow.register_chunk_handler(upper)
# restored_flow.register_chunk_handler(store)
# restored_flow.load_blueprint(blueprint)
#   |
# async_start("agently")
#   |
#   v
# upper  ->  "AGENTLY"
#   |
#   v
# store  ->  state["output"] = "AGENTLY"
#   |
# async_close()  ->  {'output': 'AGENTLY'}
