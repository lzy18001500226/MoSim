import asyncio

from agently import TriggerFlow


async def normalize(data):
    return str(data.input).strip().lower()


async def store(data):
    await data.async_set_state("normalized", data.input)


def build_flow():
    flow = TriggerFlow(name="save-load-blueprint-demo")
    flow.register_chunk_handler(normalize)
    flow.register_chunk_handler(store)
    flow.to(normalize).to(store)
    return flow


async def run(flow, value):
    execution = flow.create_execution()
    await execution.async_start(value)
    return await execution.async_close()


async def main():
    source_flow = build_flow()
    blueprint = source_flow.save_blueprint()

    restored_flow = TriggerFlow(name="restored-blueprint-demo")
    restored_flow.register_chunk_handler(normalize)
    restored_flow.register_chunk_handler(store)
    restored_flow.load_blueprint(blueprint)

    state = await run(restored_flow, "  Agently  ")
    assert state["normalized"] == "agently"
    print(state)


asyncio.run(main())

# Stable expected key output from the declared run:
# restored blueprint run closes with state["normalized"] == "agently".
#
# How it works:
# source_flow.save_blueprint() serializes the routing graph to a plain dict.
# restored_flow.register_chunk_handler(normalize) / register_chunk_handler(store)
# re-links function objects by name before load_blueprint() reconstructs the graph.
# The restored flow runs identically to the source.
# Compare with 11-triggerflow-05_blueprint.py in step_by_step which covers the same
# concept; this version shows the standalone module pattern (build_flow / run helpers).
#
# Flow:
# build_flow()  ->  source_flow.to(normalize).to(store)
#   |
# source_flow.save_blueprint()  ->  blueprint dict  (topology, no function bodies)
#   |
# restored_flow.register_chunk_handler(normalize, store)
# restored_flow.load_blueprint(blueprint)
#   |
# async_start("  Agently  ")
#   |
#   v
# normalize  ->  "agently"
#   |
#   v
# store  ->  state["normalized"] = "agently"
#   |
# async_close()  ->  {"normalized": "agently"}
