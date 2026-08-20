#!/usr/bin/env python3
"""Run the RT1 graphical bridge smoke through an explicitly attached Sysplorer port."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import mworks.sysplorer as ModelingPy


ROOT = Path(__file__).resolve().parents[2]
MODEL_NAME = "MoSimQuadrotorModel.RealTime.MworksRt1Px4CtrlGraphicalShadow100Hz"
RESULT_VARIABLES = (
    "exchangeCallCount",
    "sampleTicks",
    "processedFrames",
    "sentFrames",
    "socketReady",
    "socketErrorCode",
)


def capture_call(name: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
    try:
        value = getattr(ModelingPy, name)(*args, **kwargs)
        json.dumps(value, ensure_ascii=False)
        return {"ok": True, "data": value}
    except Exception as exc:
        return {"ok": False, "error": repr(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, required=True, help="Existing Sysplorer API port only")
    parser.add_argument("--stop-time-s", type=float, default=0.03)
    parser.add_argument("--translate-only", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "Results/mworks_live_gate/rt1_graphical_bridge/direct_port/RT1_DIRECT_PORT_SMOKE.json",
    )
    args = parser.parse_args()

    if args.port <= 0 or args.stop_time_s <= 0:
        raise SystemExit("port and stop-time-s must be positive")

    result: dict[str, Any] = {
        "schema": "mosim.mworks_rt1_graphical_bridge_direct_port.v1",
        "source": "MWORKS_ModelingPy_direct",
        "model_name": MODEL_NAME,
        "existing_sysplorer_port": args.port,
        "live_mworks_touched": True,
        "will_not_click_activation_login": True,
        "simulation_api": "ModelingPy.SimulateModel",
        "simulation_mode": 0,
        "stop_time_s": args.stop_time_s,
        "translate_only": args.translate_only,
        "claim_boundary": "MWORKS RT1 graphical bridge smoke without a UDP peer; no ROS, PX4, Gazebo, planner, localization, or flight evidence.",
    }

    result["connect"] = capture_call("ConnectSysplorer", "127.0.0.1", args.port)
    result["class_exists"] = capture_call("ClassExist", MODEL_NAME)
    result["check_model"] = capture_call("CheckModel", MODEL_NAME)
    if result["connect"].get("ok") and result["check_model"].get("data") is True:
        if args.translate_only:
            result["translate_model"] = capture_call("TranslateModel", MODEL_NAME)
            result["simulate_model"] = {"ok": False, "skipped": True}
        else:
            result["simulate_model"] = capture_call(
                "SimulateModel",
                MODEL_NAME,
                startTime=0.0,
                stopTime=args.stop_time_s,
                interval=0.01,
                simMode=0,
                path="",
            )
    else:
        result["simulate_model"] = {"ok": False, "skipped": True}

    result["post_simulation_diagnostics"] = {
        name: capture_call(name)
        for name in (
            "GetSimulationExitState",
            "GetSimulationState",
            "GetCurrentSimTime",
            "MessageText",
            "GetLastErrors",
        )
    }
    values: dict[str, Any] = {}
    simulation_ok = result["simulate_model"].get("data") is True
    if simulation_ok:
        for variable in RESULT_VARIABLES:
            probe = capture_call("GetVarValueAt", variable, "end")
            value = probe.get("data")
            probe["finite"] = (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(float(value))
            )
            values[variable] = probe
    result["result_values_at_end"] = values
    result["compiler_diagnostics"] = {
        name: capture_call(name)
        for name in ("GetCompileSolver64", "MwCompilerType")
    }

    result_values_ok = all(item.get("ok") and item.get("finite") for item in values.values())
    translation_ok = result.get("translate_model", {}).get("data") is True
    result["passed"] = bool(
        result["connect"].get("ok")
        and result["class_exists"].get("data") is True
        and result["check_model"].get("data") is True
        and ((args.translate_only and translation_ok) or (simulation_ok and result_values_ok))
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "output": str(args.output)}, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
