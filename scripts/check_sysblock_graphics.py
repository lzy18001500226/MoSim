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


def find_port_names(text: str, port_kind: str) -> list[str]:
    pattern = re.compile(rf"SysplorerEmbeddedCoder\.Port\.{port_kind}\s+([A-Za-z_][A-Za-z0-9_]*)")
    return pattern.findall(text)


def check_model(path: Path, spec: dict[str, Any]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    inports = find_port_names(text, "Inport")
    outports = find_port_names(text, "Outport")
    connect_count = text.count("connect(")
    line_count = text.count("annotation(Line")
    placement_count = text.count("Placement(")

    missing_inports = [name for name in spec["inports"] if name not in inports]
    missing_outports = [name for name in spec["outports"] if name not in outports]
    missing_blocks = [
        name
        for name in spec.get("required_blocks", [])
        if not re.search(rf"\b{name}\b", text)
    ]
    missing_refs = [
        name
        for name in spec.get("required_references", [])
        if name not in text
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
        "ok": not failures,
        "inports": inports,
        "outports": outports,
        "connect_count": connect_count,
        "line_annotation_count": line_count,
        "placement_count": placement_count,
        "failures": failures,
    }


def run_checks() -> dict[str, Any]:
    base = ROOT / "models" / "QuadrotorControllerBlocks"
    results = [check_model(base / filename, spec) for filename, spec in REQUIRED_MODELS.items()]
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
