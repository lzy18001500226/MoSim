# pyright: reportMissingImports=false

"""InteractiveWrapper example using a TriggerFlow with streamed stage updates."""

import asyncio

from agently import Agently, TriggerFlow, TriggerFlowRuntimeData
from agently_devtools import ObservationBridge, InteractiveWrapper

bridge = ObservationBridge(app_id="agently-main-examples", group_id="interactive-wrapper-triggerflow")
bridge.register(Agently)

flow = TriggerFlow(name="interactive-demo-flow")


@flow.chunk
async def validate_input(data: TriggerFlowRuntimeData):
    value = data.input
    message = value.get("input", "") if isinstance(value, dict) else str(value)
    if not message:
        await data.async_put_into_stream("Validation failed: empty input received.\n")
        return {"status": "error", "message": "Empty input received"}
    await data.async_put_into_stream(f"Validated input: {message}\n")
    return {"status": "validated", "message": message, "length": len(message)}


@flow.chunk
async def process_message(data: TriggerFlowRuntimeData):
    payload = data.input if isinstance(data.input, dict) else {}
    if payload.get("status") == "error":
        await data.async_put_into_stream("Skipping processing because validation failed.\n")
        return payload

    message = payload.get("message", "")
    processed = {
        "original": message,
        "uppercase": message.upper(),
        "word_count": len(message.split()),
        "status": "processing_complete",
    }
    await asyncio.sleep(0.2)
    await data.async_put_into_stream("Transforming message to uppercase...\n")
    await asyncio.sleep(0.2)
    await data.async_put_into_stream(f"Word count: {processed['word_count']}\n")
    return processed


@flow.chunk
async def finalize(data: TriggerFlowRuntimeData):
    result = dict(data.input) if isinstance(data.input, dict) else {"value": data.input}
    if result.get("status") == "error":
        await data.async_put_into_stream("Flow finished with a validation error.\n")
    else:
        result["final_status"] = "completed"
        await data.async_put_into_stream("Flow complete. Final structured result is ready.\n")
    await data.async_set_state("result", result)


flow.to(validate_input).to(process_message).to(finalize)

interactive = InteractiveWrapper(
    flow,
    title="TriggerFlow Demo",
    description="Interactive TriggerFlow that streams stage updates before returning the close snapshot.",
)


if __name__ == "__main__":
    print(f"Interactive UI: {interactive.ui_url}")
    print("The flow streams progress messages for validate -> process -> finalize before close.")
    try:
        interactive.wait()
    finally:
        bridge.unregister(Agently)

# Expected output when launched and given input "hello agently":
# Interactive UI: http://localhost:<port>/?...
# (browser receives streamed chunks):
#   "Validated input: hello agently"
#   "Transforming message to uppercase..."
#   "Word count: 2"
#   "Flow complete. Final structured result is ready."
#
# How it works:
# InteractiveWrapper wraps a TriggerFlow.  When the browser sends a request, the wrapper
# starts a flow execution and streams async_put_into_stream() messages to the UI as they
# are emitted.  After async_close(), the final structured snapshot is also delivered.
# Three chunks (validate_input, process_message, finalize) each write progress messages
# via async_put_into_stream() and the final state via async_set_state().
#
# Flow:
# browser request: "hello agently"
#   |
#   v
# validate_input: stream "Validated input: hello agently\n"
#   -> returns {"status":"validated","message":"hello agently","length":15}
#   |
#   v
# process_message: sleep(0.2) -> stream "Transforming message to uppercase...\n"
#                  sleep(0.2) -> stream "Word count: 2\n"
#   -> returns {"uppercase":"HELLO AGENTLY","word_count":2,"status":"processing_complete"}
#   |
#   v
# finalize: stream "Flow complete. Final structured result is ready.\n"
#   -> state["result"]["final_status"] = "completed"
# async_close() -> final snapshot delivered to browser
