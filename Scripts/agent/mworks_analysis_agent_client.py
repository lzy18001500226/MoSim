#!/usr/bin/env python3
"""Small dependency-free client used by the Julia Model Studio bridge."""

from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.error
import urllib.request
from typing import Any


def decode_argument(value: str) -> str:
    return base64.b64decode(value.encode("ascii"), validate=True).decode("utf-8")


def decode_lines(value: str) -> list[str]:
    if not value:
        return []
    return [line.strip() for line in decode_argument(value).splitlines() if line.strip()]


def encode_field(value: Any) -> str:
    return base64.b64encode(str(value).encode("utf-8")).decode("ascii")


def emit_turn(response: dict[str, Any]) -> None:
    activities = ", ".join(str(item) for item in response.get("activities", []) if item)
    print(
        "\t".join(
            [
                "turn",
                "1" if response.get("ok") else "0",
                encode_field(response.get("status", "")),
                encode_field(response.get("answer", "")),
                encode_field(response.get("partial_answer", "")),
                encode_field(activities),
                encode_field(response.get("request_id", "")),
                encode_field(response.get("error_code", "")),
                encode_field(response.get("codex_thread_id", "")),
                encode_field(response.get("error", "")),
            ]
        )
    )


def request_json(url: str, payload: dict[str, Any] | None, timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="GET" if payload is None else "POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["health", "query", "turn-start", "turn-status", "turn-cancel"])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--question-b64")
    parser.add_argument("--context-b64", default="")
    parser.add_argument("--model", default="")
    parser.add_argument("--attachments-b64", default="")
    parser.add_argument("--thread-id", default="")
    parser.add_argument("--request-id", default="")
    args = parser.parse_args()
    base_url = f"http://{args.host}:{args.port}"
    try:
        if args.command == "health":
            response = request_json(base_url + "/health", None, args.timeout)
            print("\t".join(["health", encode_field(json.dumps(response, ensure_ascii=False))]))
            return 0
        if args.command in {"query", "turn-start"}:
            if not args.question_b64:
                raise ValueError("missing_question")
            payload = {
                "question": decode_argument(args.question_b64),
                "context_text": decode_argument(args.context_b64) if args.context_b64 else "",
                "model": args.model,
                "attachments": decode_lines(args.attachments_b64),
                "codex_thread_id": args.thread_id,
            }
            endpoint = "/mworks/query" if args.command == "query" else "/mworks/turns"
            response = request_json(base_url + endpoint, payload, args.timeout)
            if args.command == "query":
                print(
                    "\t".join(
                        [
                            "query",
                            "1" if response.get("ok") else "0",
                            encode_field(response.get("answer", "")),
                            encode_field(", ".join(str(item) for item in response.get("tools_used", []) if item)),
                            encode_field(response.get("request_id", "")),
                            encode_field(response.get("error_code", "")),
                        ]
                    )
                )
            else:
                emit_turn(response)
            return 0
        if not args.request_id:
            raise ValueError("missing_request_id")
        if args.command == "turn-status":
            response = request_json(base_url + "/mworks/turns/" + args.request_id, None, args.timeout)
        else:
            response = request_json(base_url + "/mworks/turns/" + args.request_id + "/cancel", {}, args.timeout)
        emit_turn(response)
        return 0
    except (ValueError, urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        print("\t".join(["error", encode_field(type(exc).__name__), encode_field(str(exc))]))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
