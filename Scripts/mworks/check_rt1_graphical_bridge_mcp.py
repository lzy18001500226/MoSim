#!/usr/bin/env python3
"""Run the non-simulating MWORKS MCP check for the RT1 graphical bridge."""

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
BRIDGE_MODEL = MODEL_ROOT / "RealTime" / "MworksRt1Px4CtrlGraphicalShadow100Hz.mo"
MODEL_NAME = "MoSimQuadrotorModel.RealTime.MworksRt1Px4CtrlGraphicalShadow100Hz"
GRAPHICAL_DEPENDENCIES = (
    (
        ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Px4Ctrl"
        / "Px4CtrlOuterLoopGraphicalSysblock.mo",
        "MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlOuterLoopGraphicalSysblock",
    ),
    (
        ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Px4Ctrl"
        / "Px4CtrlAttitudeThrustSysblockAdapter.mo",
        "MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlAttitudeThrustSysblockAdapter",
    ),
)


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


def check_model(client: Any, model_name: str) -> dict[str, Any]:
    return client.call_tool(
        "check_model",
        {"model_name": model_name, "stop_on_error": False},
        timeout_s=300,
    )


def check_graphical_dependencies(client: Any) -> list[dict[str, Any]]:
    """Check the graphical closure after loading the package root once."""
    checks: list[dict[str, Any]] = []
    for path, model_name in GRAPHICAL_DEPENDENCIES:
        check = check_model(client, model_name)
        checks.append(
            {
                "model_name": model_name,
                "model_source_path": str(path),
                "check_model": check,
            }
        )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--log-output",
        type=Path,
        default=ROOT / "Results/mworks_live_gate/rt1_graphical_bridge/mcp/rt1_graphical_bridge_check.jsonl",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=ROOT / "Results/mworks_live_gate/rt1_graphical_bridge/mcp/RT1_MWORKS_CHECK.json",
    )
    parser.add_argument(
        "--wrapper",
        default=os.environ.get("SYSPLORER_MCP_WRAPPER"),
        help="Override the project Sysplorer MCP wrapper.",
    )
    parser.add_argument(
        "--sysplorer-api-port",
        type=int,
        default=None,
        help="Attach the MCP wrapper to an existing Sysplorer API port instead of starting a session.",
    )
    args = parser.parse_args()

    if args.sysplorer_api_port is not None:
        if args.sysplorer_api_port <= 0:
            raise SystemExit("sysplorer API port must be positive")
        os.environ["SYSPLORER_API_PORT"] = str(args.sysplorer_api_port)

    args.log_output.parent.mkdir(parents=True, exist_ok=True)
    wrapper = run_sysplorer_mcp_smoke.resolve_wrapper(args.wrapper)
    client = run_sysplorer_mcp_smoke.JsonlMcpClient(
        run_sysplorer_mcp_smoke.wrapper_command(wrapper), args.log_output
    )
    health: dict[str, Any] | None = None
    root_package_load: dict[str, Any] | None = None
    graphical_dependency_checks: list[dict[str, Any]] = []
    check: dict[str, Any] | None = None
    error: str | None = None
    try:
        health = run_sysplorer_mcp_smoke.initialize_mcp_client(client)
        root_package_load = load_root_package(client)
        if not root_package_load.get("ok"):
            raise RuntimeError(f"root_package_load_failed:{root_package_load}")
        graphical_dependency_checks = check_graphical_dependencies(client)
        if not all(
            item["check_model"]
            and item["check_model"].get("ok")
            for item in graphical_dependency_checks
        ):
            raise RuntimeError(
                f"graphical_dependency_check_failed:{graphical_dependency_checks}"
            )
        check = check_model(client, MODEL_NAME)
    except Exception as exc:  # Preserve the MCP failure packet as evidence.
        error = repr(exc)
    finally:
        client.close()

    passed = bool(
        health
        and health.get("ok")
        and health.get("driver_ready")
        and root_package_load
        and root_package_load.get("ok")
        and all(
            item["check_model"]
            and item["check_model"].get("ok")
            for item in graphical_dependency_checks
        )
        and check
        and check.get("ok")
    )
    summary = {
        "schema": "mosim.mworks_rt1_graphical_bridge_mcp.v1",
        "source": "MWORKS_MCP",
        "model_name": MODEL_NAME,
        "live_mworks_touched": True,
        "will_not_click_activation_login": True,
        "load_mode": "project_root_package_only",
        "root_package_check": {
            "attempted": True,
            "path": str(ROOT_PACKAGE),
            "claim_boundary": "The root package provides the source closure; each target still requires check_model.",
        },
        "simulation_executed": False,
        "udp_bridge_executed": False,
        "sysplorer_api_port": args.sysplorer_api_port,
        "passed": passed,
        "error": error,
        "health": health,
        "root_package_load": root_package_load,
        "bridge_model_source": str(BRIDGE_MODEL),
        "graphical_dependency_checks": graphical_dependency_checks,
        "check_model": check,
    }
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "passed": passed,
        "summary_output": str(args.summary_output),
        "log_output": str(args.log_output),
        "error": error,
    }, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
