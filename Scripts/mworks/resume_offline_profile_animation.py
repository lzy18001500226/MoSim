#!/usr/bin/env python3
"""Resume the native animation already bound in the retained Sysplorer session."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Scripts" / "mworks"))
import run_sysplorer_mcp_smoke as mcp  # type: ignore


def main() -> int:
    source = '''
import mworks.sysplorer as ModelingPy

result = {}
try:
    result["create_animation"] = ModelingPy.CreateAnimation()
    result["animation_speed"] = ModelingPy.AnimationSpeed(0.2)
except Exception as exc:
    result["exception"] = repr(exc)
RUN_SCRIPT_RESULT = result
'''
    log_path = ROOT / "Results" / "control_platform" / "offline_batches" / "resume_animation_mcp.jsonl"
    wrapper = mcp.resolve_wrapper(None)
    client = mcp.JsonlMcpClient(mcp.wrapper_command(wrapper), log_path)
    try:
        health = mcp.initialize_mcp_client(client)
        response = client.call_tool(
            "call_code",
            {"mode": "run_script", "payload": {"python_source": source}},
            timeout_s=30,
        )
    finally:
        client.close()
    nested = response.get("run_script_result") if isinstance(response, dict) else None
    if not isinstance(nested, dict) or not response.get("ok") or not nested.get("create_animation"):
        raise RuntimeError(f"no_bound_result_in_current_session:{nested or response}")
    print(json.dumps({"ok": True, "driver_ready": bool(health.get("driver_ready"))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
