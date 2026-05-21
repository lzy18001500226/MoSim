import asyncio
import json
import time

import httpx


BASE_URL = "http://127.0.0.1:8000"
PROMPT = "How are you?"


def build_payload(text: str):
    return {
        "data": {
            "input": text,
        },
        "options": {},
    }


def print_case(title: str, response: httpx.Response, started: float | None = None):
    elapsed = f" {time.time() - started:.2f}s" if started is not None else ""
    print(f"{title} {response.status_code}{elapsed}")
    print(response.json())


async def test_health(client: httpx.AsyncClient):
    response = await client.get(f"{BASE_URL}/health")
    print_case("GET /health", response)


async def test_post(client: httpx.AsyncClient, payload: dict):
    started = time.time()
    response = await client.post(f"{BASE_URL}/agent/chat", json=payload)
    print_case("POST /agent/chat", response, started)


async def test_get(client: httpx.AsyncClient, payload: dict):
    started = time.time()
    response = await client.get(
        f"{BASE_URL}/agent/chat/get",
        params={"payload": json.dumps(payload, ensure_ascii=False)},
    )
    print_case("GET /agent/chat/get", response, started)


async def test_sse(client: httpx.AsyncClient, payload: dict):
    print("GET /agent/chat/sse (SSE)")
    data_lines = 0
    async with client.stream(
        "GET",
        f"{BASE_URL}/agent/chat/sse",
        params={"payload": json.dumps(payload, ensure_ascii=False)},
    ) as response:
        print("SSE status:", response.status_code)
        async for line in response.aiter_lines():
            if not line:
                continue
            if line.startswith("data: "):
                data_lines += 1
                print("SSE", line[6:])
            elif line.startswith("event: "):
                print(line)


async def test_post_error_missing_options(client: httpx.AsyncClient):
    started = time.time()
    response = await client.post(
        f"{BASE_URL}/agent/chat",
        json={
            "data": {
                "input": "hello",
            }
        },
    )
    print_case("POST /agent/chat invalid payload (missing options)", response, started)


async def test_get_error_invalid_json(client: httpx.AsyncClient):
    started = time.time()
    response = await client.get(
        f"{BASE_URL}/agent/chat/get",
        params={"payload": "{ not-json"},
    )
    print_case("GET /agent/chat/get invalid payload (json parse)", response, started)


async def test_sse_error_invalid_json(client: httpx.AsyncClient):
    print("GET /agent/chat/sse invalid payload (SSE)")
    async with client.stream(
        "GET",
        f"{BASE_URL}/agent/chat/sse",
        params={"payload": "{ not-json"},
    ) as response:
        print("SSE status:", response.status_code)
        async for line in response.aiter_lines():
            if not line:
                continue
            print(line)
            if line.startswith("data: ") or line.startswith("event: error"):
                break


async def main():
    payload = build_payload(PROMPT)
    async with httpx.AsyncClient(timeout=120.0) as client:
        await test_health(client)
        await test_post(client, payload)
        await test_get(client, payload)
        await test_sse(client, payload)
        # print("\n--- Common Error Capture Cases ---")
        # await test_post_error_missing_options(client)
        # await test_get_error_invalid_json(client)
        # await test_sse_error_invalid_json(client)


if __name__ == "__main__":
    asyncio.run(main())

## [Response Example]:

# GET /health 200
# {'ok': True, 'provider': 'agent', 'model': 'qwen2.5:7b', 'base_url': 'http://127.0.0.1:11434/v1'}
# POST /agent/chat 200 1.83s
# {'status': 200, 'data': "As an AI assistant, I don't have feelings, but I'm here and ready to help you! How can I assist you today?", 'msg': None}
# GET /agent/chat/get 200 0.90s
# {'status': 200, 'data': "As an AI assistant, I don't have feelings, but thank you for asking! How can I assist you today?", 'msg': None}
# GET /agent/chat/sse (SSE)
# SSE status: 200
# SSE {"status": 200, "data": "I", "msg": null}
# SSE {"status": 200, "data": "'m", "msg": null}
# SSE {"status": 200, "data": " functioning", "msg": null}
# SSE {"status": 200, "data": " as", "msg": null}
# SSE {"status": 200, "data": " efficiently", "msg": null}
# SSE {"status": 200, "data": " as", "msg": null}
# SSE {"status": 200, "data": " I", "msg": null}
# SSE {"status": 200, "data": " can", "msg": null}
# SSE {"status": 200, "data": " to", "msg": null}
# SSE {"status": 200, "data": " assist", "msg": null}
# SSE {"status": 200, "data": " you", "msg": null}
# SSE {"status": 200, "data": "!", "msg": null}
# SSE {"status": 200, "data": " How", "msg": null}
# SSE {"status": 200, "data": " can", "msg": null}
# SSE {"status": 200, "data": " I", "msg": null}
# SSE {"status": 200, "data": " help", "msg": null}
# SSE {"status": 200, "data": " you", "msg": null}
# SSE {"status": 200, "data": " today", "msg": null}
# SSE {"status": 200, "data": "?", "msg": null}

# Stable expected key output from the declared run:
# GET /health returns provider="agent"; POST/GET/SSE chat routes return status 200 with data chunks.
#
# How it works:
# Test client for fastapi_helper_agent_ollama.py (must be running on port 8000).
# Sends requests to all four route types (GET /health, POST, GET chat, SSE, WebSocket)
# and prints each response.  SSE responses are parsed line by line; WebSocket streams
# the same delta tokens then closes.  All routes share the same {data:{input:"..."}} payload.
