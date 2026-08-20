#!/usr/bin/env python3
"""Run the MWORKS RT1 graphical bridge against a local UDP loopback fixture."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
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
FIXTURE = ROOT / "Scripts" / "mworks_live" / "run_rt1_mworks_graphical_loopback.py"
BATCH_SIM_MODE = 2
RESULT_VARIABLES = [
    "exchangeCallCount",
    "sampleTicks",
    "processedFrames",
    "sentFrames",
    "receivedDatagrams",
    "rejectedDatagrams",
    "socketReady",
    "socketInitStatus",
    "socketErrorCode",
    "receivedDatagramsThisTick",
    "rejectedDatagramsThisTick",
    "lastReceivedByteCount",
    "receiveErrorCode",
    "lastArmed",
    "controllerOutputValid",
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


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=f"rt1-mworks-graphical-{time.time_ns()}")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=49020)
    parser.add_argument("--rate-hz", type=float, default=100.0)
    parser.add_argument("--simulation-duration-s", type=float, default=2.0)
    parser.add_argument("--fixture-duration-s", type=float, default=90.0)
    parser.add_argument("--minimum-responses", type=int, default=20)
    parser.add_argument(
        "--fixture-profile",
        choices=("hover", "rt2_outer_loop_excitation"),
        default="hover",
        help="State/reference profile emitted by the local UDP fixture.",
    )
    parser.add_argument(
        "--mcp-timeout-s",
        type=float,
        default=300.0,
        help="Maximum wall-clock time for each MWORKS simulation call.",
    )
    parser.add_argument(
        "--log-output",
        type=Path,
        default=ROOT / "Results/mworks_live_gate/rt1_graphical_bridge/loopback/mcp.jsonl",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=ROOT / "Results/mworks_live_gate/rt1_graphical_bridge/loopback/RT1_LOOPBACK_MWORKS.json",
    )
    parser.add_argument("--wrapper", default=os.environ.get("SYSPLORER_MCP_WRAPPER"))
    parser.add_argument(
        "--sysplorer-api-port",
        type=int,
        default=None,
        help="Attach the MCP wrapper to an existing Sysplorer API port instead of starting a session.",
    )
    args = parser.parse_args()

    if args.host not in {"127.0.0.1", "localhost"}:
        raise SystemExit("This MWORKS-only loopback runner accepts localhost endpoints only")
    if args.simulation_duration_s <= 0 or args.fixture_duration_s <= args.simulation_duration_s:
        raise SystemExit("fixture duration must be greater than simulation duration")
    if args.rate_hz <= 0 or args.minimum_responses < 1 or args.mcp_timeout_s <= 0:
        raise SystemExit("rate, minimum responses, and MCP timeout must be positive")
    if args.sysplorer_api_port is not None and args.sysplorer_api_port <= 0:
        raise SystemExit("sysplorer API port must be positive")
    if args.sysplorer_api_port is not None:
        os.environ["SYSPLORER_API_PORT"] = str(args.sysplorer_api_port)

    run_dir = args.summary_output.parent
    run_dir.mkdir(parents=True, exist_ok=True)
    args.log_output.parent.mkdir(parents=True, exist_ok=True)
    fixture_output = run_dir / (
        "RT2_LOCAL_UDP_LOOPBACK.json"
        if args.fixture_profile == "rt2_outer_loop_excitation"
        else "RT1_LOCAL_UDP_LOOPBACK.json"
    )
    fixture_stdout = run_dir / "rt1_local_udp_loopback.stdout.txt"
    fixture_stderr = run_dir / "rt1_local_udp_loopback.stderr.txt"
    wrapper = run_sysplorer_mcp_smoke.resolve_wrapper(args.wrapper)
    client = run_sysplorer_mcp_smoke.JsonlMcpClient(
        run_sysplorer_mcp_smoke.wrapper_command(wrapper), args.log_output
    )

    health: dict[str, Any] | None = None
    root_package_load: dict[str, Any] | None = None
    graphical_dependency_checks: list[dict[str, Any]] = []
    check: dict[str, Any] | None = None
    simulation: dict[str, Any] | None = None
    result_values: dict[str, Any] | None = None
    result_values_by_name: dict[str, Any] | None = None
    fixture_payload: dict[str, Any] | None = None
    fixture_exit_code: int | None = None
    error: str | None = None
    fixture_process: subprocess.Popen[str] | None = None
    simulation_wall_duration_s: float | None = None

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
        if not check.get("ok"):
            raise RuntimeError(f"check_model_failed:{check}")

        # Keep state packets flowing while MWORKS translates the external C
        # function. The receive side drains to the freshest bounded batch, so
        # a separate prewarm simulation is neither required nor desirable.
        fixture_command = [
            sys.executable,
            str(FIXTURE),
            "--host",
            args.host,
            "--port",
            str(args.port),
            "--run-id",
            args.run_id,
            "--rate-hz",
            str(args.rate_hz),
            "--duration-s",
            str(args.fixture_duration_s),
            "--minimum-responses",
            str(args.minimum_responses),
            "--profile",
            args.fixture_profile,
            "--stop-on-pass",
            "--output",
            str(fixture_output),
        ]
        popen_options: dict[str, Any] = {}
        if os.name == "nt":
            popen_options["creationflags"] = subprocess.CREATE_NO_WINDOW
        with fixture_stdout.open("w", encoding="utf-8") as stdout, fixture_stderr.open(
            "w", encoding="utf-8"
        ) as stderr:
            fixture_process = subprocess.Popen(
                fixture_command,
                stdout=stdout,
                stderr=stderr,
                text=True,
                **popen_options,
            )
            time.sleep(0.1)
            simulation_started = time.monotonic()
            simulation = client.call_tool(
                "simulate_model",
                {
                    "model_name": MODEL_NAME,
                    "sim_mode": BATCH_SIM_MODE,
                    "target_time": [0.0, args.simulation_duration_s],
                },
                timeout_s=args.mcp_timeout_s,
            )
            simulation_wall_duration_s = time.monotonic() - simulation_started
            try:
                fixture_exit_code = fixture_process.wait(timeout=args.fixture_duration_s + 10.0)
            except subprocess.TimeoutExpired:
                fixture_process.terminate()
                fixture_exit_code = fixture_process.wait(timeout=10.0)

        fixture_payload = read_json(fixture_output)
        if simulation and simulation.get("ok"):
            result_values = client.call_tool(
                "result_manager",
                {
                    "action": "get_vars_value_at",
                    "model_name": MODEL_NAME,
                    "var_names": RESULT_VARIABLES,
                    "time_point": "end",
                },
                timeout_s=60,
            )
            values = result_values.get("data") if result_values else None
            if isinstance(values, list) and len(values) == len(RESULT_VARIABLES):
                result_values_by_name = dict(zip(RESULT_VARIABLES, values))
    except Exception as exc:  # Preserve all partial runtime evidence.
        error = repr(exc)
        if fixture_process is not None and fixture_process.poll() is None:
            fixture_process.terminate()
            fixture_exit_code = fixture_process.wait(timeout=10.0)
        fixture_payload = read_json(fixture_output)
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
        and simulation
        and simulation.get("ok")
        and fixture_exit_code == 0
        and fixture_payload
        and fixture_payload.get("passed")
    )
    summary = {
        "schema": "mosim.mworks_rt1_graphical_loopback_mcp.v1",
        "source": "MWORKS_MCP_plus_local_udp_fixture",
        "model_name": MODEL_NAME,
        "run_id": args.run_id,
        "live_mworks_touched": True,
        "will_not_click_activation_login": True,
        "load_mode": "project_root_package_only",
        "root_package_check": {
            "attempted": True,
            "path": str(ROOT_PACKAGE),
            "claim_boundary": "The root package provides the source closure; each target still requires check_model.",
        },
        "simulation_executed": True,
        "simulation_mode": BATCH_SIM_MODE,
        "startup_strategy": "fixture_precedes_single_batch_simulation",
        "simulation_duration_s": args.simulation_duration_s,
        "mcp_timeout_s": args.mcp_timeout_s,
        "simulation_wall_duration_s": simulation_wall_duration_s,
        "fixture_started_before_simulation": True,
        "fixture_profile": args.fixture_profile,
        "udp_bridge_executed": True,
        "endpoint": {"host": args.host, "port": args.port},
        "sysplorer_api_port": args.sysplorer_api_port,
        "claim_boundary": (
            "MWORKS real-time graphical-control and local UDP loopback only; "
            "no ROS, PX4, Gazebo, planner, localization, or flight evidence."
        ),
        "passed": passed,
        "error": error,
        "health": health,
        "root_package_load": root_package_load,
        "bridge_model_source": str(BRIDGE_MODEL),
        "graphical_dependency_checks": graphical_dependency_checks,
        "check_model": check,
        "simulate_model": simulation,
        "result_values": result_values,
        "result_values_by_name": result_values_by_name,
        "fixture_exit_code": fixture_exit_code,
        "fixture": fixture_payload,
        "artifact_refs": {
            "mcp_log": str(args.log_output),
            "fixture_json": str(fixture_output),
            "fixture_stdout": str(fixture_stdout),
            "fixture_stderr": str(fixture_stderr),
        },
    }
    args.summary_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "passed": passed,
                "summary_output": str(args.summary_output),
                "fixture_output": str(fixture_output),
                "error": error,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
