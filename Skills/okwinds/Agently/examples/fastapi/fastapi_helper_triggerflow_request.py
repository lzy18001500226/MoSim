import asyncio
import json
import time

import httpx


BASE_URL = "http://127.0.0.1:8001"
PROMPT = "Give me 3 short suggestions about how to write Python code?"


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
    response = await client.post(f"{BASE_URL}/flow/chat", json=payload)
    print_case("POST /flow/chat", response, started)


async def test_get(client: httpx.AsyncClient, payload: dict):
    started = time.time()
    response = await client.get(
        f"{BASE_URL}/flow/chat/get",
        params={"payload": json.dumps(payload, ensure_ascii=False)},
    )
    print_case("GET /flow/chat/get", response, started)


async def test_sse(client: httpx.AsyncClient, payload: dict):
    print("GET /flow/chat/sse (SSE)")
    data_lines = 0
    async with client.stream(
        "GET",
        f"{BASE_URL}/flow/chat/sse",
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
        f"{BASE_URL}/flow/chat",
        json={
            "data": {
                "input": "hello",
            }
        },
    )
    print_case("POST /flow/chat invalid payload (missing options)", response, started)


async def test_get_error_invalid_json(client: httpx.AsyncClient):
    started = time.time()
    response = await client.get(
        f"{BASE_URL}/flow/chat/get",
        params={"payload": "{ not-json"},
    )
    print_case("GET /flow/chat/get invalid payload (json parse)", response, started)


async def test_post_error_runtime(client: httpx.AsyncClient):
    started = time.time()
    response = await client.post(
        f"{BASE_URL}/flow/chat",
        json={
            "data": {
                "input": "hello",
                "raise_error": True,
            },
            "options": {},
        },
    )
    print_case("POST /flow/chat runtime error from provider", response, started)


async def test_sse_error_runtime(client: httpx.AsyncClient):
    print("GET /flow/chat/sse runtime error (SSE)")
    payload = {
        "data": {
            "input": "hello",
            "raise_error": True,
        },
        "options": {},
    }
    async with client.stream(
        "GET",
        f"{BASE_URL}/flow/chat/sse",
        params={"payload": json.dumps(payload, ensure_ascii=False)},
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
        # await test_post_error_runtime(client)
        # await test_sse_error_runtime(client)


if __name__ == "__main__":
    asyncio.run(main())

## [Response Example]:

# GET /health 200
# {'ok': True, 'provider': 'triggerflow', 'model': 'qwen2.5:7b', 'base_url': 'http://127.0.0.1:11434/v1'}
# POST /flow/chat 200 3.55s
# {'status': 200, 'data': {'response': {'input': 'Give me 3 short suggestions about how to write Python code?', 'reply': '...'}}, 'msg': None}
# GET /flow/chat/get 200 1.18s
# {'status': 200, 'data': {'response': {'input': 'Give me 3 short suggestions about how to write Python code?', 'reply': '...'}}, 'msg': None}
# GET /flow/chat/sse (SSE)
# SSE status: 200
# SSE {"status": 200, "data": {"event": "delta", "content": "Sure"}, "msg": null}
# SSE {"status": 200, "data": {"event": "delta", "content": "!"}, "msg": null}
# SSE {"status": 200, "data": {"event": "delta", "content": " Here"}, "msg": null}
# SSE {"status": 200, "data": {"event": "delta", "content": " are"}, "msg": null}
# SSE {"status": 200, "data": {"event": "delta", "content": " three"}, "msg": null}
# SSE {"status": 200, "data": {"event": "delta", "content": " short"}, "msg": null}
# SSE {"status": 200, "data": {"event": "delta", "content": " suggestions"}, "msg": null}
# SSE {"status": 200, "data": {"event": "delta", "content": " for"}, "msg": null}
# SSE {"status": 200, "data": {"event": "delta", "content": " writing"}, "msg": null}
# SSE {"status": 200, "data": {"event": "delta", "content": " Python"}, "msg": null}
# SSE {"status": 200, "data": {"event": "delta", "content": " code"}, "msg": null}
# SSE {"status": 200, "data": {"event": "delta", "content": ":\n\n"}, "msg": null}
# SSE {"status": 200, "data": {"event": "delta", "content": "1"}, "msg": null}
# ...
# SSE {"status": 200, "data": {"event": "delta", "content": " indent"}, "msg": null}
# SSE {"status": 200, "data": {"event": "delta", "content": "."}, "msg": null}
# SSE {"status": 200, "data": {"event": "final", "content": "Sure! Here are three short suggestions for writing Python code:\n\n1. **Use Meaningful Variable Names**: Choose names that clearly describe what the variable holds. This makes your code easier to understand and maintain.\n\n2. **Leverage List Comprehensions and Built-in Functions**: These can make your code more concise and readable. For example, use `map()`, `filter()`, or list comprehensions instead of explicit loops where appropriate.\n\n3. **Indent Properly and Be Consistent**: Python relies on indentation to define blocks of code. Ensure you are consistent with 4 spaces (or however your team uses) for each level of indent."}, "msg": null}

# Stable expected key output from the declared run:
# GET /health returns provider="triggerflow"; POST/GET/SSE flow routes return status 200 and data.response.
#
# How it works:
# Test client for fastapi_helper_triggerflow_ollama.py (must be running on port 8001).
# Tests all route types: GET /health, POST, GET, SSE, WebSocket.
# TriggerFlow responses include response.data.response (the close snapshot), not just text.
# SSE items from async_put_into_stream() arrive before the final snapshot item.
