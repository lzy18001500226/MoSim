#!/usr/bin/env python3
"""Static acceptance checks for project graphical Sysblock controllers."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


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
                "roll_inc_limit",
                "pitch_error_sum",
                "pitch_kp_gain",
                "pitch_indi_gain_block",
                "pitch_inc_limit",
                "yaw_error_sum",
                "yaw_kp_gain",
                "yaw_indi_gain_block",
                "yaw_inc_limit",
            ],
            "min_connects": 36,
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
                "motor1_limit",
                "motor2_limit",
                "motor3_limit",
                "motor4_limit",
            ],
            "min_connects": 31,
        },
        "KnownRotorFaultMixerBlock": {
            "inports": ["thrust_ref", "roll_cmd", "pitch_cmd", "yaw_cmd"],
            "outports": ["y", "y1", "y2", "y3"],
            "required_blocks": ["raw_mixer", "rotor1_eta", "rotor1_allocator", "motor2_limit", "motor3_limit", "motor4_limit"],
            "min_connects": 13,
        },
        "RotorFaultIsolationBlock": {
            "inports": ["x_error", "y_error"],
            "outports": ["eta_hat1", "eta_hat2", "eta_hat3", "eta_hat4", "fault_index"],
            "required_blocks": ["signature_kernel", "FaultSignatureEstimatorKernelBlock"],
            "min_connects": 7,
        },
        "AdaptiveFaultMixerBlock": {
            "inports": ["thrust_ref", "roll_cmd", "pitch_cmd", "yaw_cmd", "eta_hat1", "eta_hat2", "eta_hat3", "eta_hat4"],
            "outports": ["y", "y1", "y2", "y3"],
            "required_blocks": ["raw_mixer", "eta1_allocator", "eta2_allocator", "eta3_allocator", "eta4_allocator"],
            "min_connects": 16,
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


def run_checks() -> dict[str, Any]:
    base = ROOT / "models" / "QuadrotorControllerBlocks"
    results = [check_model(base / filename, spec) for filename, spec in REQUIRED_MODELS.items()]
    for filename, specs in PACKAGE_MODELS.items():
        results.extend(check_package_models(base / filename, specs))
    return {
        "source": "static_model_contract",
        "scope": "graphical_awff_sysblock_controller",
        "ok": all(item["ok"] for item in results),
        "results": results,
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
