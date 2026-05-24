#!/usr/bin/env python3
"""Static acceptance checks for project graphical Sysblock controllers."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


BEHAVIOR_EXPECTATIONS: dict[str, list[str]] = {
    "AWFF_FullControllerFlatGraphical_Sysblock.mo": [
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
        "SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator",
    ],
    "AWFF_InnovationGraphicalControllers.L1ResidualOuterLoopBlock": [
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
        "SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator",
    ],
    "AWFF_InnovationGraphicalControllers.PIDAttitudeInnerLoopBlock": [
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
    ],
    "AWFF_InnovationGraphicalControllers.INDIAttitudeInnerLoopBlock": [
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
        "SysplorerEmbeddedCoder.Discrete.UnitDelay",
    ],
    "AWFF_InnovationGraphicalControllers.MotorMixerBlock": [
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
    ],
    "AWFF_InnovationGraphicalControllers.KnownRotorFaultMixerBlock": [
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
    ],
    "AWFF_InnovationGraphicalControllers.RotorFaultIsolationBlock": [
        "SysplorerEmbeddedCoder.Discontinuities.DeadZone",
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
        "SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator",
        "SysplorerEmbeddedCoder.SignalRouting.Switch",
    ],
    "AWFF_InnovationGraphicalControllers.AdaptiveFaultMixerBlock": [
        "SysplorerEmbeddedCoder.MathOperation.Product",
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
    ],
    "AWFF_InnovationGraphicalControllers.LinearMPCOuterLoopBlock": [
        "SysplorerEmbeddedCoder.Discrete.UnitDelay",
        "SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator",
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
    ],
    "AWFF_InnovationGraphicalControllers.Rotor1OnlineEfficiencyEstimatorBlock": [
        "SysplorerEmbeddedCoder.Discontinuities.DeadZone",
        "SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator",
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
    ],
    "AWFF_InnovationGraphicalControllers.AWFF_L1OnlineFaultAllocationControllerGraphical_Sysblock": [
        "L1ResidualOuterLoopBlock",
        "Rotor1OnlineEfficiencyEstimatorBlock",
        "AdaptiveFaultMixerBlock",
    ],
    "AWFF_InnovationGraphicalControllers.AWFF_FaultCompensationControllerGraphical_Sysblock": [
        "L1ResidualOuterLoopBlock",
        "PIDAttitudeInnerLoopBlock",
        "KnownRotorFaultMixerBlock",
    ],
    "AWFF_InnovationGraphicalControllers.AWFF_LinearMPCControllerGraphical_Sysblock": [
        "LinearMPCOuterLoopBlock",
        "INDIAttitudeInnerLoopBlock",
        "MotorMixerBlock",
    ],
    "AWFF_InnovationGraphicalControllers.AWFF_LinearMPCOnlineFaultAllocationControllerGraphical_Sysblock": [
        "LinearMPCOuterLoopBlock",
        "Rotor1OnlineEfficiencyEstimatorBlock",
        "AdaptiveFaultMixerBlock",
    ],
}


REQUIRED_MODELS: dict[str, dict[str, Any]] = {
    "AWFF_PositionOuterLoop_Sysblock.mo": {
        "inports": ["x_error", "y_error", "z_error", "z_ref_rate"],
        "outports": ["pitch_ref", "roll_ref", "thrust_ref"],
        "required_blocks": ["x_kp", "x_kd", "x_sum", "x_scale", "y_kp", "y_kd", "y_sum", "y_scale", "z_kp", "z_ki", "z_kd", "z_ff", "z_sum"],
        "min_connects": 20,
    },
    "AWFF_AttitudeInnerLoop_Sysblock.mo": {
        "inports": ["roll_ref", "pitch_ref", "yaw_ref", "roll_mea", "pitch_mea", "yaw_mea"],
        "outports": ["roll_cmd", "pitch_cmd", "yaw_cmd"],
        "required_blocks": ["roll_error", "roll_kp", "roll_kd", "roll_sum", "pitch_error", "pitch_kp", "pitch_kd", "pitch_sum", "yaw_error", "yaw_kp"],
        "min_connects": 18,
    },
    "AWFF_MotorMixer_Sysblock.mo": {
        "inports": ["thrust_ref", "roll_cmd", "pitch_cmd", "yaw_cmd"],
        "outports": ["y", "y1", "y2", "y3"],
        "required_blocks": ["neg_roll", "neg_pitch", "neg_yaw", "motor1_sum", "motor2_sum", "motor3_sum", "motor4_sum"],
        "min_connects": 23,
    },
    "AWFF_FullController_Sysblock.mo": {
        "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
        "outports": ["y", "y1", "y2", "y3"],
        "required_blocks": ["position_loop", "attitude_loop", "motor_mixer"],
        "required_references": ["AWFF_PositionOuterLoop_Sysblock", "AWFF_AttitudeInnerLoop_Sysblock", "AWFF_MotorMixer_Sysblock"],
        "min_connects": 18,
    },
    "AWFF_FullControllerFlatGraphical_Sysblock.mo": {
        "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
        "outports": ["y", "y1", "y2", "y3"],
        "required_blocks": ["x_kp", "x_kd", "x_sum", "pitch_ref_scale", "y_kp", "y_kd", "y_sum", "roll_ref_scale", "z_kp", "z_ki", "z_kd", "z_ff", "thrust_sum", "roll_error", "roll_cmd_sum", "pitch_error", "pitch_cmd_sum", "yaw_error", "motor1_sum", "motor2_sum", "motor3_sum", "motor4_sum"],
        "min_connects": 60,
    },
}


PACKAGE_MODELS: dict[str, dict[str, dict[str, Any]]] = {
    "AWFF_InnovationGraphicalControllers.mo": {
        "INDIAttitudeInnerLoopBlock": {
            "inports": ["roll_ref", "pitch_ref", "yaw_ref", "roll_mea", "pitch_mea", "yaw_mea"],
            "outports": ["roll_cmd", "pitch_cmd", "yaw_cmd"],
            "required_blocks": [
                "roll_error_sum",
                "roll_kp_gain",
                "roll_indi_gain_block",
                "pitch_error_sum",
                "pitch_kp_gain",
                "pitch_indi_gain_block",
                "yaw_error_sum",
                "yaw_kp_gain",
                "yaw_indi_gain_block",
            ],
            "min_connects": 27,
        },
        "MotorMixerBlock": {
            "inports": ["thrust_ref", "roll_cmd", "pitch_cmd", "yaw_cmd"],
            "outports": ["y", "y1", "y2", "y3"],
            "required_blocks": [
                "roll_pos",
                "roll_neg",
                "pitch_pos",
                "pitch_neg",
                "yaw_pos",
                "yaw_neg",
                "thrust_neg",
                "motor1_sum",
                "motor2_sum",
                "motor3_sum",
                "motor4_sum",
            ],
            "min_connects": 23,
        },
        "KnownRotorFaultMixerBlock": {
            "inports": ["thrust_ref", "roll_cmd", "pitch_cmd", "yaw_cmd"],
            "outports": ["y", "y1", "y2", "y3"],
            "required_blocks": ["raw_mixer", "rotor1_comp_gain"],
            "min_connects": 5,
        },
        "RotorFaultIsolationBlock": {
            "inports": ["x_error", "y_error"],
            "outports": ["eta_hat1", "eta_hat2", "eta_hat3", "eta_hat4", "fault_index"],
            "required_blocks": ["neg_x_half", "pos_x_half", "neg_y_half", "pos_y_half", "sig1_sum", "eta1_gain", "eta1_raw_sum"],
            "min_connects": 24,
        },
        "AdaptiveFaultMixerBlock": {
            "inports": ["thrust_ref", "roll_cmd", "pitch_cmd", "yaw_cmd", "eta_hat1", "eta_hat2", "eta_hat3", "eta_hat4"],
            "outports": ["y", "y1", "y2", "y3"],
            "required_blocks": ["raw_mixer"],
            "min_connects": 4,
        },
        "AWFF_L1ResidualControllerGraphical_Sysblock": {
            "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
            "outports": ["y", "y1", "y2", "y3"],
            "required_blocks": ["l1_outer", "attitude_loop", "motor_mixer", "L1ResidualOuterLoopBlock", "PIDAttitudeInnerLoopBlock", "MotorMixerBlock"],
            "min_connects": 18,
        },
        "AWFF_INDIControllerGraphical_Sysblock": {
            "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
            "outports": ["y", "y1", "y2", "y3"],
            "required_blocks": ["l1_outer", "attitude_loop", "motor_mixer", "L1ResidualOuterLoopBlock", "INDIAttitudeInnerLoopBlock", "MotorMixerBlock"],
            "min_connects": 18,
        },
        "AWFF_L1FaultAllocationControllerGraphical_Sysblock": {
            "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
            "outports": ["y", "y1", "y2", "y3"],
            "required_blocks": ["l1_outer", "attitude_loop", "motor_mixer", "L1ResidualOuterLoopBlock", "PIDAttitudeInnerLoopBlock", "KnownRotorFaultMixerBlock"],
            "min_connects": 18,
        },
        "AWFF_L1MultiFaultIsolationControllerGraphical_Sysblock": {
            "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
            "outports": ["y", "y1", "y2", "y3", "eta_hat1", "eta_hat2", "eta_hat3", "eta_hat4", "fault_index"],
            "required_blocks": ["l1_outer", "attitude_loop", "motor_mixer", "fault_isolation", "L1ResidualOuterLoopBlock", "PIDAttitudeInnerLoopBlock", "AdaptiveFaultMixerBlock", "RotorFaultIsolationBlock"],
            "min_connects": 29,
        },
        "AWFF_L1OnlineFaultAllocationControllerGraphical_Sysblock": {
            "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
            "outports": ["y", "y1", "y2", "y3", "eta_hat"],
            "required_blocks": ["l1_outer", "attitude_loop", "motor_mixer", "rotor1_eta_estimator", "L1ResidualOuterLoopBlock", "PIDAttitudeInnerLoopBlock", "AdaptiveFaultMixerBlock", "Rotor1OnlineEfficiencyEstimatorBlock"],
            "min_connects": 24,
        },
        "AWFF_FaultCompensationControllerGraphical_Sysblock": {
            "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
            "outports": ["y", "y1", "y2", "y3"],
            "required_blocks": ["awff_outer", "attitude_loop", "motor_mixer", "L1ResidualOuterLoopBlock", "PIDAttitudeInnerLoopBlock", "KnownRotorFaultMixerBlock"],
            "min_connects": 18,
        },
        "LinearMPCOuterLoopBlock": {
            "inports": ["x_error", "y_error", "z_error", "z_ref_rate"],
            "outports": ["pitch_ref", "roll_ref", "thrust_ref"],
            "required_blocks": [
                "x_error_delay",
                "x_horizon_gain",
                "x_terminal_sum",
                "x_l1_filter",
                "x_acc_sat",
                "pitch_ref_sat",
                "y_error_delay",
                "y_horizon_gain",
                "y_terminal_sum",
                "y_l1_filter",
                "y_acc_sat",
                "roll_ref_sat",
                "z_error_delay",
                "z_horizon_gain",
                "z_terminal_sum",
                "z_integrator",
                "z_l1_filter_mpc",
                "thrust_sat",
            ],
            "min_connects": 75,
        },
        "Rotor1OnlineEfficiencyEstimatorBlock": {
            "inports": ["x_error", "y_error"],
            "outports": ["eta_hat"],
            "required_blocks": [
                "eta_signature_sum",
                "eta_signature_deadzone",
                "eta_drop_filter",
                "eta_raw_sum",
                "eta_sat",
            ],
            "min_connects": 11,
        },
        "AWFF_LinearMPCControllerGraphical_Sysblock": {
            "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
            "outports": ["y", "y1", "y2", "y3"],
            "required_blocks": ["mpc_outer", "attitude_loop", "motor_mixer", "LinearMPCOuterLoopBlock", "INDIAttitudeInnerLoopBlock", "MotorMixerBlock"],
            "min_connects": 18,
        },
        "AWFF_LinearMPCOnlineFaultAllocationControllerGraphical_Sysblock": {
            "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
            "outports": ["y", "y1", "y2", "y3", "eta_hat"],
            "required_blocks": ["mpc_outer", "attitude_loop", "motor_mixer", "rotor1_eta_estimator", "LinearMPCOuterLoopBlock", "INDIAttitudeInnerLoopBlock", "AdaptiveFaultMixerBlock", "Rotor1OnlineEfficiencyEstimatorBlock"],
            "min_connects": 24,
        },
    },
}


def find_port_names(text: str, port_kind: str) -> list[str]:
    pattern = re.compile(rf"SysplorerEmbeddedCoder\.Port\.{port_kind}\s+([A-Za-z_][A-Za-z0-9_]*)")
    return pattern.findall(text)


def top_level_model_text(text: str) -> str:
    """Return declarations before nested model definitions.

    Hierarchical Sysblock controllers may embed child models so a standalone
    parent file can be opened without preloading dependencies. Static port
    checks should still report only the parent model interface.
    """

    match = re.search(r"^  model\s+[A-Za-z_][A-Za-z0-9_]*\b", text, re.MULTILINE)
    return text[: match.start()] if match else text


def named_model_text(text: str, model_name: str) -> str:
    match = re.search(rf"^  model\s+{re.escape(model_name)}\b", text, re.MULTILINE)
    if not match:
        return ""
    end_match = re.search(rf"^  end\s+{re.escape(model_name)};", text[match.start() :], re.MULTILINE)
    if not end_match:
        return text[match.start() :]
    return text[match.start() : match.start() + end_match.end()]


def check_text(
    interface_text: str,
    path: Path,
    spec: dict[str, Any],
    label: str | None = None,
    structure_text: str | None = None,
) -> dict[str, Any]:
    if structure_text is None:
        structure_text = interface_text
    inports = find_port_names(interface_text, "Inport")
    outports = find_port_names(interface_text, "Outport")
    connect_count = structure_text.count("connect(")
    line_count = structure_text.count("annotation(Line")
    placement_count = structure_text.count("Placement(")

    missing_inports = [name for name in spec["inports"] if name not in inports]
    missing_outports = [name for name in spec["outports"] if name not in outports]
    missing_blocks = [
        name
        for name in spec.get("required_blocks", [])
        if not re.search(rf"\b{name}\b", structure_text)
    ]
    missing_refs = [
        name
        for name in spec.get("required_references", [])
        if name not in structure_text
    ]

    failures: list[str] = []
    if missing_inports:
        failures.append(f"missing inports: {', '.join(missing_inports)}")
    if missing_outports:
        failures.append(f"missing outports: {', '.join(missing_outports)}")
    if missing_blocks:
        failures.append(f"missing blocks: {', '.join(missing_blocks)}")
    if missing_refs:
        failures.append(f"missing references: {', '.join(missing_refs)}")
    if connect_count < int(spec["min_connects"]):
        failures.append(f"connect count {connect_count} < {spec['min_connects']}")
    if line_count != connect_count:
        failures.append(f"annotation(Line) count {line_count} != connect count {connect_count}")
    if placement_count <= len(inports) + len(outports):
        failures.append("diagram placements do not cover internal blocks")

    return {
        "file": path.as_posix(),
        "model": label,
        "ok": not failures,
        "inports": inports,
        "outports": outports,
        "connect_count": connect_count,
        "line_annotation_count": line_count,
        "placement_count": placement_count,
        "failures": failures,
    }


def check_model(path: Path, spec: dict[str, Any]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    parent_text = top_level_model_text(text)
    return check_text(parent_text if parent_text else text, path, spec, structure_text=text)


def check_package_models(path: Path, specs: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    results: list[dict[str, Any]] = []
    for model_name, spec in specs.items():
        model_text = named_model_text(text, model_name)
        if not model_text:
            results.append(
                {
                    "file": path.as_posix(),
                    "model": model_name,
                    "ok": False,
                    "inports": [],
                    "outports": [],
                    "connect_count": 0,
                    "line_annotation_count": 0,
                    "placement_count": 0,
                    "failures": ["model not found"],
                }
            )
            continue
        results.append(check_text(model_text, path, spec, model_name))
    if re.search(r"extends\s+AWFF_|redeclare|extends\s+MotorMixerBlock", text):
        results.append(
            {
                "file": path.as_posix(),
                "model": "package_safety",
                "ok": False,
                "inports": [],
                "outports": [],
                "connect_count": 0,
                "line_annotation_count": 0,
                "placement_count": 0,
                "failures": ["package contains fragile graphical inheritance/redeclare pattern"],
            }
        )
    return results


def behavior_contract_checks(base: Path) -> list[dict[str, Any]]:
    """Report whether graphical models expose key dynamic/nonlinear behavior.

    The structure checks above answer "can this model be opened and reviewed as
    a block diagram?". This contract answers the separate question the project
    actually needs before using a graphical model as a simulation counterpart:
    do the diagrams contain the expected saturation, delay/integrator, switch,
    dead-zone, and product behavior instead of only passing wires through?
    """

    results: list[dict[str, Any]] = []
    innovation_path = base / "AWFF_InnovationGraphicalControllers.mo"
    for label, required_tokens in BEHAVIOR_EXPECTATIONS.items():
        if label.endswith(".mo"):
            path = base / label
            model_text = path.read_text(encoding="utf-8") if path.exists() else ""
        else:
            path = innovation_path
            model_name = label.split(".")[-1]
            package_text = path.read_text(encoding="utf-8") if path.exists() else ""
            model_text = named_model_text(package_text, model_name)

        missing = [token for token in required_tokens if token not in model_text]
        results.append(
            {
                "file": path.as_posix(),
                "model": label,
                "ok": not missing,
                "required_behavior_blocks": required_tokens,
                "missing_behavior_blocks": missing,
                "failures": []
                if not missing
                else [
                    "missing graphical behavior blocks: "
                    + ", ".join(missing)
                ],
            }
        )
    return results


def run_checks() -> dict[str, Any]:
    base = ROOT / "Models" / "QuadrotorControllerBlocks"
    results = [check_model(base / filename, spec) for filename, spec in REQUIRED_MODELS.items()]
    for filename, specs in PACKAGE_MODELS.items():
        results.extend(check_package_models(base / filename, specs))
    behavior_results = behavior_contract_checks(base)
    structure_ok = all(item["ok"] for item in results)
    behavior_equivalence_ok = all(item["ok"] for item in behavior_results)
    return {
        "source": "static_model_contract",
        "scope": "graphical_awff_sysblock_controller",
        "ok": structure_ok,
        "structure_ok": structure_ok,
        "behavior_equivalence_ok": behavior_equivalence_ok,
        "Results": results,
        "behavior_results": behavior_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path, help="Optional JSON summary output path")
    args = parser.parse_args()

    summary = run_checks()
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
