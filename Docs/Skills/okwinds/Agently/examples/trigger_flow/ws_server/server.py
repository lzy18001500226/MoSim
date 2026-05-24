import asyncio
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from agently import Agently, TriggerFlow, TriggerFlowRuntimeData


OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "ollama")

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": OLLAMA_BASE_URL,
        "api_key": OLLAMA_API_KEY,
        "model": OLLAMA_MODEL,
        "model_type": "chat",
        "request_options": {"temperature": 0.3},
    },
)

app = FastAPI()
flow = TriggerFlow(name="ws-stream-demo")


async def model_response(data: TriggerFlowRuntimeData):
    agent = Agently.create_agent()
    agent.role("You are a concise and helpful assistant.", always=True)
    response = agent.input(str(data.input)).get_response()

    async for delta in response.get_async_generator(type="delta"):
        if delta:
            await data.async_put_into_stream({"event": "delta", "content": delta})

    full_reply = await response.async_get_text()
    await data.async_put_into_stream({"event": "final", "content": full_reply})
    await data.async_set_state("reply", full_reply)


flow.to(model_response)


@app.websocket("/")
async def trigger_flow_websocket(ws: WebSocket):
    await ws.accept()
    await ws.send_json({"status": "ready", "content": None, "stop": False})
    try:
        while True:
            payload = await ws.receive_json()
            execution = flow.create_execution(auto_close=False)
            await execution.async_start(payload["user_input"])
            close_task = asyncio.create_task(execution.async_close())

            async for item in execution.get_async_runtime_stream(timeout=None):
                if not isinstance(item, dict):
                    continue
                if item.get("event") == "delta":
                    await ws.send_json(
                        {
                            "status": "received",
                            "content": item.get("content"),
                            "stop": False,
                        }
                    )
                elif item.get("event") == "final":
                    await ws.send_json(
                        {
                            "status": "done",
                            "content": item.get("content"),
                            "stop": True,
                        }
                    )

            await close_task
    except WebSocketDisconnect:
        pass
    except Exception:
        await ws.close()


if __name__ == "__main__":
    import uvicorn

    print("Start WebSocket Server on http://127.0.0.1:15596")
    print(f"Using local Ollama model: {OLLAMA_MODEL} ({OLLAMA_BASE_URL})")
    uvicorn.run(app, host="0.0.0.0", port=15596)

# Stable expected key output from the declared run:
# server startup prints the local Ollama model/base_url; a WebSocket client first receives {"status": "ready", "stop": False}, then delta events and one final done event.
#
# How it works:
# - The file starts a service/demo wrapper around an Agently provider.
# - Requests are converted into Agent or TriggerFlow calls and streamed or returned through the service route.
# - Stable behavior is the route/UI startup and the response shape, not exact model prose.
#
# ASCII flow:
# WebSocket message
#   |
#   v
# TriggerFlow execution
#   |
#   v
# model delta -> runtime stream
#   |
#   v
# WebSocket received/done messages
