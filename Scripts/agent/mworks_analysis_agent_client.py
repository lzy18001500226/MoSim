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


def encode_field(value: Any) -> str:
    return base64.b64encode(str(value).encode("utf-8")).decode("ascii")


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
    parser.add_argument("command", choices=["health", "query"])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--question-b64")
    parser.add_argument("--context-b64", default="")
    args = parser.parse_args()
    base_url = f"http://{args.host}:{args.port}"
    try:
        if args.command == "health":
            response = request_json(base_url + "/health", None, args.timeout)
            print("\t".join(["health", encode_field(json.dumps(response, ensure_ascii=False))]))
            return 0
        if not args.question_b64:
            raise ValueError("missing_question")
        response = request_json(
            base_url + "/mworks/query",
            {
                "question": decode_argument(args.question_b64),
                "context_text": decode_argument(args.context_b64) if args.context_b64 else "",
            },
            args.timeout,
        )
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
        return 0
    except (ValueError, urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        print("\t".join(["error", encode_field(type(exc).__name__), encode_field(str(exc))]))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
