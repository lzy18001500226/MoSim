#!/usr/bin/env python3
"""Static contract for the optimized pure-graphical ss controller."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/ProjectOwned/MoSim_OptimizedSSGraphicalController.mo"
RESULT_MODEL_PATH = ROOT / "Results/control_optimization_ss_graphical/models/graphical/MoSim_OptimizedSSGraphicalController.mo"
MODEL_NAME = "MoSim_OptimizedSSGraphicalController"
EXPECTED_INPUTS = {"x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"}
EXPECTED_OUTPUTS = {"y", "y1", "y2", "y3"}
EXPECTED_SS = {"x_outer_ss", "y_outer_ss", "z_outer_ss", "roll_inner_ss", "pitch_inner_ss", "yaw_inner_ss"}


def check(path: Path, *, require_within: bool) -> dict:
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    models = re.findall(r"\bmodel\s+([A-Za-z_]\w*)\b", text)
    inputs = set(re.findall(r"SysplorerEmbeddedCoder\.Port\.Inport\s+(\w+)", text))
    outputs = set(re.findall(r"SysplorerEmbeddedCoder\.Port\.Outport\s+(\w+)", text))
    ss_blocks = set(re.findall(r"SysplorerEmbeddedCoder\.Discrete\.DiscreteStateSpace\s+(\w+)", text))
    forbidden_tokens = [
        "SysplorerEmbeddedCoder.Utilities.CFunction",
        "SysplorerEmbeddedCoder.Utilities.CCaller",
        "Equation_Sysblock",
        "Modelica.Blocks",
        "function ",
    ]
    required_connections = [
        "connect(roll_ref_limit.y, roll_error.u1)",
        "connect(pitch_ref_limit.y, pitch_error.u1)",
        "connect(thrust_command_sum.y, thrust_limit.u)",
        "connect(m1_mix_sum.y, m1_limit.u)",
        "connect(m4_mix_sum.y, m4_limit.u)",
    ]
    forbidden_connections = [
        "connect(y_outer_ss.y, roll_error.u1)",
        "connect(x_outer_ss.y, pitch_error.u1)",
    ]
    missing_parameters = {
        block: [parameter for parameter in ("A", "B", "C", "D") if not re.search(rf"\b{parameter}=", text[text.find(block):text.find(block) + 500])]
        for block in EXPECTED_SS
        if block in text
    }
    missing_parameters = {block: values for block, values in missing_parameters.items() if values}
    result = {
        "schema": "mosim.optimized_ss_graphical_controller.static_check.v1",
        "source": "static_model_contract",
        "path": path.as_posix(),
        "exists": path.is_file(),
        "model_name_present": MODEL_NAME in models,
        "inputs": sorted(inputs),
        "outputs": sorted(outputs),
        "state_space_blocks": sorted(ss_blocks),
        "input_contract_ok": EXPECTED_INPUTS <= inputs,
        "output_contract_ok": EXPECTED_OUTPUTS <= outputs,
        "state_space_contract_ok": EXPECTED_SS <= ss_blocks and len(ss_blocks) == 6,
        "parameter_contract_ok": not missing_parameters,
        "forbidden_tokens": [token for token in forbidden_tokens if token in text],
        "required_connections_ok": all(token in text for token in required_connections),
        "forbidden_connections": [token for token in forbidden_connections if token in text],
        "connection_count": text.count("connect("),
        "within_package_ok": (
            text.startswith("within MoSimQuadrotorModel.Control.Implementations.Graphical.ProjectOwned;")
            if require_within
            else True
        ),
        "missing_parameters": missing_parameters,
    }
    result["pure_graphical_ss_ok"] = bool(
        result["exists"]
        and result["model_name_present"]
        and result["input_contract_ok"]
        and result["output_contract_ok"]
        and result["state_space_contract_ok"]
        and result["parameter_contract_ok"]
        and not result["forbidden_tokens"]
        and result["required_connections_ok"]
        and not result["forbidden_connections"]
        and result["connection_count"] >= 60
        and result["within_package_ok"]
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    result = {
        "source_model": check(MODEL_PATH, require_within=True),
        "result_model": check(RESULT_MODEL_PATH, require_within=False),
    }
    result["ok"] = bool(result["source_model"]["pure_graphical_ss_ok"] and result["result_model"]["pure_graphical_ss_ok"])
    if args.json_output:
        output = args.json_output if args.json_output.is_absolute() else ROOT / args.json_output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
