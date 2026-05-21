# pyright: reportMissingImports=false

import asyncio

from agently import Agently, TriggerFlow, TriggerFlowRuntimeData
from agently_devtools import ObservationBridge


bridge = ObservationBridge(
    app_id="agently-main-examples",
    group_id="devtools-local-demo",
)
bridge.register(Agently)

flow = TriggerFlow(name="devtools-local-demo-flow")


@flow.chunk
async def prepare(data: TriggerFlowRuntimeData):
    return {"topic": str(data.input), "status": "prepared"}


@flow.chunk
async def finalize(data: TriggerFlowRuntimeData):
    payload = (
        dict(data.input) if isinstance(data.input, dict) else {"value": data.input}
    )
    payload["status"] = "completed"
    await data.async_set_state("result", payload)


flow.to(prepare).to(finalize)


async def main():
    execution = flow.create_execution()
    await execution.async_start("release readiness")
    snapshot = await execution.async_close()
    print({"snapshot": snapshot, "meta": execution.result.get_meta()})


try:
    asyncio.run(main())
finally:
    bridge.unregister(Agently)

# Stable expected key output from the declared run:
# snapshot.result.status == "completed" for topic "release readiness"; without a listener, a buffered ObservationBridge warning is expected.
#
# How it works:
# ObservationBridge.register(Agently) installs event listeners on the Agently runtime
# to forward TriggerFlow and agent execution events to the agently-devtools server.
# When the devtools server is not running, events are buffered locally and the flow
# still executes normally.  The snapshot from async_close() is the ground truth for
# local assertions; bridge events are best-effort observability side effects.
#
# Flow:
# bridge.register(Agently) -> hooks installed
#   |
#   v
# prepare chunk: returns {"topic":"release readiness","status":"prepared"}
# finalize chunk: state["result"]["status"] = "completed"
#   |
#   v
# async_close() -> {"result":{"topic":"release readiness","status":"completed"}}
# bridge.unregister(Agently) -> hooks removed
