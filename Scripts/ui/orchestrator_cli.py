#!/usr/bin/env python3
"""JSON command-line entry point for the MoSim Orchestrator core."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.orchestration import ORCHESTRATOR_COMMANDS, MoSimOrchestrator


def dispatch(orchestrator: MoSimOrchestrator, request: dict):
    action = request.get("action") or request.get("command")
    if action not in ORCHESTRATOR_COMMANDS:
        return orchestrator._response(str(request.get("request_id", "")), False, "unsupported_action")
    method = getattr(orchestrator, action, None)
    arguments = dict(request)
    arguments.pop("action", None)
    arguments.pop("command", None)
    arguments.setdefault("request_id", "")
    return method(**arguments)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request", type=Path)
    parser.add_argument("--response", type=Path)
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))
    response = dispatch(MoSimOrchestrator(), request)
    rendered = json.dumps(response, ensure_ascii=False, indent=2) + "\n"
    if args.response:
        args.response.parent.mkdir(parents=True, exist_ok=True)
        args.response.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0 if response.get("accepted") else 2


if __name__ == "__main__":
    raise SystemExit(main())
