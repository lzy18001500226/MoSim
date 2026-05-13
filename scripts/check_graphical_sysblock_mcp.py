#!/usr/bin/env python3
"""Validate graphical AWFF Sysblock controllers through Sysplorer MCP."""

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
    ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(ROOT / "scripts"))
    import run_sysplorer_mcp_smoke  # type: ignore


ROOT = Path(__file__).resolve().parents[1]


MODELS = [
    {
        "model_name": "AWFF_PositionOuterLoop_Sysblock",
        "file": "models/QuadrotorControllerBlocks/AWFF_PositionOuterLoop_Sysblock.mo",
        "verify_result_var": "thrust_ref",
    },
    {
        "model_name": "AWFF_AttitudeInnerLoop_Sysblock",
        "file": "models/QuadrotorControllerBlocks/AWFF_AttitudeInnerLoop_Sysblock.mo",
        "verify_result_var": "roll_cmd",
    },
    {
        "model_name": "AWFF_MotorMixer_Sysblock",
        "file": "models/QuadrotorControllerBlocks/AWFF_MotorMixer_Sysblock.mo",
        "verify_result_var": "y",
    },
    {
        "model_name": "AWFF_FullController_Sysblock",
        "file": "models/QuadrotorControllerBlocks/AWFF_FullController_Sysblock.mo",
        "verify_result_var": "y",
        "extra_files": [
            "models/QuadrotorControllerBlocks/AWFF_PositionOuterLoop_Sysblock.mo",
            "models/QuadrotorControllerBlocks/AWFF_AttitudeInnerLoop_Sysblock.mo",
            "models/QuadrotorControllerBlocks/AWFF_MotorMixer_Sysblock.mo",
        ],
    },
    {
        "model_name": "AWFF_FullControllerFlatGraphical_Sysblock",
        "file": "models/QuadrotorControllerBlocks/AWFF_FullControllerFlatGraphical_Sysblock.mo",
        "verify_result_var": "y",
    },
]


INNOVATION_MODELS = [
    {
        "model_name": "AWFF_InnovationGraphicalControllers",
        "file": "models/QuadrotorControllerBlocks/AWFF_InnovationGraphicalControllers.mo",
        "verify_result_var": "l1_residual_overview.y",
    },
    {
        "model_name": "AWFF_InnovationGraphicalControllers.MotorMixerBlock",
        "file": "models/QuadrotorControllerBlocks/AWFF_InnovationGraphicalControllers.mo",
        "verify_result_var": "y",
    },
    {
        "model_name": "AWFF_InnovationGraphicalControllers.INDIAttitudeInnerLoopBlock",
        "file": "models/QuadrotorControllerBlocks/AWFF_InnovationGraphicalControllers.mo",
        "verify_result_var": "roll_cmd",
    },
    {
        "model_name": "AWFF_InnovationGraphicalControllers.KnownRotorFaultMixerBlock",
        "file": "models/QuadrotorControllerBlocks/AWFF_InnovationGraphicalControllers.mo",
        "verify_result_var": "y",
    },
    {
        "model_name": "AWFF_InnovationGraphicalControllers.RotorFaultIsolationBlock",
        "file": "models/QuadrotorControllerBlocks/AWFF_InnovationGraphicalControllers.mo",
        "verify_result_var": "fault_index",
    },
    {
        "model_name": "AWFF_InnovationGraphicalControllers.AdaptiveFaultMixerBlock",
        "file": "models/QuadrotorControllerBlocks/AWFF_InnovationGraphicalControllers.mo",
        "verify_result_var": "y",
    },
    {
        "model_name": "AWFF_InnovationGraphicalControllers.LinearMPCOuterLoopBlock",
        "file": "models/QuadrotorControllerBlocks/AWFF_InnovationGraphicalControllers.mo",
        "verify_result_var": "thrust_ref",
    },
    {
        "model_name": "AWFF_InnovationGraphicalControllers.Rotor1OnlineEfficiencyEstimatorBlock",
        "file": "models/QuadrotorControllerBlocks/AWFF_InnovationGraphicalControllers.mo",
        "verify_result_var": "eta_hat",
    },
    {
        "model_name": "AWFF_InnovationGraphicalControllers.AWFF_L1ResidualControllerGraphical_Sysblock",
        "file": "models/QuadrotorControllerBlocks/AWFF_InnovationGraphicalControllers.mo",
        "verify_result_var": "y",
    },
    {
        "model_name": "AWFF_InnovationGraphicalControllers.AWFF_INDIControllerGraphical_Sysblock",
        "file": "models/QuadrotorControllerBlocks/AWFF_InnovationGraphicalControllers.mo",
        "verify_result_var": "y",
    },
    {
        "model_name": "AWFF_InnovationGraphicalControllers.AWFF_L1FaultAllocationControllerGraphical_Sysblock",
        "file": "models/QuadrotorControllerBlocks/AWFF_InnovationGraphicalControllers.mo",
        "verify_result_var": "y",
    },
    {
        "model_name": "AWFF_InnovationGraphicalControllers.AWFF_L1MultiFaultIsolationControllerGraphical_Sysblock",
        "file": "models/QuadrotorControllerBlocks/AWFF_InnovationGraphicalControllers.mo",
        "verify_result_var": "fault_index",
    },
    {
        "model_name": "AWFF_InnovationGraphicalControllers.AWFF_L1OnlineFaultAllocationControllerGraphical_Sysblock",
        "file": "models/QuadrotorControllerBlocks/AWFF_InnovationGraphicalControllers.mo",
        "verify_result_var": "eta_hat",
    },
    {
        "model_name": "AWFF_InnovationGraphicalControllers.AWFF_FaultCompensationControllerGraphical_Sysblock",
        "file": "models/QuadrotorControllerBlocks/AWFF_InnovationGraphicalControllers.mo",
        "verify_result_var": "y",
    },
    {
        "model_name": "AWFF_InnovationGraphicalControllers.AWFF_LinearMPCControllerGraphical_Sysblock",
        "file": "models/QuadrotorControllerBlocks/AWFF_InnovationGraphicalControllers.mo",
        "verify_result_var": "y",
    },
    {
        "model_name": "AWFF_InnovationGraphicalControllers.AWFF_LinearMPCOnlineFaultAllocationControllerGraphical_Sysblock",
        "file": "models/QuadrotorControllerBlocks/AWFF_InnovationGraphicalControllers.mo",
        "verify_result_var": "eta_hat",
    },
]


