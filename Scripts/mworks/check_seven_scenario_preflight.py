#!/usr/bin/env python3
"""Record native MWORKS model-integrity evidence for the seven-scenario gate.

This entrypoint intentionally performs package loading and model checks only.
It does not start a solver, extract result data, or create simulation evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = ROOT / "Models" / "MoSimQuadrotorModel"
MODEL_FILE = MODEL_ROOT / "package.mo"
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "control_platform" / "seven_scenario_preflight_20260727"

TRAJECTORY_MODELS = (
    "MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath",
    "MoSimQuadrotorModel.Guidance.Trajectories.HoverHold",
    "MoSimQuadrotorModel.Guidance.Trajectories.StepResponse",
    "MoSimQuadrotorModel.Guidance.Trajectories.Figure8",
    "MoSimQuadrotorModel.Guidance.Trajectories.SpiralAscent",
    "MoSimQuadrotorModel.Guidance.Trajectories.WindDisturbance",
    "MoSimQuadrotorModel.Guidance.Trajectories.ParameterMismatch",
    "MoSimQuadrotorModel.Guidance.Trajectories.MotorFault",
)
SHARED_RUNNER_MODELS = (
    "MoSimQuadrotorModel.Experiment.Runners.AttitudeThrustRunner",
    "MoSimQuadrotorModel.Experiment.Runners.BodyRateThrustRunner",
    "MoSimQuadrotorModel.Experiment.Runners.RotorCommandRunner",
    "MoSimQuadrotorModel.Experiment.Runners.WrenchRunner",
)
FORMAL_RUNNER_MODELS = (
    "MoSimQuadrotorModel.Experiment.Runners.OfficialPidFormalRunner",
    "MoSimQuadrotorModel.Experiment.Runners.CascadePidFormalRunner",
    "MoSimQuadrotorModel.Experiment.Runners.LqrBaselineFormalRunner",
    "MoSimQuadrotorModel.Experiment.Runners.SuperTwistingSmcFormalRunner",
    "MoSimQuadrotorModel.Experiment.Runners.LinearMpcFormalRunner",
    "MoSimQuadrotorModel.Experiment.Runners.DfbcHighOrderFormalRunner",
    "MoSimQuadrotorModel.Experiment.Runners.TrainedNeuralResidualFormalRunner",
    "MoSimQuadrotorModel.Experiment.Runners.Px4CtrlFormalRunner",
)
TARGETS = TRAJECTORY_MODELS + SHARED_RUNNER_MODELS + FORMAL_RUNNER_MODELS
ALLOWED_MCP_TOOLS = frozenset({"session_manager", "model_manager", "check_model"})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def source_hashes() -> dict[str, str]:
    paths = [
        MODEL_FILE,
        ROOT / "Config" / "control_platform" / "seven_scenario_injection_contract.json",
        ROOT / "Config" / "control_platform" / "seven_scenario_experiment_profiles.json",
        MODEL_ROOT / "Vehicle" / "Sunray150Assembly.mo",
        MODEL_ROOT / "Vehicle" / "Dynamics" / "PhysicalWrenchAdapter.mo",
        MODEL_ROOT / "Vehicle" / "Dynamics" / "RotorActuatorCore.mo",
    ]
    paths.extend(
        MODEL_ROOT / "Guidance" / "Trajectories" / f"{model.rsplit('.', 1)[-1]}.mo"
        for model in TRAJECTORY_MODELS[1:]
    )
    paths.extend(
        MODEL_ROOT / "Experiment" / "Runners" / f"{model.rsplit('.', 1)[-1]}.mo"
        for model in SHARED_RUNNER_MODELS + FORMAL_RUNNER_MODELS
    )
    return {
        path.relative_to(ROOT).as_posix(): sha256(path)
        for path in paths
        if path.is_file()
    }


def run_check_only(*, output_dir: Path, wrapper: str | None, timeout_s: float) -> tuple[dict[str, Any], int]:
    sys.path.insert(0, str(ROOT / "Scripts" / "mworks"))
    import run_sysplorer_mcp_smoke as mcp  # type: ignore

    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "SYSPLORER_MCP_CHECK_ONLY.jsonl"
    summary_path = output_dir / "CHECK_MODEL_RESULTS.json"
    log_path.write_text("", encoding="utf-8")
    started_at = time.time()
    record: dict[str, Any] = {
        "schema": "mosim.seven_scenario_preflight_check_model.v1",
        "status": "running",
        "source": "MWORKS_MCP",
        "claim_boundary": "Native package loading and CheckModel integrity evidence only. No scenario simulation, result extraction, metric calculation, controller ranking, code generation, or runtime validation has run.",
        "live_mworks_touched": True,
        "scenario_simulation_started": False,
        "solver_started": False,
        "allowed_mcp_tools": sorted(ALLOWED_MCP_TOOLS),
        "model_root": MODEL_FILE.relative_to(ROOT).as_posix(),
        "model_root_sha256": sha256(MODEL_FILE),
        "source_sha256": source_hashes(),
        "profiles_path": "Config/control_platform/seven_scenario_experiment_profiles.json",
        "targets": list(TARGETS),
        "target_count": len(TARGETS),
        "raw_mcp_log": log_path.relative_to(ROOT).as_posix(),
        "started_at_unix": started_at,
    }
    client: Any | None = None
    exit_code = 1
    try:
        resolved_wrapper = mcp.resolve_wrapper(wrapper)
        record["wrapper"] = resolved_wrapper
        client = mcp.JsonlMcpClient(mcp.wrapper_command(resolved_wrapper), log_path)
        record["health"] = mcp.initialize_mcp_client(client)
        record["load_root"] = client.call_tool(
            "model_manager",
            {
                "action": "load_file",
                "file_path": mcp.windows_path(MODEL_FILE),
                "force_reload": True,
                "auto_load_deps": True,
            },
            timeout_s=timeout_s,
        )
        checks: list[dict[str, Any]] = []
        for model_name in TARGETS:
            result = client.call_tool(
                "check_model",
                {"model_name": model_name, "stop_on_error": True},
                timeout_s=timeout_s,
            )
            checks.append({"model_name": model_name, "ok": bool(result.get("ok")), "result": result})
        record["checks"] = checks
        record["all_requested_models_checked"] = len(checks) == len(TARGETS)
        record["all_passed"] = bool(record["load_root"].get("ok")) and all(item["ok"] for item in checks)
        record["status"] = "passed" if record["all_passed"] else "failed"
        exit_code = 0 if record["status"] == "passed" else 1
    except Exception as exc:
        record["status"] = "blocked"
        record["error"] = repr(exc)
    finally:
        if client is not None:
            client.close()
        record["completed_at_unix"] = time.time()
        record["elapsed_s"] = record["completed_at_unix"] - started_at
        write_json(summary_path, record)
    return record, exit_code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--wrapper", help="Override the local Sysplorer MCP wrapper")
    parser.add_argument("--timeout-s", type=float, default=300.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    record, exit_code = run_check_only(output_dir=output_dir, wrapper=args.wrapper, timeout_s=args.timeout_s)
    print(
        json.dumps(
            {
                "status": record["status"],
                "target_count": record["target_count"],
                "all_passed": record.get("all_passed", False),
                "summary": (output_dir / "CHECK_MODEL_RESULTS.json").relative_to(ROOT).as_posix(),
                "raw_mcp_log": (output_dir / "SYSPLORER_MCP_CHECK_ONLY.jsonl").relative_to(ROOT).as_posix(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
