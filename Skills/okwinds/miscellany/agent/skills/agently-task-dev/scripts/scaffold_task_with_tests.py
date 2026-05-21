#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


def _norm_task_name(name: str) -> str:
    name = name.strip().lower().replace("-", "_")
    name = re.sub(r"[^a-z0-9_]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    if not name:
        raise ValueError("task name is empty after normalization")
    if not re.match(r"^[a-z_][a-z0-9_]*$", name):
        raise ValueError(f"invalid task name: {name}")
    return name


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _plan_outputs(task_name: str, out_root: Path) -> list[Path]:
    tasks_root = out_root / "agently_tasks"
    task_dir = tasks_root / task_name
    tests_dir = out_root / "tests"
    return [
        tasks_root / "__init__.py",
        task_dir / "__init__.py",
        task_dir / "task.py",
        task_dir / "asgi_app.py",
        task_dir / "tests_openai_stub.py",
        tests_dir / "conftest.py",
        tests_dir / f"test_{task_name}.py",
    ]


def _existing_outputs(paths: list[Path]) -> list[Path]:
    return [p for p in paths if p.exists()]


ASGI_OPENAI_STUB = r"""# Minimal OpenAI-compatible ASGI stub for Agently tests
# - Supports POST /v1/chat/completions with SSE streaming
# - Provides deterministic "model output" (JSON text) split into chunks to exercise streaming_parse/instant
from __future__ import annotations

import json
from typing import Any, Awaitable, Callable


def _sse_data(data: str) -> bytes:
    return f"data: {data}\n\n".encode("utf-8")


async def app(scope: dict, receive: Callable[[], Awaitable[dict]], send: Callable[[dict], Awaitable[None]]):
    if scope["type"] != "http":
        await send({"type": "http.response.start", "status": 404, "headers": [(b"content-type", b"text/plain")]})
        await send({"type": "http.response.body", "body": b"not found"})
        return

    path = scope.get("path", "")
    method = scope.get("method", "GET").upper()

    if method != "POST" or path != "/v1/chat/completions":
        await send({"type": "http.response.start", "status": 404, "headers": [(b"content-type", b"text/plain")]})
        await send({"type": "http.response.body", "body": b"not found"})
        return

    # Drain request body (we don't need to parse; this is a deterministic stub).
    body = b""
    while True:
        msg = await receive()
        if msg["type"] == "http.request":
            body += msg.get("body", b"")
            if not msg.get("more_body", False):
                break

    # Deterministic structured output (JSON string) that Agently will streaming-parse.
    result_obj: dict[str, Any] = {
        "reply": "ok",
        "sources": [
            {"url": "https://example.com/a", "notes": "stub source A"},
            {"url": "https://example.com/b", "notes": "stub source B"},
        ],
    }
    result_text = json.dumps(result_obj, ensure_ascii=False)

    # Split into chunks to exercise streaming parse (instant events).
    chunks = [result_text[:10], result_text[10:25], result_text[25:]]

    headers = [
        (b"content-type", b"text/event-stream; charset=utf-8"),
        (b"cache-control", b"no-cache"),
        (b"connection", b"keep-alive"),
    ]
    await send({"type": "http.response.start", "status": 200, "headers": headers})

    def _chunk_payload(content: str, finish_reason: str | None = None) -> str:
        return json.dumps(
            {
                "id": "stub",
                "object": "chat.completion.chunk",
                "choices": [{"index": 0, "delta": {"content": content}, "finish_reason": finish_reason}],
            },
            ensure_ascii=False,
        )

    # Stream content chunks.
    for i, part in enumerate(chunks):
        await send({"type": "http.response.body", "body": _sse_data(_chunk_payload(part)), "more_body": True})

    # Final chunk with finish_reason=stop (optional but close to real providers).
    await send(
        {
            "type": "http.response.body",
            "body": _sse_data(_chunk_payload("", finish_reason="stop")),
            "more_body": True,
        }
    )
    await send({"type": "http.response.body", "body": _sse_data("[DONE]"), "more_body": False})
"""


TASK_PY = r"""from __future__ import annotations

from typing import Any, Iterator, AsyncIterator

from agently import Agently


def get_schema() -> dict[str, Any]:
    return {
        "reply": (str, "Final reply to user"),
        "sources": [
            {
                "url": (str, "Source URL"),
                "notes": (str, "Why this source matters / extracted notes"),
            }
        ],
    }


def _build_agent() -> Any:
    agent = Agently.create_agent()
    # Production default: local OpenAI-compatible (e.g., Ollama).
    # In tests we override settings to use an ASGI stub transport.
    agent.set_settings(
        "OpenAICompatible",
        {
            "base_url": "http://127.0.0.1:11434/v1",
            "model": "qwen2.5:7b",
            "options": {"temperature": 0.2},
        },
    )
    return agent


def run(question: str) -> dict[str, Any]:
    agent = _build_agent()
    schema = get_schema()
    result = (
        agent.input(question)
        .output(schema)
        .start(
            ensure_keys=["sources[*].url", "sources[*].notes", "reply"],
            max_retries=2,
            raise_ensure_failure=False,
        )
    )
    return result


def stream_instant(question: str) -> Iterator[Any]:
    agent = _build_agent()
    schema = get_schema()
    response = agent.input(question).output(schema).get_response()
    for ev in response.result.get_generator(type="instant"):
        yield ev


async def stream_instant_async(question: str) -> AsyncIterator[Any]:
    agent = _build_agent()
    schema = get_schema()
    response = agent.input(question).output(schema).get_response()
    async for ev in response.result.get_async_generator(type="instant"):
        yield ev
"""


ASGI_APP = r"""# Minimal ASGI app exposing the task as SSE + POST without external deps (no FastAPI required)
from __future__ import annotations

import json
from urllib.parse import parse_qs
from typing import Awaitable, Callable

from .task import stream_instant_async, run


def _json_response(status: int, obj: dict):
    body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    return status, [(b"content-type", b"application/json; charset=utf-8")], body


async def app(scope: dict, receive: Callable[[], Awaitable[dict]], send: Callable[[dict], Awaitable[None]]):
    if scope["type"] != "http":
        status, headers, body = _json_response(404, {"error": "not found"})
        await send({"type": "http.response.start", "status": status, "headers": headers})
        await send({"type": "http.response.body", "body": body})
        return

    path = scope.get("path", "")
    method = scope.get("method", "GET").upper()

    if method == "GET" and path == "/sse":
        query = parse_qs((scope.get("query_string") or b"").decode("utf-8"))
        question = (query.get("question") or [""])[0]
        headers = [(b"content-type", b"text/event-stream; charset=utf-8")]
        await send({"type": "http.response.start", "status": 200, "headers": headers})

        # Convert Agently instant events → SSE
        async for ev in stream_instant_async(question):
            payload = {
                "type": "field",
                "data": {"path": getattr(ev, "path", None), "value": getattr(ev, "value", None)},
            }
            chunk = f"data: {json.dumps(payload, ensure_ascii=False)}\n\n".encode("utf-8")
            await send({"type": "http.response.body", "body": chunk, "more_body": True})

        await send({"type": "http.response.body", "body": b"", "more_body": False})
        return

    if method == "POST" and path == "/ask":
        body = b""
        while True:
            msg = await receive()
            if msg["type"] == "http.request":
                body += msg.get("body", b"")
                if not msg.get("more_body", False):
                    break
        try:
            data = json.loads(body.decode("utf-8") or "{}")
        except Exception:
            data = {}
        question = str(data.get("question") or "")
        result = run(question)
        status, headers, out = _json_response(200, {"result": result})
        await send({"type": "http.response.start", "status": status, "headers": headers})
        await send({"type": "http.response.body", "body": out})
        return

    status, headers, body = _json_response(404, {"error": "not found"})
    await send({"type": "http.response.start", "status": status, "headers": headers})
    await send({"type": "http.response.body", "body": body})
"""


TEST_PY = r"""from __future__ import annotations

import asyncio
import json

import httpx
import pytest

try:
    from agently import Agently
except Exception:
    pytest.skip(
        "agently is not importable. Run tests inside the Agently repo/venv or set PYTHONPATH to agently.",
        allow_module_level=True,
    )

from agently_tasks.{task_name}.task import get_schema, run, stream_instant


@pytest.fixture(autouse=True)
def _use_openai_stub():
    # Route OpenAICompatible requests into an ASGI stub so tests do not require network/API keys.
    from agently_tasks.{task_name}.tests_openai_stub import app as stub_app

    transport = httpx.ASGITransport(app=stub_app)
    Agently.set_settings(
        "OpenAICompatible",
        {{
            "base_url": "http://testserver/v1",
            "model": "stub-model",
            "auth": "none",
            "client_options": {{
                "transport": transport,
                "base_url": "http://testserver",
            }},
        }},
    )
    yield


def test_run_returns_schema_and_keys():
    schema = get_schema()
    assert isinstance(schema, dict)

    result = run("hello")
    assert isinstance(result, dict)
    assert "reply" in result and isinstance(result["reply"], str)
    assert "sources" in result and isinstance(result["sources"], list) and result["sources"]
    assert "url" in result["sources"][0]
    assert "notes" in result["sources"][0]


def test_instant_stream_has_paths():
    events = list(stream_instant("hello"))
    assert events, "expected instant events"
    paths = [getattr(e, "path", None) for e in events]
    assert any(p == "reply" for p in paths)


def test_sse_endpoint_streams_fields():
    async def _run():
        from agently_tasks.{task_name}.asgi_app import app as task_app

        transport = httpx.ASGITransport(app=task_app)
        async with httpx.AsyncClient(transport=transport, base_url="http://task") as client:
            r = await client.get("/sse", params={{"question": "hello"}})
            assert r.status_code == 200
            assert r.headers.get("content-type", "").startswith("text/event-stream")
            # At least one SSE event line
            assert "data:" in r.text
            # The payload should be JSON
            first = r.text.split("data: ", 1)[1].split("\n", 1)[0]
            obj = json.loads(first)
            assert obj.get("type") == "field"

    asyncio.run(_run())
"""

CONFTEST_PY = r"""from __future__ import annotations

import sys
from pathlib import Path

# Make the scaffolded project importable regardless of pytest rootdir detection.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold an Agently task + regression tests (offline stubbed).")
    parser.add_argument("task_name", help="Task name (letters/numbers/-/_).")
    parser.add_argument("--out", default=".", help="Output project root (default: .).")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files if they exist (default: fail if any target exists).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned file writes and exit without writing anything.",
    )
    args = parser.parse_args()

    task_name = _norm_task_name(args.task_name)
    out_root = Path(args.out).resolve()

    planned = _plan_outputs(task_name=task_name, out_root=out_root)
    existing = _existing_outputs(planned)

    if existing and not args.force:
        print("[FAIL] target files already exist (use --force to overwrite):")
        for p in existing:
            print(f"- {p}")
        return 1

    if args.dry_run:
        print("[DRY-RUN] planned writes:")
        for p in planned:
            marker = "overwrite" if p in existing else "create"
            print(f"- {marker}: {p}")
        return 0

    # Layout:
    # agently_tasks/<task_name>/{task.py,asgi_app.py,tests_openai_stub.py}
    # tests/test_<task_name>.py
    tasks_root = out_root / "agently_tasks"
    task_dir = tasks_root / task_name
    tests_dir = out_root / "tests"

    _write(tasks_root / "__init__.py", "")
    _write(task_dir / "__init__.py", "")
    _write(task_dir / "task.py", TASK_PY)
    _write(task_dir / "asgi_app.py", ASGI_APP)
    _write(task_dir / "tests_openai_stub.py", ASGI_OPENAI_STUB)

    test_content = TEST_PY.format(task_name=task_name)
    _write(tests_dir / "conftest.py", CONFTEST_PY)
    _write(tests_dir / f"test_{task_name}.py", test_content)

    print("[OK] scaffolded:")
    print(f"- {task_dir}")
    print(f"- {tests_dir / f'test_{task_name}.py'}")
    print("\nNext:")
    print("- Run: `python -m pytest -q`")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