def windows_path(repo_path: str) -> str:
    return "C:\\Users\\HP\\Desktop\\Quadrotor\\" + repo_path.replace("/", "\\")


def load_file(client: Any, repo_path: str) -> dict[str, Any]:
    return client.call_tool(
        "model_manager",
        {
            "action": "load_file",
            "file_path": windows_path(repo_path),
            "force_reload": True,
            "auto_load_deps": True,
        },
        timeout_s=300,
    )


def validate_one(client: Any, item: dict[str, Any], simulate: bool) -> dict[str, Any]:
    loads = []
    for extra_file in item.get("extra_files", []):
        loads.append({"file": extra_file, "result": load_file(client, extra_file)})
    loads.append({"file": item["file"], "result": load_file(client, item["file"])})

    check_result = client.call_tool(
        "check_model",
        {"model_name": item["model_name"], "stop_on_error": True},
        timeout_s=300,
    )

    simulate_result: dict[str, Any] | None = None
    if simulate and check_result.get("ok"):
        simulate_result = client.call_tool(
            "simulate_model",
            {
                "model_name": item["model_name"],
                "sim_mode": 0,
                "target_time": [0, 1],
                "verify_result_var": item["verify_result_var"],
                "verify_time_point": "end",
            },
            timeout_s=360,
        )

    return {
        "model_name": item["model_name"],
        "file": item["file"],
        "verify_result_var": item["verify_result_var"],
        "load_ok": all(load["result"].get("ok") for load in loads),
        "check_ok": bool(check_result.get("ok")),
        "simulate_ok": None if simulate_result is None else bool(simulate_result.get("ok")),
        "loads": loads,
        "check_result": check_result,
        "simulate_result": simulate_result,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log-output", type=Path, default=ROOT / "results/model_checks/awff_sysblock/logs/sysplorer_graphical_sysblock_controller_check_20260511.jsonl")
    parser.add_argument("--summary-output", type=Path, default=ROOT / "results/model_checks/awff_sysblock/logs/sysplorer_graphical_sysblock_controller_check_20260511_summary.json")
    parser.add_argument("--no-simulate", action="store_true", help="Only run load_file and check_model")
    parser.add_argument("--include-innovation", action="store_true", help="Also check L1/INDI/fault-isolation graphical controller package")
    parser.add_argument("--innovation-only", action="store_true", help="Check only L1/INDI/fault-isolation graphical controller package")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.log_output.parent.mkdir(parents=True, exist_ok=True)
    wrapper = run_sysplorer_mcp_smoke.resolve_wrapper(os.environ.get("SYSPLORER_MCP_WRAPPER"))
    client = run_sysplorer_mcp_smoke.JsonlMcpClient([wrapper], args.log_output)
    try:
        health = run_sysplorer_mcp_smoke.initialize_mcp_client(client)
        selected_models = []
        if not args.innovation_only:
            selected_models.extend(MODELS)
        if args.include_innovation or args.innovation_only:
            selected_models.extend(INNOVATION_MODELS)
        results = [validate_one(client, item, not args.no_simulate) for item in selected_models]
    finally:
        print("Shutdown: skipped; Sysplorer GUI/session left reusable")
        client.close()

    summary = {
        "source": "MWORKS_MCP",
        "evidence_level": "real_sysplorer_mcp_graphical_sysblock_controller_check",
        "health_ok": bool(health.get("ok") and health.get("driver_ready")),
        "models_checked": len(results),
        "all_check_ok": all(item["check_ok"] for item in results),
        "all_simulate_ok": None if args.no_simulate else all(item["simulate_ok"] is True for item in results),
        "results": results,
    }
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "health_ok": summary["health_ok"],
        "models_checked": summary["models_checked"],
        "all_check_ok": summary["all_check_ok"],
        "all_simulate_ok": summary["all_simulate_ok"],
        "summary_output": args.summary_output.as_posix(),
        "log_output": args.log_output.as_posix(),
    }, ensure_ascii=False, indent=2))
    simulate_gate = True if args.no_simulate else bool(summary["all_simulate_ok"])
    return 0 if summary["health_ok"] and summary["all_check_ok"] and simulate_gate else 1


if __name__ == "__main__":
    raise SystemExit(main())
