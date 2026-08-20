#!/usr/bin/env python3
"""Diagnose the RT1 graphical bridge through the direct MWORKS simulation API."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    import run_sysplorer_mcp_smoke
except ImportError:  # pragma: no cover
    ROOT = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(ROOT / "Scripts" / "mworks"))
    import run_sysplorer_mcp_smoke  # type: ignore


ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = ROOT / "Models" / "MoSimQuadrotorModel"
ROOT_PACKAGE = MODEL_ROOT / "package.mo"
MODEL_NAME = "MoSimQuadrotorModel.RealTime.MworksRt1Px4CtrlGraphicalShadow100Hz"
RESULT_VARIABLES = [
    "time",
    "exchangeCallCount",
    "sampleTicks",
    "processedFrames",
    "sentFrames",
    "socketReady",
    "socketErrorCode",
]


def load_root_package(client: Any) -> dict[str, Any]:
    return client.call_tool(
        "model_manager",
        {
            "action": "load_file",
            "file_path": str(ROOT_PACKAGE),
            "force_reload": True,
            "auto_load_deps": True,
        },
        timeout_s=300,
    )


def direct_simulation_source(stop_time_s: float) -> str:
    return f'''\
import json
import mworks.sysplorer as ModelingPy

MODEL_NAME = {MODEL_NAME!r}
results = {{"simulation_api": "ModelingPy.SimulateModel"}}

def capture(api_name):
    diagnostic = {{"api": api_name}}
    try:
        value = getattr(ModelingPy, api_name)()
        json.dumps(value, ensure_ascii=False)
        diagnostic.update(ok=True, data=value)
    except Exception as exc:
        diagnostic.update(ok=False, error=repr(exc))
    return diagnostic

try:
    results["simulate"] = ModelingPy.SimulateModel(
        MODEL_NAME,
        startTime=0.0,
        stopTime={stop_time_s!r},
        interval=0.01,
        simMode=0,
        path="",
    )
except Exception as exc:
    results["simulate"] = False
    results["simulate_error"] = repr(exc)

results["post_simulation_diagnostics"] = {{
    name: capture(name)
    for name in (
        "GetSimulationExitState",
        "GetSimulationState",
        "GetCurrentSimTime",
        "MessageText",
        "GetLastErrors",
    )
}}
RUN_SCRIPT_RESULT = results
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stop-time-s", type=float, default=0.03)
    parser.add_argument("--mcp-timeout-s", type=float, default=180.0)
    parser.add_argument(
        "--log-output",
        type=Path,
        default=ROOT / "Results/mworks_live_gate/rt1_graphical_bridge/direct_api/mcp.jsonl",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=ROOT / "Results/mworks_live_gate/rt1_graphical_bridge/direct_api/RT1_DIRECT_API_DIAGNOSTIC.json",
    )
    parser.add_argument("--wrapper", default=os.environ.get("SYSPLORER_MCP_WRAPPER"))
    parser.add_argument("--sysplorer-api-port", type=int, default=None)
    args = parser.parse_args()

    if args.stop_time_s <= 0 or args.mcp_timeout_s <= 0:
        raise SystemExit("stop-time-s and mcp-timeout-s must be positive")
    if args.sysplorer_api_port is not None:
        if args.sysplorer_api_port <= 0:
            raise SystemExit("sysplorer-api-port must be positive")
        os.environ["SYSPLORER_API_PORT"] = str(args.sysplorer_api_port)

    args.log_output.parent.mkdir(parents=True, exist_ok=True)
    wrapper = run_sysplorer_mcp_smoke.resolve_wrapper(args.wrapper)
    client = run_sysplorer_mcp_smoke.JsonlMcpClient(
        run_sysplorer_mcp_smoke.wrapper_command(wrapper), args.log_output
    )
    health: dict[str, Any] | None = None
    root_package_load: dict[str, Any] | None = None
    check: dict[str, Any] | None = None
    direct_call: dict[str, Any] | None = None
    result_values: dict[str, Any] | None = None
    error: str | None = None
    try:
        health = run_sysplorer_mcp_smoke.initialize_mcp_client(client)
        root_package_load = load_root_package(client)
        if not root_package_load.get("ok"):
            raise RuntimeError(f"root_package_load_failed:{root_package_load}")
        check = client.call_tool(
            "check_model",
            {"model_name": MODEL_NAME, "stop_on_error": False},
            timeout_s=300,
        )
        if not check.get("ok"):
            raise RuntimeError(f"check_model_failed:{check}")
        direct_call = client.call_tool(
            "call_code",
            {"mode": "run_script", "payload": {"python_source": direct_simulation_source(args.stop_time_s)}},
            timeout_s=args.mcp_timeout_s,
        )
        run_result = direct_call.get("run_script_result", {}) if direct_call else {}
        if direct_call.get("ok") and run_result.get("simulate") is True:
            result_values = client.call_tool(
                "result_manager",
                {
                    "action": "get_vars_values",
                    "model_name": MODEL_NAME,
                    "var_names": RESULT_VARIABLES,
                },
                timeout_s=60,
            )
    except Exception as exc:
        error = repr(exc)
    finally:
        client.close()

    run_result = direct_call.get("run_script_result", {}) if direct_call else {}
    simulation_ok = bool(direct_call and direct_call.get("ok") and run_result.get("simulate") is True)
    values_ok = bool(result_values and result_values.get("ok")) if simulation_ok else False
    summary = {
        "schema": "mosim.mworks_rt1_graphical_bridge_direct_api.v1",
        "source": "MWORKS_MCP",
        "model_name": MODEL_NAME,
        "live_mworks_touched": True,
        "will_not_click_activation_login": True,
        "load_mode": "project_root_package_only",
        "simulation_api": "ModelingPy.SimulateModel",
        "simulation_mode": 0,
        "stop_time_s": args.stop_time_s,
        "claim_boundary": "MWORKS RT1 graphical bridge runtime diagnostic only; no UDP peer, ROS, PX4, Gazebo, planner, localization, or flight evidence.",
        "passed": bool(
            health
            and health.get("ok")
            and root_package_load
            and root_package_load.get("ok")
            and check
            and check.get("ok")
            and simulation_ok
            and values_ok
        ),
        "error": error,
        "health": health,
        "root_package_load": root_package_load,
        "check_model": check,
        "direct_simulation": direct_call,
        "result_values": result_values,
        "artifact_refs": {"mcp_log": str(args.log_output)},
    }
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": summary["passed"], "summary_output": str(args.summary_output), "error": error}, ensure_ascii=False, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
